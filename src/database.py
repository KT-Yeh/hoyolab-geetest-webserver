from typing import TypeVar

import sqlalchemy
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.sql._typing import ColumnExpressionArgument

from .models import Base

DatabaseModel = Base
T_DatabaseModel = TypeVar("T_DatabaseModel", bound=Base)

_engine = create_async_engine("sqlite+aiosqlite:///data/bot.db")
_sessionmaker = async_sessionmaker(_engine, expire_on_commit=False)


class Database:
    engine = _engine
    sessionmaker = _sessionmaker

    @classmethod
    async def close(cls) -> None:
        """關閉資料庫，在關閉前需要呼叫一次"""
        await cls.engine.dispose()

    @classmethod
    async def insert_or_replace(cls, instance: DatabaseModel) -> None:
        """插入物件到資料庫，若已存在相同 Primary Key，則以新物件取代舊物件，
        Example: `Database.insert_or_replace(User(discord_id=123))`

        Paramaters:
        ------
        instance: `DatabaseModel`
            資料庫 Table (ORM) 的實例物件
        """
        async with cls.sessionmaker() as session:
            await session.merge(instance)
            await session.commit()

    @classmethod
    async def select_one(
        cls,
        table: type[T_DatabaseModel],
        whereclause: ColumnExpressionArgument[bool] | None = None,
    ) -> T_DatabaseModel | None:
        """指定資料庫 Table 與選擇條件，從資料庫選擇一項物件，
        Example: `Database.select_one(User, User.discord_id.is_(id))`

        Parameters
        ------
        table: `type[T_DatabaseModel]`
            要選擇的資料庫 Table (ORM) Class，Ex: `User`
        whereclause: `ColumnExpressionArgument[bool]` | `None`
            ORM Column 的 Where 選擇條件，Ex: `User.discord_id.is_(123456)`

        Returns
        ------
        `T_DatabaseModel` | `None`:
            根據參數所選擇出該 Table 符合條件的物件，若無任何符合則回傳 `None`
        """
        async with cls.sessionmaker() as session:
            stmt = sqlalchemy.select(table)
            if whereclause is not None:
                stmt = stmt.where(whereclause)
            result = await session.execute(stmt)
            return result.scalar()
