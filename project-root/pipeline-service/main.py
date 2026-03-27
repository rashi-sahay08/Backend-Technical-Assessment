from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models.customer import Customer
from services.ingestion import fetch_all_customers, upsert_customers

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. Ingest API
@app.post("/api/ingest")
def ingest(db: Session = Depends(get_db)):
    customers = fetch_all_customers()
    count = upsert_customers(db, customers)

    return {"status": "success", "records_processed": count}

# 2. Get customers (paginated)
@app.get("/api/customers")
def get_customers(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    offset = (page - 1) * limit

    data = db.query(Customer).offset(offset).limit(limit).all()
    total = db.query(Customer).count()

    return {
        "data": [c.__dict__ for c in data],
        "total": total,
        "page": page,
        "limit": limit
    }

# 3. Get single customer
@app.get("/api/customers/{customer_id}")
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter_by(customer_id=customer_id).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer