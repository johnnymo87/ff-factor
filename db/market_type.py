from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_repr import RepresentableBase


Base = declarative_base(cls=RepresentableBase)
class MarketType(Base):
    __tablename__ = 'market_types'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
