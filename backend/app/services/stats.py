from collections import defaultdict

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Wish, Account
from app.config import PITY_HARD_5, PITY_HARD_4, STANDARD_5_CHARS, GACHA_TYPES, GACHA_TYPE_ORDER
from app.schemas import (
    BannerSummary,
    PityInfo,
    DetailedStats,
    TimelinePoint,
)


async def get_banner_summaries(
    session: AsyncSession, account_id: int
) -> list[BannerSummary]:
    summaries = []
    for gt in GACHA_TYPE_ORDER:
        if gt not in GACHA_TYPES:
            continue

        result = await get_banner_summary(session, account_id, gt)
        if result and result.total_pulls > 0:
            summaries.append(result)

    return summaries


async def get_banner_summary(
    session: AsyncSession, account_id: int, uigf_type: str
) -> BannerSummary | None:
    stmt = (
        select(Wish)
        .where(Wish.account_id == account_id, Wish.uigf_gacha_type == uigf_type)
        .order_by(Wish.timestamp.asc(), Wish.wish_id.asc())
    )
    result = await session.execute(stmt)
    wishes = result.scalars().all()

    if not wishes:
        return None

    total = len(wishes)
    count_5 = sum(1 for w in wishes if w.rarity == 5)
    count_4 = sum(1 for w in wishes if w.rarity == 4)

    pity_5 = 0
    for w in reversed(wishes):
        if w.rarity == 5:
            break
        pity_5 += 1

    pity_4 = 0
    for w in reversed(wishes):
        if w.rarity in (4, 5):
            break
        pity_4 += 1

    name = GACHA_TYPES.get(uigf_type, uigf_type)

    return BannerSummary(
        gacha_type=uigf_type,
        name=name,
        total_pulls=total,
        pity_5=pity_5,
        pity_4=pity_4,
        count_5=count_5,
        count_4=count_4,
    )


async def get_detailed_stats(
    session: AsyncSession, account_id: int, uigf_type: str | None = None
) -> DetailedStats:
    stmt = select(Wish).where(Wish.account_id == account_id)

    if uigf_type:
        stmt = stmt.where(Wish.uigf_gacha_type == uigf_type)

    result = await session.execute(stmt)
    all_wishes = result.scalars().all()

    total = len(all_wishes)

    five_stars = [w for w in all_wishes if w.rarity == 5]
    four_stars = [w for w in all_wishes if w.rarity == 4]

    avg_pity_5 = None
    avg_pity_4 = None
    if five_stars:
        avg_pity_5 = sum(w.pity_5 or 0 for w in five_stars) / len(five_stars)
    if four_stars:
        avg_pity_4 = sum(w.pity_4 or 0 for w in four_stars) / len(four_stars)

    wins = sum(1 for w in five_stars if w.is_5050_win is True)
    losses = sum(1 for w in five_stars if w.is_5050_win is False)
    total_5050 = wins + losses

    pity_cap_5 = PITY_HARD_5.get(uigf_type or "301", 90)
    pity_cap_4 = PITY_HARD_4.get(uigf_type or "301", 10)

    pulls_by_month = await _get_pulls_by_month(session, account_id, uigf_type)

    return DetailedStats(
        avg_pity_5=avg_pity_5,
        avg_pity_4=avg_pity_4,
        luckiness_5=(
            avg_pity_5 / pity_cap_5
            if avg_pity_5
            else None
        ),
        luckiness_4=(
            avg_pity_4 / pity_cap_4
            if avg_pity_4
            else None
        ),
        total_pulls=total,
        wins_5050=wins,
        losses_5050=losses,
        total_5050=total_5050,
        known_5050=total_5050 > 0,
        pulls_by_month=pulls_by_month,
    )


async def _get_pulls_by_month(
    session: AsyncSession, account_id: int, uigf_type: str | None = None
) -> list[dict]:
    from sqlalchemy import text

    query = """
        SELECT
            strftime('%Y-%m', timestamp) as month,
            COUNT(*) as pulls,
            SUM(CASE WHEN rarity = 5 THEN 1 ELSE 0 END) as count_5,
            SUM(CASE WHEN rarity = 4 THEN 1 ELSE 0 END) as count_4
        FROM wishes
        WHERE account_id = :aid
    """
    params = {"aid": account_id}

    if uigf_type:
        query += " AND uigf_gacha_type = :gt"
        params["gt"] = uigf_type

    query += " GROUP BY month ORDER BY month ASC"

    result = await session.execute(text(query), params)
    rows = result.fetchall()
    return [
        {
            "month": r[0],
            "pulls": r[1],
            "count_5": r[2],
            "count_4": r[3],
        }
        for r in rows
    ]


async def compare_accounts(
    session: AsyncSession, account_ids: list[int]
) -> list[dict]:
    result = []
    for aid in account_ids:
        stmt = select(Account).where(Account.id == aid)
        acct = (await session.execute(stmt)).scalar_one_or_none()
        if not acct:
            continue

        summaries = await get_banner_summaries(session, aid)
        stats = await get_detailed_stats(session, aid)
        result.append({
            "account": {
                "id": acct.id,
                "name": acct.name,
                "uid": acct.uid,
                "region": acct.region,
            },
            "banners": [s.model_dump() for s in summaries],
            "stats": {
                "total_pulls": stats.total_pulls,
                "wins_5050": stats.wins_5050,
                "losses_5050": stats.losses_5050,
                "total_5050": stats.total_5050,
                "known_5050": stats.known_5050,
                "avg_pity_5": stats.avg_pity_5,
                "avg_pity_4": stats.avg_pity_4,
            },
        })

    return result
