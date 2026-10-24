"""Server-side HoYoverse session; secrets never leave this module via the API."""
import json
import os
import tempfile
from pathlib import Path
from urllib.parse import unquote

import httpx

from app.config import DATA_DIR
from app.services.hoyo import HoyoAPIError

SESSION_PATH = Path(DATA_DIR) / ".hoyo-sessions.json"
COOKIE_NAMES = ("account_id_v2", "account_mid_v2", "cookie_token_v2")
ACCOUNT_API = "https://api-account-os.hoyoverse.com"


def load_sessions() -> dict:
    try:
        return json.loads(SESSION_PATH.read_text())
    except FileNotFoundError:
        return {}
    except (OSError, ValueError):
        raise HoyoAPIError("Cannot read HoYoverse connection. Sign in to HoYoverse and reconnect from your browser.") from None


def save_sessions(sessions: dict) -> None:
    SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd, path = tempfile.mkstemp(prefix=".hoyo-session-", dir=SESSION_PATH.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(sessions, stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(path, SESSION_PATH)
    finally:
        if os.path.exists(path):
            os.unlink(path)


async def account_request(path: str, cookies: dict, *, payload=None) -> dict:
    try:
        async with httpx.AsyncClient(cookies=cookies, timeout=30, follow_redirects=False) as client:
            if payload is None:
                response = await client.get(ACCOUNT_API + path, params={"game_biz": "hk4e_global"})
            else:
                response = await client.post(ACCOUNT_API + path, json=payload)
        response.raise_for_status()
        result = response.json()
    except (httpx.HTTPError, ValueError):
        raise HoyoAPIError("Cannot reach HoYoverse. Try again later.") from None
    if result.get("retcode") != 0:
        code = result.get("retcode")
        raise HoyoAPIError(f"HoYoverse authorization failed (code {code}). Sign in to HoYoverse and reconnect from your browser.")
    data = result.get("data")
    if not isinstance(data, dict):
        raise HoyoAPIError("Invalid HoYoverse response. Try again later.")
    return data


async def connect(cookies: dict, expected_uid: str | None = None) -> list[dict]:
    cookies = {name: cookies.get(name, "") for name in COOKIE_NAMES}
    if not all(isinstance(value, str) and value and len(value) < 16384 for value in cookies.values()):
        raise HoyoAPIError("The three required HoYoverse cookies are missing or invalid.")
    data = await account_request("/account/binding/api/getUserGameRolesOfRegionByCookieToken", cookies)
    roles = [{"uid": str(role["game_uid"]), "region": role["region"],
              "nickname": role.get("nickname", "")} for role in data.get("list", [])]
    if not roles:
        raise HoyoAPIError("No Genshin characters found for this HoYoverse account.")
    if expected_uid and not any(role["uid"] == expected_uid for role in roles):
        signed_in = ", ".join(role["uid"] for role in roles)
        raise HoyoAPIError(f"Your browser is signed in for UID {signed_in}, not {expected_uid}. "
                           "Switch HoYoverse accounts or select the matching character in SELFwishes.")
    sessions = load_sessions()
    # Reconnecting an account also removes roles no longer returned by HoYoverse.
    sessions = {uid: session for uid, session in sessions.items()
                if session["cookies"].get("account_id_v2") != cookies["account_id_v2"]}
    for role in roles:
        sessions[role["uid"]] = {**role, "cookies": cookies}
    save_sessions(sessions)
    return roles


def connected_roles() -> list[dict]:
    return [{key: value[key] for key in ("uid", "region", "nickname")}
            for value in load_sessions().values()]


async def create_authkey(uid: str) -> dict:
    session = load_sessions().get(uid)
    if not session:
        raise HoyoAPIError("This UID is not connected. Connect it from your browser first.")
    data = await account_request("/binding/api/genAuthKeyByCookieToken", session["cookies"], payload={
        "game_uid": uid, "region": session["region"], "game_biz": "hk4e_global",
        "auth_appid": "webview_gacha",
    })
    if not data.get("authkey"):
        raise HoyoAPIError("HoYoverse did not return a wish history key. Reconnect the account.")
    return {"authkey": unquote(data["authkey"]), "region": session["region"],
            "game_biz": "hk4e_global", "lang": "en"}
