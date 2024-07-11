from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session


def create_db_session(db_url: str) -> scoped_session:
    engine = create_engine(db_url)
    return scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


Base = declarative_base()