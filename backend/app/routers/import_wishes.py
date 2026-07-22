from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Account, Wish
from app.schemas import ImportRequest, ImportResult
from app.services.hoyo import fetch_all_wishes, parse_auth_url, HoyoAPIError
from app.services.parser import dedup_wishes, merge_and_sort_wishes, calc_pity, recalc_pity_batch, parse_into_db_rows
from app.config import GACHA_TYPES, GACHA_TYPE_ORDER

router = APIRouter(prefix="/api/import", tags=["import"])


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

        for w, d in zip(wishes, dicts):
            w.pity_5 = d["pity_5"]
            w.pity_4 = d["pity_4"]
            w.is_5050_win = d["is_5050_win"]
            w.is_guaranteed = d["is_guaranteed"]

    await db.commit()


@router.post("", response_model=ImportResult)
async def import_wishes(body: ImportRequest, db: AsyncSession = Depends(get_db)):
    try:
        parsed = parse_auth_url(body.url)
    except HoyoAPIError as e:
        raise HTTPException(400, str(e))

    authkey = parsed["authkey"]
    region = parsed.get("region")
    base_url = parsed.get("base_url")
    game_biz = parsed.get("game_biz")

    raw_wishes: dict[str, list[dict]] = {}
    total_wishes_fetched = 0

    for gacha_type in GACHA_TYPES:
        try:
            wishes = await fetch_all_wishes(authkey, gacha_type, region, base_url=base_url, game_biz=game_biz)
            if wishes:
                raw_wishes[gacha_type] = wishes
                total_wishes_fetched += len(wishes)
        except HoyoAPIError:
            continue

    if not raw_wishes:
        raise HTTPException(400, "No wishes found. Authkey may be expired or invalid.")

    merged = merge_and_sort_wishes(raw_wishes)

    sample = list(raw_wishes.values())[0][0]
    uid = sample["uid"]
    detected_region = sample.get("region") or region or "unknown"

    account_name = body.account_name or f"Account ({uid})"

    existing_account = (
        await db.execute(select(Account).where(Account.uid == uid))
    ).scalar_one_or_none()

    if existing_account:
        account = existing_account
        account.name = account_name
    else:
        account = Account(name=account_name, uid=uid, region=detected_region)
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

        rows = parse_into_db_rows(account.id, uigf_type, deduped)
        all_db_rows.extend(rows)

    if all_db_rows:
        db.add_all([Wish(**row) for row in all_db_rows])

    await db.commit()

    await _recalc_account(db, account.id)

    if not all_db_rows:
        raise HTTPException(400, "No new wishes to import")

    await db.refresh(account)

    banner_list = []
    for gt in GACHA_TYPE_ORDER:
        if gt in merged:
            banner_list.append({
                "gacha_type": gt,
                "name": GACHA_TYPES.get(gt, gt),
                "count": len(merged[gt]),
            })

    return ImportResult(
        account_id=account.id,
        account_name=account.name,
        uid=uid,
        total_wishes=total_wishes_fetched,
        new_wishes=total_new,
        banners=banner_list,
    )
