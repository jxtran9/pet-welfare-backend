from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello from Railway backend with DB!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/animals-simple")
def list_animals(db: Session = Depends(get_db)):
    """
    Simple example: return up to 20 animals from the Animal table.
    Adjust column names if your schema is different.
    """
    query = text("""
        SELECT AnimalID, Species, Sex, AgeMonths
        FROM Animal
        LIMIT 20;
    """)
    rows = db.execute(query).mappings().all()
    return list(rows)