from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import uuid, json, hashlib, secrets, os

# ─── Database ────────────────────────────────────────────────────────────────
DATABASE_URL = "sqlite:///./laundry.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ─── Config ──────────────────────────────────────────────────────────────────
SECRET_KEY = "laundryos-super-secret-key-2024"
DELIVERY_DAYS = {"STANDARD": 3, "EXPRESS": 1, "SAME_DAY": 0}

GARMENT_PRICES = {
    "Shirt": 40, "Pants": 60, "Saree": 120, "Kurta": 50,
    "Jacket": 150, "Dress": 100, "Suit": 250, "Bed Sheet": 80,
    "Blanket": 200, "T-Shirt": 35, "Jeans": 70, "Coat": 180,
}

# ─── DB Models ───────────────────────────────────────────────────────────────
class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    password_hash = Column(String)
    role = Column(String, default="customer")
    created_at = Column(DateTime, default=datetime.utcnow)
    orders = relationship("OrderDB", back_populates="user")

class OrderDB(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    customer_name = Column(String, index=True)
    phone = Column(String, index=True)
    garments = Column(String)
    total_amount = Column(Float)
    status = Column(String, default="RECEIVED")
    service_type = Column(String, default="STANDARD")
    estimated_delivery = Column(DateTime)
    notes = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("UserDB", back_populates="orders")

Base.metadata.create_all(bind=engine)

# ─── Auth Helpers ─────────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    return hashlib.sha256((password + SECRET_KEY).encode()).hexdigest()

def make_token(user_id: int, role: str) -> str:
    rand = secrets.token_hex(16)
    sig = hashlib.sha256((f"{user_id}:{role}:{rand}" + SECRET_KEY).encode()).hexdigest()
    return f"{sig}.{user_id}.{role}"

active_tokens: dict = {}

security = HTTPBearer(auto_error=False)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = credentials.credentials
    if token not in active_tokens:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return active_tokens[token]

def require_staff(user=Depends(get_current_user)):
    if user["role"] != "staff":
        raise HTTPException(status_code=403, detail="Staff access required")
    return user

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def order_to_dict(order: OrderDB):
    return {
        "order_id": order.order_id,
        "customer_name": order.customer_name,
        "phone": order.phone,
        "garments": json.loads(order.garments),
        "total_amount": order.total_amount,
        "status": order.status,
        "service_type": order.service_type,
        "estimated_delivery": order.estimated_delivery.isoformat() if order.estimated_delivery else None,
        "notes": order.notes or "",
        "created_at": order.created_at.isoformat() if order.created_at else "",
        "updated_at": order.updated_at.isoformat() if order.updated_at else "",
        "user_id": order.user_id,
    }

def seed_staff():
    db = SessionLocal()
    existing = db.query(UserDB).filter(UserDB.email == "staff@laundry.com").first()
    if not existing:
        staff = UserDB(
            name="Store Manager",
            email="staff@laundry.com",
            phone="9000000000",
            password_hash=hash_password("staff123"),
            role="staff"
        )
        db.add(staff)
        db.commit()
    db.close()

# ─── Pydantic Schemas ─────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    name: str
    email: str
    phone: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class GarmentItem(BaseModel):
    name: str
    quantity: int
    price_per_item: Optional[float] = None

class CreateOrderRequest(BaseModel):
    customer_name: str
    phone: str
    garments: List[GarmentItem]
    service_type: Optional[str] = "STANDARD"
    notes: Optional[str] = ""

class UpdateStatusRequest(BaseModel):
    status: str

# ─── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(title="LaundryOS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    seed_staff()

# ─── Auth ────────────────────────────────────────────────────────────────────
@app.post("/auth/register")
def register(req: RegisterRequest, db=Depends(get_db)):
    if db.query(UserDB).filter(UserDB.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = UserDB(
        name=req.name, email=req.email, phone=req.phone,
        password_hash=hash_password(req.password), role="customer"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = make_token(user.id, user.role)
    active_tokens[token] = {"user_id": user.id, "role": user.role, "name": user.name, "email": user.email}
    return {"token": token, "role": user.role, "name": user.name, "email": user.email, "user_id": user.id}

@app.post("/auth/login")
def login(req: LoginRequest, db=Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == req.email).first()
    if not user or user.password_hash != hash_password(req.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = make_token(user.id, user.role)
    active_tokens[token] = {"user_id": user.id, "role": user.role, "name": user.name, "email": user.email}
    return {"token": token, "role": user.role, "name": user.name, "email": user.email, "user_id": user.id}

@app.post("/auth/logout")
def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials and credentials.credentials in active_tokens:
        del active_tokens[credentials.credentials]
    return {"message": "Logged out"}

@app.get("/auth/me")
def me(user=Depends(get_current_user)):
    return user

# ─── Garments ────────────────────────────────────────────────────────────────
@app.get("/garments/prices")
def get_garment_prices():
    return GARMENT_PRICES

# ─── Orders ──────────────────────────────────────────────────────────────────
@app.post("/orders")
def create_order(req: CreateOrderRequest, user=Depends(get_current_user), db=Depends(get_db)):
    order_id = "ORD-" + str(uuid.uuid4())[:8].upper()
    garments_data = []
    total = 0.0
    for g in req.garments:
        price = g.price_per_item if g.price_per_item else GARMENT_PRICES.get(g.name, 50)
        subtotal = price * g.quantity
        total += subtotal
        garments_data.append({"name": g.name, "quantity": g.quantity, "price_per_item": price, "subtotal": subtotal})

    days = DELIVERY_DAYS.get(req.service_type, 3)
    est_delivery = datetime.utcnow() + timedelta(days=days)

    order = OrderDB(
        order_id=order_id, user_id=user["user_id"],
        customer_name=req.customer_name, phone=req.phone,
        garments=json.dumps(garments_data), total_amount=total,
        status="RECEIVED", service_type=req.service_type or "STANDARD",
        estimated_delivery=est_delivery, notes=req.notes or "",
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order_to_dict(order)

@app.get("/orders")
def list_orders(
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    user=Depends(get_current_user), db=Depends(get_db)
):
    query = db.query(OrderDB)
    if user["role"] == "customer":
        query = query.filter(OrderDB.user_id == user["user_id"])
    if status and status != "ALL":
        query = query.filter(OrderDB.status == status)
    if search:
        query = query.filter(
            (OrderDB.customer_name.ilike(f"%{search}%")) |
            (OrderDB.phone.ilike(f"%{search}%")) |
            (OrderDB.order_id.ilike(f"%{search}%"))
        )
    orders = query.order_by(OrderDB.created_at.desc()).all()
    return [order_to_dict(o) for o in orders]

@app.get("/orders/{order_id}")
def get_order(order_id: str, user=Depends(get_current_user), db=Depends(get_db)):
    order = db.query(OrderDB).filter(OrderDB.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if user["role"] == "customer" and order.user_id != user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    return order_to_dict(order)

@app.patch("/orders/{order_id}/status")
def update_status(order_id: str, req: UpdateStatusRequest, staff=Depends(require_staff), db=Depends(get_db)):
    valid = ["RECEIVED", "PROCESSING", "READY", "DELIVERED"]
    if req.status not in valid:
        raise HTTPException(status_code=400, detail="Invalid status")
    order = db.query(OrderDB).filter(OrderDB.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = req.status
    order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(order)
    return order_to_dict(order)

# ─── Dashboards ──────────────────────────────────────────────────────────────
@app.get("/dashboard/staff")
def staff_dashboard(staff=Depends(require_staff), db=Depends(get_db)):
    orders = db.query(OrderDB).all()
    today = datetime.utcnow().date()
    today_orders = [o for o in orders if o.created_at and o.created_at.date() == today]
    status_counts = {"RECEIVED": 0, "PROCESSING": 0, "READY": 0, "DELIVERED": 0}
    for o in orders:
        if o.status in status_counts:
            status_counts[o.status] += 1
    service_revenue = {}
    for o in orders:
        service_revenue[o.service_type] = service_revenue.get(o.service_type, 0) + o.total_amount
    recent = sorted(orders, key=lambda x: x.created_at, reverse=True)[:8]
    customers = db.query(UserDB).filter(UserDB.role == "customer").count()
    return {
        "total_orders": len(orders),
        "total_revenue": sum(o.total_amount for o in orders),
        "today_orders": len(today_orders),
        "today_revenue": sum(o.total_amount for o in today_orders),
        "total_customers": customers,
        "orders_by_status": status_counts,
        "service_revenue": service_revenue,
        "recent_orders": [order_to_dict(o) for o in recent],
    }

@app.get("/dashboard/customer")
def customer_dashboard(user=Depends(get_current_user), db=Depends(get_db)):
    orders = db.query(OrderDB).filter(OrderDB.user_id == user["user_id"]).all()
    status_counts = {"RECEIVED": 0, "PROCESSING": 0, "READY": 0, "DELIVERED": 0}
    for o in orders:
        if o.status in status_counts:
            status_counts[o.status] += 1
    active = [o for o in orders if o.status != "DELIVERED"]
    recent = sorted(orders, key=lambda x: x.created_at, reverse=True)[:5]
    return {
        "total_orders": len(orders),
        "total_spent": sum(o.total_amount for o in orders),
        "active_orders": len(active),
        "orders_by_status": status_counts,
        "recent_orders": [order_to_dict(o) for o in recent],
    }

# ─── Serve Frontend ──────────────────────────────────────────────────────────
@app.get("/", response_class=FileResponse)
def serve_frontend():
    return FileResponse(os.path.join(os.path.dirname(__file__), "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
