from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, EmailStr
from typing import Optional
import mysql.connector

app = FastAPI(title="Pet Health & Welfare API")

# ---------- DB CONNECTION ----------

def get_connection():
    """
    Opens a new connection to the Railway-hosted MySQL database.
    Replace the placeholder values with your actual Railway info.
    """
    return mysql.connector.connect(
        host="mysql.railway.internal",
        port=3306,
        user="root",
        password="vMyDVSZsnhvoCLZcQblLnYOrFiNNcviL",
        database="railway"
    )

# ---------- REQUEST MODELS ----------

class AnimalCreate(BaseModel):
    AnimalID: int
    OrgID: int
    Species: str
    Sex: str
    AgeMonths: int
    Microchip: Optional[str] = None
    Notes: Optional[str] = None


class AdopterUpdate(BaseModel):
    Phone: str
    Email: EmailStr


# ---------- ENDPOINTS ----------

@app.get("/animals", summary="Search animals by species and organization")
def search_animals(
    species: Optional[str] = Query(None, description="Dog, Cat, etc."),
    org_id: Optional[int] = Query(None, description="Organization ID"),
):
    """
    Search animals by optional species and organization.
    If no filters are provided, returns all animals.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Base query
    sql = """
        SELECT
            AnimalID,
            OrgID,
            Species,
            Sex,
            AgeMonths,
            Microchip,
            Notes
        FROM Animal
    """

    conditions = []
    params = []

    # Add filters only if they were provided
    if species:
        conditions.append("Species = %s")
        params.append(species)

    if org_id is not None:
        conditions.append("OrgID = %s")
        params.append(org_id)

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    cursor.execute(sql, params)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows


@app.post("/animals", summary="Create a new animal")
def create_animal(animal: AnimalCreate):
    conn = get_connection()
    cur = conn.cursor()

    sql = """
        INSERT INTO Animal
            (AnimalID, OrgID, Species, Sex, AgeMonths, Microchip, Notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    params = (
        animal.AnimalID,
        animal.OrgID,
        animal.Species,
        animal.Sex,
        animal.AgeMonths,
        animal.Microchip,
        animal.Notes,
    )

    try:
        cur.execute(sql, params)
        conn.commit()
    except mysql.connector.Error as e:
        conn.rollback()
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))

    cur.close()
    conn.close()
    return {"message": "Animal created successfully"}


@app.put("/adopters/{ssn}", summary="Update adopter contact info")
def update_adopter(ssn: str, data: AdopterUpdate):
    conn = get_connection()
    cur = conn.cursor()

    sql = """
        UPDATE Adopter
        SET Phone = %s,
            Email = %s
        WHERE Ssn = %s;
    """
    params = (data.Phone, data.Email, ssn)

    cur.execute(sql, params)
    conn.commit()

    if cur.rowcount == 0:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Adopter not found")

    cur.close()
    conn.close()
    return {"message": "Adopter updated successfully"}
