import sqlalchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column


class Base(MappedAsDataclass, DeclarativeBase):
    """資料庫 Table 基礎類別，繼承自 sqlalchemy `MappedAsDataclass`, `DeclarativeBase`"""

    type_annotation_map = {dict[str, str]: sqlalchemy.JSON}


class User(Base):
    """使用者資料庫 Table"""

    __tablename__ = "users"

    discord_id: Mapped[int] = mapped_column(primary_key=True)
    """使用者 Discord ID"""


class GeetestChallenge(Base):
    """用在簽到圖形驗證 Geetest 的 Challenge 值"""

    __tablename__ = "geetest_challenge"

    discord_id: Mapped[int] = mapped_column(primary_key=True)
    """使用者 Discord ID"""

    genshin: Mapped[dict[str, str] | None] = mapped_column(default=None)
    """原神 challenge 值"""
    honkai3rd: Mapped[dict[str, str] | None] = mapped_column(default=None)
    """崩壞3 challenge 值"""
    starrail: Mapped[dict[str, str] | None] = mapped_column(default=None)
