# Pet Welfare Backend (FastAPI)

This is the backend API for the Pet Health & Welfare Database project.
It connects to a MySQL database hosted on Railway and provides data to the React UI.

## How to Run Locally

1. Install Python packages:
   pip install -r requirements.txt

2. Set your database connection (replace with your own values):
   export DATABASE_URL="mysql+pymysql://<user>:<password>@<host>/<database>"

3. Start the server:
   uvicorn main:app --reload

4. Open API documentation:
   http://localhost:8000/docs

## Main Endpoints

Core UI Endpoints:
- GET /animals-simple : list animals
- POST /add-animal : add new animal
- DELETE /delete-animal/{animal_id} : delete animal
- GET /animal-stats : count animals by species

Additional Analysis Endpoints:
- GET /welfare-followups : animals needing follow-up
- GET /adoption-stats : adoption statistics
- GET /health : health check
- GET / : root endpoint

## Technologies Used

- FastAPI
- Python
- Raw SQL (no ORM)
- Railway for database hosting

## Notes

- Backend uses raw SQL to interact with the database.
- Update the DATABASE_URL environment variable if your MySQL connection details change.
- Designed to work with the React UI deployed on Vercel.