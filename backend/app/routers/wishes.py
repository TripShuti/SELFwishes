import math

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Wish, Account
from app.schemas import WishOut, WishPage, DetailedStats
from app.services.stats import get_detailed_stats, compare_accounts

router = APIRouter(prefix="/api", tags=["wishes"])


@router.get("/wishes", response_model=WishPage)
async def list_wishes(
    account_id: int = Query(..., description="Account ID"),
    gacha_type: str | None = Query(None, description="Filter by uigf_gacha_type"),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    sort_by: str = Query("timestamp", pattern="^(timestamp|rarity|item_name|item_type|pity_5|pity_4|uigf_gacha_type)$"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
):
    account = await db.get(Account, account_id)
    if not account:
        raise HTTPException(404, "Account not found")

    stmt = select(Wish).where(Wish.account_id == account_id)

    if gacha_type:
        stmt = stmt.where(Wish.uigf_gacha_type == gacha_type)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    sort_col = getattr(Wish, sort_by, Wish.timestamp)
    direction = sort_col.asc if sort_dir == "asc" else sort_col.desc
    stmt = stmt.order_by(
        direction(),
        Wish.timestamp.asc() if sort_dir == "asc" else Wish.timestamp.desc(),
        Wish.wish_id.asc() if sort_dir == "asc" else Wish.wish_id.desc(),
    )

    offset = (page - 1) * size
    stmt = stmt.offset(offset).limit(size)

    result = await db.execute(stmt)
    items = result.scalars().all()

    return WishPage(
        items=[WishOut.model_validate(w) for w in items],
        total=total,
        page=page,
        size=size,
    )


@router.get("/accounts/{account_id}/stats", response_model=DetailedStats)
async def account_stats(
    account_id: int,
    gacha_type: str | None = Query(None, description="Filter by uigf_gacha_type"),
    db: AsyncSession = Depends(get_db),
):
    account = await db.get(Account, account_id)
    if not account:
        raise HTTPException(404, "Account not found")
    return await get_detailed_stats(db, account_id, gacha_type)


@router.post("/compare", response_model=list[dict])
async def compare(account_ids: list[int], db: AsyncSession = Depends(get_db)):
    return await compare_accounts(db, account_ids)
