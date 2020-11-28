from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_repr import RepresentableBase


Base = declarative_base(cls=RepresentableBase)
class SourceFilename(Base):
    __tablename__ = 'source_filenames'

    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
