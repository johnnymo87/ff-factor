# To talk to the DB
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, scoped_session


Engine = db.create_engine('postgresql://postgres:example@db/postgres')
Session = scoped_session(sessionmaker(bind=Engine))
