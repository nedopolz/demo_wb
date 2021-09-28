from sqlalchemy import (BigInteger, Column, String, ForeignKey, select, Boolean, update)

from reports_parser.db.database import Base


class ReportAccount(Base):
    __tablename__ = 'report_accounts'

    id = Column(BigInteger(), primary_key=True)
    newID = Column(String(1000))
    oldID = Column(String(100))
    parsed_report = Column(Boolean, default=False)
    parsed_remains = Column(Boolean, default=False)
    phone = Column(ForeignKey('report_phone_accounts.id', ondelete='CASCADE'))

    __mapper_args__ = {"eager_defaults": True}

    @classmethod
    async def get_supply_accounts(cls, phone_account_id: int, session):
        stmt = select(ReportAccount).where(cls.phone == phone_account_id)
        result = (await session.execute(stmt)).scalars().all()
        return result

    @classmethod
    async def get_all(cls,  session):
        stmt = select(ReportAccount)
        result = (await session.execute(stmt)).scalars().all()
        return result

    @classmethod
    async def check_for_parsing_need(cls, session):
        ans = 0
        stmt = select(ReportAccount).where(cls.parsed_report == False)
        result = (await session.execute(stmt)).scalars().all()
        ans += len(result)
        stmt = select(ReportAccount).where(cls.parsed_remains == False)
        result = (await session.execute(stmt)).scalars().all()
        ans += len(result)
        if ans != 0:
            return True
        else:
            return False

    @classmethod
    async def update_report_status(cls, session, account_id: int, status: bool):
        stmt = update(cls).where(cls.id == account_id).values(
            parsed_report=status)
        await session.execute(stmt)

    @classmethod
    async def update_remains_status(cls, session, account_id: int, status: bool):
        stmt = update(cls).where(cls.id == account_id).values(
            parsed_remains=status)
        await session.execute(stmt)

    @classmethod
    async def get_name(cls, session, newID: str):
        stmt = select(ReportAccount).where(cls.newID == newID)
        result = (await session.execute(stmt)).scalars().all()
        return result

