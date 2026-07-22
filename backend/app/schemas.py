from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AccountCreate(BaseModel):
    name: str
    uid: Optional[str] = None
    region: Optional[str] = None


class AccountOut(BaseModel):
    id: int
    name: str
    uid: Optional[str] = None
    region: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ImportRequest(BaseModel):
    url: str
    account_name: Optional[str] = None


class ImportProgress(BaseModel):
    status: str
    message: str
    progress: int


class ImportResult(BaseModel):
    account_id: int
    account_name: str
    uid: str
    total_wishes: int
    new_wishes: int
    banners: list[dict]


class PityInfo(BaseModel):
    pity_5: int
    pity_4: int
    max_pity_5: int
    max_pity_4: int
    total_pulls: int


class BannerSummary(BaseModel):
    gacha_type: str
    name: str
    total_pulls: int
    pity_5: int
    pity_4: int
    count_5: int
    count_4: int


class AccountSummary(BaseModel):
    account: AccountOut
    banners: list[BannerSummary]


class DetailedStats(BaseModel):
    avg_pity_5: Optional[float] = None
    avg_pity_4: Optional[float] = None
    luckiness_5: Optional[float] = None
    luckiness_4: Optional[float] = None
    total_pulls: int
    wins_5050: int = 0
    losses_5050: int = 0
    total_5050: int = 0
    known_5050: bool = False
    pulls_by_month: Optional[list[dict]] = None


class WishOut(BaseModel):
    id: int
    gacha_type: str
    uigf_gacha_type: str
    item_name: str
    item_type: str
    rarity: int
    timestamp: str
    pity_5: Optional[int] = None
    pity_4: Optional[int] = None
    is_5050_win: Optional[bool] = None
    is_guaranteed: Optional[bool] = None
    pull_count: int

    model_config = {"from_attributes": True}


class WishPage(BaseModel):
    items: list[WishOut]
    total: int
    page: int
    size: int


class AccountCompare(BaseModel):
    accounts: list[AccountSummary]


class TimelinePoint(BaseModel):
    month: str
    pulls: int
    count_5: int
    count_4: int


class CompareData(BaseModel):
    labels: list[str]
    datasets: list[dict]
