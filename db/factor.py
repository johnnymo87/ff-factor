from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Date, Integer, Numeric

Base = declarative_base()
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

    def __repr__(self):
       return "<SourceFilename(id='%d', filename='%s'>" % (
           self.id,
           self.filename)
