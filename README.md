# Pet Welfare Backend (FastAPI)

This is the backend API for the Pet Health & Welfare Database project.  
It connects to our MySQL database on Railway and sends data to the React UI.

## How to Run Locally

1. Install Python packages:
   pip install -r requirements.txt

2. Set your database connection:
   export DATABASE_URL="mysql+pymysql://<user>:<password>@<host>/<database>"

3. Start the server:
   uvicorn main:app --reload

4. Open API docs:
   http://localhost:8000/docs

## Main Endpoints

- GET /animals-simple → list animals  
- POST /add-animal → add new animal  
- DELETE /delete-animal/{id} → delete animal  
- GET /animal-stats → counts animals by species

## Notes

- Backend is deployed on Railway.
- Uses FastAPI + SQLAlchemy + raw SQL.