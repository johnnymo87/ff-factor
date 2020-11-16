from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()
class SourceFilename(Base):
    __tablename__ = 'source_filenames'

    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)

    def __repr__(self):
       return "<SourceFilename(id='%d', filename='%s'>" % (
           self.id,
           self.filename)
