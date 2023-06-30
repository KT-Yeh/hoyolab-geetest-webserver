from enum import Enum

from pydantic import BaseModel


class Game(str, Enum):
    GENSHIN = "genshin"
    """Genshin Impact"""
    HONKAI = "honkai3rd"
    """Honkai Impact 3rd"""
    STARRAIL = "hkrpg"
    """Honkai Star Rail"""


class GeetestResult(BaseModel):
    geetest_challenge: str
    geetest_validate: str
    geetest_seccode: str
