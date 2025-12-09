from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Query
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
    Simple example: return up to 50 animals from the Animal table.
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


# ---------- Simple aggregate query ----------

@app.get("/animal-stats")
def animal_stats(db: Session = Depends(get_db)):
    """
    Example 'complex' query: aggregate animals by species.
    Used for the small chip summary in the UI.
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


# =====================================================
#   COMPLEX QUERIES FOR UI (with dropdown filters)
# =====================================================

@app.get("/welfare-followups")
def welfare_followups(
    species: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    """
    Complex welfare query for the UI.

    Shows animals whose welfare exam suggests they need additional attention.
    Here we approximate 'needs follow-up' as a lower HealthScore (<= 6),
    then join WelfareExam, Animal, and Organization.

    Optional filter:
      - species: If provided and not 'All', filters by Animal.Species.
    """
    base_sql = """
        SELECT
            A.AnimalID,
            A.Species,
            A.AgeMonths,
            A.Sex,
            Org.OrgName,
            W.Date      AS ExamDate,
            W.HealthScore,
            W.Notes
        FROM WelfareExam W
        JOIN Animal A
            ON W.AnimalID = A.AnimalID
        JOIN Organization Org
            ON W.OrgID = Org.OrgID
        WHERE W.HealthScore IS NOT NULL
          AND W.HealthScore <= 6
    """

    params: dict = {}

    if species is not None and species != "All":
        base_sql += " AND A.Species = :species"
        params["species"] = species

    base_sql += " ORDER BY W.Date DESC, A.AnimalID"

    query = text(base_sql)
    rows = db.execute(query, params).mappings().all()
    return list(rows)


@app.get("/adoption-stats")
def adoption_stats(
    state: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    """
    Complex adoption statistics query for the UI.

    Joins Adoption, Outcome, Animal, Adopter, and Location to compute
    adoption counts grouped by State and Species.

    Optional filter:
      - state: If provided and not 'All', restricts to that Location.State.
    """
    base_sql = """
        SELECT
            L.State,
            A.Species,
            COUNT(*) AS AdoptionCount
        FROM Adoption AD
        JOIN Outcome O
            ON AD.OutcomeID = O.OutcomeID
        JOIN Animal A
            ON O.AnimalID = A.AnimalID
        JOIN Adopter D
            ON AD.AdopterSsn = D.Ssn
        JOIN Location L
            ON D.LocationID = L.LocationID
    """

    params: dict = {}

    if state is not None and state != "All":
        base_sql += " WHERE L.State = :state"
        params["state"] = state

    base_sql += """
        GROUP BY L.State, A.Species
        ORDER BY L.State, A.Species
    """

    query = text(base_sql)
    rows = db.execute(query, params).mappings().all()
    return list(rows)
