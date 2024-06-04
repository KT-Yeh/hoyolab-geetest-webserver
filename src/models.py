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
    cookie_default: Mapped[str | None] = mapped_column(default=None)
    """當特定遊戲的 cookie 未設定時，則使用此欄位的 cookie"""
    cookie_genshin: Mapped[str | None] = mapped_column(default=None)
    """用來給原神指令使用的 Hoyolab 或米游社網頁的 Cookie"""
    cookie_honkai3rd: Mapped[str | None] = mapped_column(default=None)
    """用來給崩壞3指令使用的 Hoyolab 或米游社網頁的 Cookie"""
    cookie_starrail: Mapped[str | None] = mapped_column(default=None)
    """用來給星穹鐵道指令使用的 Hoyolab 或米游社網頁的 Cookie"""
    cookie_themis: Mapped[str | None] = mapped_column(default=None)
    """用來給未定事件簿指令使用的 Hoyolab 或米游社網頁的 Cookie"""


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
