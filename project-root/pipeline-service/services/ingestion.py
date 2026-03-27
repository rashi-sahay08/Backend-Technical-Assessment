import requests
from sqlalchemy.orm import Session
from models.customer import Customer

FLASK_API = "http://mock-server:5000/api/customers"

def fetch_all_customers():
    page = 1
    limit = 10
    all_data = []

    while True:
        response = requests.get(f"{FLASK_API}?page={page}&limit={limit}")
        data = response.json()

        customers = data.get("data", [])
        if not customers:
            break

        all_data.extend(customers)
        page += 1

    return all_data


def upsert_customers(db: Session, customers):
    count = 0

    for c in customers:
        existing = db.query(Customer).filter_by(
            customer_id=str(c["customer_id"])
        ).first()

        if existing:
            for key, value in c.items():
                setattr(existing, key, value)
        else:
            new_customer = Customer(
                customer_id=str(c["customer_id"]),
                first_name=c["first_name"],
                last_name=c["last_name"],
                email=c["email"],
                phone=c.get("phone"),
                address=c.get("address"),
                date_of_birth=c.get("date_of_birth"),
                account_balance=c.get("account_balance"),
                created_at=c.get("created_at")
            )
            db.add(new_customer)

        count += 1

    db.commit()
    return count