from sqlalchemy import Column, Date, Integer, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_repr import RepresentableBase

Base = declarative_base(cls=RepresentableBase)
class Factor(Base):
    __tablename__ = 'factors'

    id = Column(Integer, primary_key=True)
    source_filename_id = Column(Integer, nullable=False)
    occurred_at = Column(Date, nullable=False)
    mkt_rf = Column(Numeric, nullable=False)
    smb = Column(Numeric, nullable=False)
    hml = Column(Numeric, nullable=False)
    rf = Column(Numeric, nullable=False)
    mom = Column(Numeric)
    rmw = Column(Numeric)
    cma = Column(Numeric)
