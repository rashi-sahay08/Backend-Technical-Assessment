from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

DATA_FILE = os.path.join("data", "customers.json")

def load_customers():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# Health check
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200

# Get paginated customers
@app.route("/api/customers", methods=["GET"])
def get_customers():
    customers = load_customers()

    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))

    start = (page - 1) * limit
    end = start + limit

    return jsonify({
        "data": customers[start:end],
        "total": len(customers),
        "page": page,
        "limit": limit
    })

# Get customer by ID
@app.route("/api/customers/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):
    customers = load_customers()

    customer = next(
        (c for c in customers if c["customer_id"] == customer_id),
        None
    )

    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    return jsonify(customer)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)