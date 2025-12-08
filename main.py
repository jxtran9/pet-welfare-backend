from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db

app = FastAPI()

# Allow your frontend to call the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can later change this to your exact frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Hello from Railway backend with DB!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/animals-simple")
def list_animals(db: Session = Depends(get_db)):
    query = text("""
        SELECT AnimalID, Species, Sex, AgeMonths
        FROM Animal
        LIMIT 20;
    """)
    rows = db.execute(query).mappings().all()
    return list(rows)