from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship

from app.database import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    uid = Column(String(16), nullable=True)
    region = Column(String(16), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    wishes = relationship("Wish", back_populates="account", cascade="all, delete-orphan")


class Wish(Base):
    __tablename__ = "wishes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    gacha_type = Column(String(4), nullable=False)
    uigf_gacha_type = Column(String(4), nullable=False)
    item_id = Column(String(32), default="")
    item_name = Column(String(64), nullable=False)
    item_type = Column(String(16), nullable=False)
    rarity = Column(Integer, nullable=False)
    timestamp = Column(String(32), nullable=False)
    wish_id = Column(String(32), nullable=False, unique=True)
    pull_count = Column(Integer, nullable=False, default=0)
    pity_5 = Column(Integer, nullable=True)
    pity_4 = Column(Integer, nullable=True)
    is_5050_win = Column(Boolean, nullable=True)
    is_guaranteed = Column(Boolean, nullable=True)

    account = relationship("Account", back_populates="wishes")
