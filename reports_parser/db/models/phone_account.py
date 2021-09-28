from sqlalchemy import (BigInteger, Column, String, select, Boolean, update)

from reports_parser.db.database import Base


class ReportPhoneAccount(Base):
    __tablename__ = 'report_phone_accounts'

    id = Column(BigInteger(), primary_key=True)
    phone = Column(String(20))
    sms_code = Column(String(20), default=None, nullable=True)
    token = Column(String(1000), default=None, nullable=True)
    wait_code = Column(Boolean(), default=False, nullable=False)

    __mapper_args__ = {"eager_defaults": True}

    @classmethod
    async def get_all(cls, session):
        stmt = select(ReportPhoneAccount)
        result = (await session.execute(stmt)).scalars().all()
        return result

    @classmethod
    async def get(cls, session, account_id):
        stmt = select(ReportPhoneAccount).where(ReportPhoneAccount.id == account_id)
        result = (await session.execute(stmt)).scalar()
        return result

    @classmethod
    async def update_token(cls, session, account_id: int, token: str):
        stmt = update(cls).where(cls.id == account_id).values(
            token=token,
            sms_code='',
            wait_code=True)
        await session.execute(stmt)
