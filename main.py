from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel


from database import get_db


app = FastAPI()

class AnimalCreate(BaseModel):
    OrgID: int
    Species: str
    Sex: str
    AgeMonths: int


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


 @app.post("/add-animal")
def add_animal(animal: AnimalCreate, db: Session = Depends(get_db)):
    """
    Simple CREATE endpoint:
    Inserts a new animal row into the Animal table.
    """
    query = text("""
        INSERT INTO Animal (OrgID, Species, Sex, AgeMonths)
        VALUES (:org_id, :species, :sex, :age)
    """)
    db.execute(
        query,
        {
            "org_id": animal.OrgID,
            "species": animal.Species,
            "sex": animal.Sex,
            "age": animal.AgeMonths,
        },
    )
    db.commit()
    return {"status": "success"}
   