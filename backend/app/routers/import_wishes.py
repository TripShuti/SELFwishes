import asyncio

from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Account, Wish
from app.schemas import ImportRequest, ImportResult
from app.services.hoyo import fetch_all_wishes, parse_auth_url, HoyoAPIError
from app.services.parser import dedup_wishes, merge_and_sort_wishes, calc_pity, recalc_pity_batch, parse_into_db_rows
from app.config import GACHA_TYPES, GACHA_TYPE_ORDER
from app.services.hoyo_session import connected_roles, create_authkey, connect

router = APIRouter(prefix="/api/import", tags=["import"])
import_lock = asyncio.Lock()


class HoyoImportRequest(BaseModel):
    uid: str = Field(pattern=r"^[0-9]{8,12}$")


@router.get("/hoyoverse")
async def hoyoverse_connections():
    try:
        return {"roles": connected_roles()}
    except HoyoAPIError as exc:
        raise HTTPException(400, str(exc)) from None


@router.post("/hoyoverse/connect")
async def connect_browser(request: Request):
    # Account secrets are accepted only through an explicitly approved extension.
    # Parse manually: validation responses must never echo cookie input values.
    from urllib.parse import urlparse
    import json
    origin = request.headers.get("origin")
    if origin and urlparse(origin).scheme not in ("chrome-extension", "moz-extension"):
        raise HTTPException(403, "Connect using the SELFwishes browser extension.")
    if request.headers.get("x-selfwishes-bridge") != "1":
        raise HTTPException(403, "Connect using the SELFwishes browser extension.")
    raw = bytearray()
    async for chunk in request.stream():
        raw.extend(chunk)
        if len(raw) > 65536:
            raise HTTPException(413, "Connection request is too large.")
    try:
        body = json.loads(raw)
        cookies = body["cookies"]
        expected_uid = body.get("expected_uid")
        if not isinstance(cookies, dict):
            raise ValueError()
        if expected_uid is not None and (not isinstance(expected_uid, str) or
                                        not expected_uid.isascii() or not expected_uid.isdigit() or
                                        not 8 <= len(expected_uid) <= 12):
            raise ValueError()
    except (ValueError, KeyError, TypeError):
        raise HTTPException(400, "Invalid browser connection request.") from None
    if import_lock.locked():
        raise HTTPException(409, "An import is already running. Please wait.")
    async with import_lock:
        try:
            return {"roles": await connect(cookies, expected_uid=expected_uid)}
        except HoyoAPIError as exc:
            raise HTTPException(400, str(exc)) from None


@router.post("/hoyoverse", response_model=ImportResult)
async def import_hoyoverse(body: HoyoImportRequest, db: AsyncSession = Depends(get_db)):
    if import_lock.locked():
        raise HTTPException(409, "An import is already running. Please wait.")
    async with import_lock:
        try:
            parsed = await create_authkey(body.uid)
            return await _import_parsed(parsed, db, expected_uid=body.uid, incremental=True)
        except HoyoAPIError as exc:
            raise HTTPException(400, str(exc)) from None


async def _recalc_account(db: AsyncSession, account_id: int):
    for uigf_type in GACHA_TYPE_ORDER:
        stmt = (
            select(Wish)
            .where(Wish.account_id == account_id, Wish.uigf_gacha_type == uigf_type)
            .order_by(Wish.timestamp.asc(), Wish.wish_id.asc())
        )
        result = await db.execute(stmt)
        wishes = result.scalars().all()
        if not wishes:
            continue

        dicts = []
        for w in wishes:
            dicts.append({
                "id": w.wish_id,
                "name": w.item_name,
                "rank_type": str(w.rarity),
                "time": w.timestamp,
            })

        recalc_pity_batch(dicts, uigf_type)

        for position, (w, d) in enumerate(zip(wishes, dicts), start=1):
            w.pull_count = position
            w.pity_5 = d["pity_5"]
            w.pity_4 = d["pity_4"]
            w.is_5050_win = d["is_5050_win"]
            w.is_guaranteed = d["is_guaranteed"]

    await db.commit()


@router.post("", response_model=ImportResult)
async def import_wishes(body: ImportRequest, db: AsyncSession = Depends(get_db)):
    if import_lock.locked():
        raise HTTPException(409, "An import is already running. Please wait.")
    async with import_lock:
        try:
            parsed = parse_auth_url(body.url)
            return await _import_parsed(parsed, db, account_name=body.account_name)
        except HoyoAPIError as exc:
            raise HTTPException(400, str(exc)) from None


async def _import_parsed(parsed: dict, db: AsyncSession, *, expected_uid=None,
                         incremental=False, account_name=None):
    authkey = parsed["authkey"]
    region = parsed.get("region")
    base_url = parsed.get("base_url")
    game_biz = parsed.get("game_biz")

    known_ids = set()
    existing_account = None
    if expected_uid:
        existing_account = (await db.execute(
            select(Account).where(Account.uid == expected_uid)
        )).scalar_one_or_none()
        if incremental and existing_account:
            known_ids = set((await db.execute(
                select(Wish.wish_id).where(Wish.account_id == existing_account.id)
            )).scalars().all())

    raw_wishes: dict[str, list[dict]] = {}
    total_wishes_fetched = 0
    # 301 returns both character event banners. Querying 400 separately duplicates them.
    for gacha_type in GACHA_TYPES:
        if gacha_type == "400":
            continue
        wishes = await fetch_all_wishes(
            authkey, gacha_type, region, lang="en", base_url=base_url, game_biz=game_biz,
            existing_ids=known_ids if incremental else None,
        )
        for wish in wishes:
            if expected_uid and str(wish.get("uid")) != expected_uid:
                raise HoyoAPIError("Wish history UID does not match the connected account.")
        if wishes:
            raw_wishes[gacha_type] = wishes
            total_wishes_fetched += len(wishes)

    if not raw_wishes:
        if existing_account:
            return ImportResult(account_id=existing_account.id, account_name=existing_account.name,
                                uid=expected_uid, total_wishes=0, new_wishes=0, banners=[])
        raise HoyoAPIError("No wishes found in the available history.")

    merged = merge_and_sort_wishes(raw_wishes)

    sample = list(raw_wishes.values())[0][0]
    uid = sample["uid"]
    detected_region = sample.get("region") or region or "unknown"

    existing_account = (
        await db.execute(select(Account).where(Account.uid == uid))
    ).scalar_one_or_none()

    if existing_account:
        account = existing_account
        if account_name:
            account.name = account_name
    else:
        account = Account(name=account_name or f"Account ({uid})", uid=uid, region=detected_region)
        db.add(account)

    await db.flush()

    existing_result = await db.execute(select(Wish.wish_id))
    existing_ids = {row[0] for row in existing_result.fetchall()}

    total_new = 0
    all_db_rows = []

    for uigf_type in GACHA_TYPE_ORDER:
        if uigf_type not in merged:
            continue
        wishes = merged[uigf_type]
        if not wishes:
            continue

        processed = calc_pity(wishes, uigf_type)
        deduped, new_count = dedup_wishes(existing_ids, processed)
        total_new += new_count
        existing_ids.update(str(w["id"]) for w in deduped)

        rows = parse_into_db_rows(account.id, uigf_type, deduped)
        all_db_rows.extend(rows)

    if all_db_rows:
        db.add_all([Wish(**row) for row in all_db_rows])

    await db.flush()
    await _recalc_account(db, account.id)

    await db.refresh(account)

    banner_list = []
    for gt in GACHA_TYPE_ORDER:
        if gt in merged:
            banner_list.append({
                "gacha_type": gt,
                "name": GACHA_TYPES.get(gt, gt),
                "count": len(merged[gt]),
                "new_count": sum(row["uigf_gacha_type"] == gt for row in all_db_rows),
            })

    return ImportResult(
        account_id=account.id,
        account_name=account.name,
        uid=uid,
        total_wishes=total_wishes_fetched,
        new_wishes=total_new,
        banners=banner_list,
    )
