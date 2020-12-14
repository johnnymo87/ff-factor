from sqlalchemy import Column, Date, Integer, Numeric, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_repr import RepresentableBase

Base = declarative_base(cls=RepresentableBase)
class TickerPrice(Base):
    __tablename__ = 'ticker_prices'

    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)
    occurred_at = Column(Date, nullable=False)
    percentage_change = Column(Numeric, nullable=False)
