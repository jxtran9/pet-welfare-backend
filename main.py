from fastapi import FastAPI, Depends, HTTPException
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
        SELECT AnimalID, OrgID, Species, Sex, AgeMonths, Microchip, Notes
        FROM Animal
        ORDER BY AnimalID
        LIMIT 50;
        """
    )
    rows = db.execute(query).mappings().all()
    return list(rows)


# ---------- CRUD: Create animal ----------

class AnimalCreate(BaseModel):
    AnimalID: int
    OrgID: int
    Species: str
    Sex: str
    AgeMonths: int
    Microchip: str | None = None
    Notes: str | None = None



@app.post("/add-animal")
def add_animal(animal: AnimalCreate, db: Session = Depends(get_db)):
    """
    Simple CREATE endpoint:
    Inserts a new animal row into the Animal table.
    AnimalID is provided by the client (must be unique and >= 1).
    """
    query = text(
        """
        INSERT INTO Animal (AnimalID, OrgID, Species, Sex, AgeMonths, Microchip, Notes)
        VALUES (:animal_id, :org_id, :species, :sex, :age, :microchip, :notes)
        """
    )
    db.execute(
        query,
        {
            "animal_id": animal.AnimalID,
            "org_id": animal.OrgID,
            "species": animal.Species,
            "sex": animal.Sex,
            "age": animal.AgeMonths,
            "microchip": animal.Microchip,
            "notes": animal.Notes,
        },
    )
    db.commit()
    return {"status": "success"}

@app.delete("/delete-animal/{animal_id}")
def delete_animal(animal_id: int, db: Session = Depends(get_db)):
    """
    DELETE endpoint:
    Deletes an animal row from the Animal table by AnimalID.
    """
    # Check if the animal exists
    check_query = text(
        """
        SELECT AnimalID
        FROM Animal
        WHERE AnimalID = :animal_id
        """
    )
    row = db.execute(check_query, {"animal_id": animal_id}).first()
    if not row:
        # If not found, return 404 so UI can react
        raise HTTPException(status_code=404, detail="Animal not found")

    # Perform delete
    delete_query = text(
        """
        DELETE FROM Animal
        WHERE AnimalID = :animal_id
        """
    )
    db.execute(delete_query, {"animal_id": animal_id})
    db.commit()

    return {"status": "deleted", "animal_id": animal_id}


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
