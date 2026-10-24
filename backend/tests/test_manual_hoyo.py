import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx

_data = tempfile.TemporaryDirectory()
os.environ["DATA_DIR"] = _data.name

from app.database import Base, engine, async_session
from app.models import Account, Wish
from app.main import app
from app.routers import import_wishes as imports
from app.services import hoyo, hoyo_session
from sqlalchemy import select, func


def wish(wid="2", uid="716004704"):
    return {"id": wid, "uid": uid, "name": "Candace", "rank_type": "4",
            "time": "2026-10-21 16:38:12", "gacha_type": "301", "item_type": "Character"}


class ManualHoyoTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    async def asyncTearDown(self):
        await engine.dispose()

    async def test_url_cannot_choose_destination(self):
        parsed = hoyo.parse_auth_url("http://127.0.0.1/private?authkey=test&region=os_euro")
        self.assertEqual(parsed["base_url"], hoyo.HOYO_BASE_URL)
        cn = hoyo.parse_auth_url("https://webstatic.mihoyo.com/page?authkey=test")
        self.assertIn("public-operation-hk4e.mihoyo.com", cn["base_url"])

    async def test_pagination_stops_at_existing_id(self):
        result = {"region": "os_euro", "list": [wish("3"), wish("2"), wish("1")]}
        with patch.object(hoyo, "fetch_gacha_page", new=AsyncMock(return_value=result)) as fetch:
            rows = await hoyo.fetch_all_wishes("secret", "301", existing_ids={"2"})
        self.assertEqual([row["id"] for row in rows], ["3"])
        self.assertEqual(fetch.await_count, 1)

    async def test_repeated_import_preserves_name_and_has_no_duplicates(self):
        async def fetch(key, banner, *args, **kwargs):
            return [wish(), wish()] if banner == "301" else []
        async with async_session() as db:
            db.add(Account(name="TripShuti", uid="716004704", region="os_euro"))
            await db.commit()
            with patch.object(imports, "fetch_all_wishes", side_effect=fetch):
                first = await imports._import_parsed({"authkey": "secret"}, db,
                                                    expected_uid="716004704", incremental=True)
                second = await imports._import_parsed({"authkey": "secret"}, db,
                                                     expected_uid="716004704", incremental=True)
            self.assertEqual(first.new_wishes, 1)
            self.assertEqual(first.banners[0]["new_count"], 1)
            self.assertEqual(second.banners[0]["new_count"], 0)
            self.assertEqual(second.new_wishes, 0)
            self.assertEqual(second.account_name, "TripShuti")
            self.assertEqual(await db.scalar(select(func.count()).select_from(Wish)), 1)

    async def test_incremental_import_recalculates_lifetime_pity_and_sequence(self):
        async with async_session() as db:
            with patch.object(imports, "fetch_all_wishes", new=AsyncMock(side_effect=[
                [], [], [wish("1")], [], []
            ])):
                await imports._import_parsed({"authkey": "secret"}, db, expected_uid="716004704")
            with patch.object(imports, "fetch_all_wishes", new=AsyncMock(side_effect=[
                [], [], [wish("2")], [], []
            ])):
                await imports._import_parsed({"authkey": "secret"}, db, expected_uid="716004704", incremental=True)
            rows = (await db.execute(select(Wish).order_by(Wish.wish_id))).scalars().all()
            self.assertEqual([row.pull_count for row in rows], [1, 2])
            self.assertEqual([row.pity_5 for row in rows], [1, 2])

    async def test_no_partial_save_when_banner_fails(self):
        async def fetch(key, banner, *args, **kwargs):
            if banner == "302":
                raise hoyo.HoyoAPIError("API unavailable")
            return [wish()] if banner == "301" else []
        async with async_session() as db:
            with patch.object(imports, "fetch_all_wishes", side_effect=fetch):
                with self.assertRaises(hoyo.HoyoAPIError):
                    await imports._import_parsed({"authkey": "secret"}, db)
            self.assertEqual(await db.scalar(select(func.count()).select_from(Wish)), 0)
            self.assertEqual(await db.scalar(select(func.count()).select_from(Account)), 0)

    async def test_wrong_uid_is_rejected(self):
        with patch.object(imports, "fetch_all_wishes", new=AsyncMock(return_value=[wish(uid="738064929")])):
            async with async_session() as db:
                with self.assertRaises(hoyo.HoyoAPIError):
                    await imports._import_parsed({"authkey": "secret"}, db, expected_uid="716004704")

    async def test_session_permissions_and_public_response(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sessions.json"
            cookies = {key: "secret-value" for key in hoyo_session.COOKIE_NAMES}
            with patch.object(hoyo_session, "SESSION_PATH", path), patch.object(
                hoyo_session, "account_request", new=AsyncMock(return_value={"list": [
                    {"game_uid": "716004704", "region": "os_euro", "nickname": "Trip"}
                ]})
            ):
                await hoyo_session.connect(cookies)
                public = hoyo_session.connected_roles()
                self.assertEqual(path.stat().st_mode & 0o777, 0o600)
                self.assertNotIn("secret-value", str(public))
                self.assertNotIn("cookies", str(public))

    async def test_browser_connection_rejects_foreign_origin(self):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://selfwishes") as client:
            response = await client.post("/api/import/hoyoverse/connect", json={"cookies": {}},
                                         headers={"Origin": "https://untrusted.example", "X-SELFwishes-Bridge": "1"})
        self.assertEqual(response.status_code, 403)

    async def test_browser_connection_validation_does_not_echo_secrets(self):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://selfwishes") as client:
            response = await client.post("/api/import/hoyoverse/connect", json={"cookies": "secret-value"},
                                         headers={"Origin": "moz-extension://test", "X-SELFwishes-Bridge": "1"})
        self.assertEqual(response.status_code, 400)
        self.assertNotIn("secret-value", response.text)

    async def test_browser_connection_checks_uid_before_saving(self):
        cookies = {key: "secret-value" for key in hoyo_session.COOKIE_NAMES}
        with patch.object(hoyo_session, "account_request", new=AsyncMock(return_value={"list": [
            {"game_uid": "716004704", "region": "os_euro", "nickname": "Trip"}
        ]})), patch.object(hoyo_session, "save_sessions") as save:
            with self.assertRaises(hoyo.HoyoAPIError):
                await hoyo_session.connect(cookies, expected_uid="738064929")
            save.assert_not_called()

    async def test_browser_connection_returns_only_metadata(self):
        role = {"uid": "716004704", "region": "os_euro", "nickname": "Trip"}
        with patch.object(imports, "connect", new=AsyncMock(return_value=[role])) as connect:
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://selfwishes") as client:
                response = await client.post("/api/import/hoyoverse/connect", json={
                    "cookies": {key: "secret-value" for key in hoyo_session.COOKIE_NAMES},
                    "expected_uid": "716004704"},
                    headers={"Origin": "chrome-extension://test", "X-SELFwishes-Bridge": "1"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"roles": [role]})
            self.assertNotIn("secret-value", response.text)
            self.assertEqual(connect.await_args.kwargs["expected_uid"], "716004704")

    async def test_upstream_errors_do_not_expose_secrets(self):
        request = httpx.Request("GET", "https://example.com/?authkey=secret-value")
        with patch.object(httpx.AsyncClient, "get", side_effect=httpx.ConnectError(
            "secret-value", request=request
        )):
            with self.assertRaises(hoyo.HoyoAPIError) as error:
                await hoyo.fetch_gacha_page(httpx.AsyncClient(), "secret-value", "301", 1)
        self.assertNotIn("secret-value", str(error.exception))


if __name__ == "__main__":
    unittest.main()
