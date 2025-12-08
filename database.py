import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Get DATABASE_URL from Railway env vars
raw_url = os.getenv("DATABASE_URL")

if not raw_url:
    raise RuntimeError("DATABASE_URL is not set")

# Tell SQLAlchemy to use PyMySQL driver
DATABASE_URL = raw_url.replace("mysql://", "mysql+pymysql://")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()