from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel

from database import get_db

app = FastAPI()

# CORS so UI (localhost or Vercel) can call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict later
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
    """
    Simple example: return up to 20 animals from the Animal table.
    Adjust column names if your schema is different.
    """
    query = text(
        """
        SELECT AnimalID, OrgID, Species, Sex, AgeMonths
        FROM Animal
        LIMIT 20;
        """
    )
    rows = db.execute(query).mappings().all()
    return list(rows)


# ---------- CRUD: Create animal ----------

class AnimalCreate(BaseModel):
    OrgID: int
    Species: str
    Sex: str
    AgeMonths: int


@app.post("/add-animal")
def add_animal(animal: AnimalCreate, db: Session = Depends(get_db)):
    """
    Simple CREATE endpoint:
    Inserts a new animal row into the Animal table.
    """
    query = text(
        """
        INSERT INTO Animal (OrgID, Species, Sex, AgeMonths)
        VALUES (:org_id, :species, :sex, :age)
        """
    )
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


# ---------- Complex query example ----------

@app.get("/animal-stats")
def animal_stats(db: Session = Depends(get_db)):
    """
    Example 'complex' query: aggregate animals by species.
    Can be used as a demo for analytical reporting.
    """
    query = text(
        """
        SELECT Species, COUNT(*) AS Count
        FROM Animal
        GROUP BY Species;
        """
    )
    rows = db.execute(query).mappings().all()
    return list(rows)
