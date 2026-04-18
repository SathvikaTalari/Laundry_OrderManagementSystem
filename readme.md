# 🧺 LaundryOS — AI-First Laundry Order Management System

> A full-stack dry cleaning management platform with role-based authentication, real-time order tracking, estimated delivery, and dual dashboards for staff and customers.

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Features Implemented](#-features-implemented)
- [Tech Stack](#-tech-stack)
- [Setup Instructions](#-setup-instructions)
- [Default Credentials](#-default-credentials)
- [API Reference](#-api-reference)
- [AI Usage Report](#-ai-usage-report)
- [Tradeoffs & Decisions](#-tradeoffs--decisions)
- [Known Issues](#-known-issues)
- [Future Improvements](#-future-improvements)
- [Project Structure](#-project-structure)

---

## 🌟 Overview

LaundryOS is a complete order management system built for dry cleaning stores. It supports two user roles — **Staff** and **Customer** — each with their own tailored dashboard. Orders can be created, tracked through a status pipeline, billed automatically, and assigned an estimated delivery date based on the chosen service type.

The project was built as an AI-first exercise, using Claude (Anthropic) as the primary development assistant throughout the entire build.

---

## ✅ Features Implemented

### 🔐 Authentication
- JWT-style token-based login and registration
- Role-based access control: `staff` and `customer`
- Session persistence via `localStorage` — stays logged in on page refresh
- Auto-seeded staff account on first startup
- Secure password hashing (SHA-256 + secret key)
- Token invalidation on logout

### 👔 Staff Dashboard
- **Stats overview:** Total orders, total revenue, today's orders, today's revenue, total registered customers
- **Order pipeline:** Live count of orders in each status (Received → Processing → Ready → Delivered)
- **Full orders table** with search (by name, phone, order ID) and status filters
- **Order detail modal** with full garment breakdown and inline status updater
- Ability to create orders on behalf of any customer

### 👤 Customer Dashboard
- **Personal stats:** Total orders placed, total amount spent, active orders count
- **Order cards** with animated progress bars showing order completion percentage
- 🔔 "Ready for Pickup" alert badge on eligible orders
- Order history with status filter tabs
- Self-service order placement

### 📦 Order Management
- Unique Order ID generation (`ORD-XXXXXXXX` format)
- Multi-garment orders with per-item pricing
- Auto-fill pricing from a configurable garment price list
- Running bill preview updated live as garments are added
- Special instructions / notes field per order
- Full order detail view for both staff and customers

### 📅 Estimated Delivery
- Three service tiers with different turnaround times:
  | Service | Turnaround | Badge |
  |---------|-----------|-------|
  | Standard | 3 business days | Economy |
  | Express | Next day | +20% |
  | Same Day | By 8:00 PM today | Priority |
- Estimated delivery date stored in the database
- Displayed on order cards, order detail modal, and bill preview panel

### 📊 Billing
- Hardcoded price list (editable in `main.py`)
- Per-garment subtotal calculation
- Live total bill preview before order submission
- Revenue tracked in both staff dashboard (all-time + today)

---

## 🛠 Tech Stack

| Layer | Technology | Reason |
|-------|-----------|--------|
| Backend | Python + FastAPI | Fast to build, async-ready, auto docs at `/docs` |
| Database | SQLite + SQLAlchemy | Zero-config, file-based, perfect for single-server deployment |
| Auth | Custom token system | Avoids JWT library Python 3.14 compatibility issues |
| Frontend | Vanilla HTML/CSS/JS | No build step required — just open the file |
| Fonts | Google Fonts (Playfair Display + Outfit) | Premium editorial feel |

---

## ⚙️ Setup Instructions

### Prerequisites

- Python 3.9 or higher (tested up to 3.14)
- `pip` package manager
- A modern web browser

---

### Step 1 — Clone or Download

```bash
git clone https://github.com/yourusername/laundryos.git
cd laundryos
```

Or download and unzip the project folder.

---

### Step 2 — Install Backend Dependencies

Navigate into the backend folder and install requirements:

```bash
cd backend
pip install -r requirements.txt
```

> ⚠️ **Python 3.14 users:** The pinned versions in `requirements.txt` use `>=` ranges to ensure compatibility. If you see build errors related to `pydantic-core`, make sure you have the latest pip: `pip install --upgrade pip`

---

### Step 3 — Start the Backend Server

```bash
python main.py
```

You should see:

```
INFO:     Started server process [XXXXX]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

The server creates `laundry.db` automatically on first run and seeds a default staff account.

> 💡 **Keep this terminal open.** The backend must stay running while you use the app.

---

### Step 4 — Open the Frontend

Open `frontend/index.html` directly in your browser (double-click in File Explorer, or drag into Chrome/Edge).

- The Backend URL field defaults to `http://localhost:8000`
- Click **Connect** to verify the backend is reachable
- Log in or register to start using the app

> ⚠️ Do **not** navigate to `http://localhost:8000` in your browser — the backend only serves API routes, not a webpage. The frontend is a separate HTML file.

---

### Step 5 — (Optional) Interactive API Docs

FastAPI generates interactive documentation automatically:

```
http://localhost:8000/docs
```

---

## 🔑 Default Credentials

| Role | Email | Password |
|------|-------|----------|
| Staff | `staff@laundry.com` | `staff123` |
| Customer | Register a new account | Your chosen password |

---

## 📡 API Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/auth/register` | None | Register new customer |
| `POST` | `/auth/login` | None | Login and get token |
| `POST` | `/auth/logout` | Token | Invalidate session |
| `GET` | `/auth/me` | Token | Get current user info |
| `GET` | `/garments/prices` | None | Get price list |
| `POST` | `/orders` | Token | Create new order |
| `GET` | `/orders` | Token | List orders (filtered by role) |
| `GET` | `/orders/{id}` | Token | Get single order |
| `PATCH` | `/orders/{id}/status` | Staff | Update order status |
| `GET` | `/dashboard/staff` | Staff | Staff analytics |
| `GET` | `/dashboard/customer` | Token | Customer analytics |

Customers automatically see only their own orders. Staff sees all orders.

---

## 🤖 AI Usage Report

### Tools Used

**Primary tool: Claude (Anthropic) — claude.ai**

This entire project was built interactively with Claude as the development assistant — from initial architecture decisions through debugging Python 3.14 compatibility errors.

No other AI tools (ChatGPT, GitHub Copilot, Gemini) were used in this project.

---

### Sample Prompts Used

**Prompt 1 — Initial Build**
> *"Build a Mini Laundry Order Management System (AI-First). Features: Create orders with customer name, phone, garments, quantity, price. Order status management (RECEIVED, PROCESSING, READY, DELIVERED). View all orders with filters. Basic dashboard. Use frontend and Python for backend and database."*

**Prompt 2 — Fixing Python 3.14 Compatibility**
> *"There is an error in requirements.txt [pasted error log showing pydantic-core build failure on Python 3.14]"*

**Prompt 3 — Major Feature Addition**
> *"Add authentication and a dashboard for both staff and the user and even add estimated delivery and make the UI look good."*

**Prompt 4 — Debugging Runtime**
> *"[Pasted terminal output showing server starting but GET / returning 404]"*

---

### What AI Got Right

- **FastAPI boilerplate** — generated the full route structure, Pydantic models, SQLAlchemy models, CORS config, and dependency injection pattern correctly in one pass
- **Database relationships** — the `User` ↔ `Order` foreign key relationship and SQLAlchemy ORM setup worked without modification
- **Role-based filtering** — customers automatically seeing only their own orders was implemented correctly first try
- **Frontend structure** — the single-file HTML/CSS/JS architecture with no build step was a smart suggestion for this use case
- **Estimated delivery logic** — the `timedelta` calculation for delivery dates based on service type was correct immediately
- **UI/UX design** — the warm cream + teal + gold palette, progress bars, and card-based customer view were all generated with good design sensibility

---

### What AI Got Wrong

**1. Python Version Compatibility**

The initial `requirements.txt` pinned `pydantic==2.9.2`, which requires compiling `pydantic-core` from Rust source. This fails on Python 3.14 because the Rust bindings (PyO3 v0.22.2) only supported up to Python 3.13 at that version.

*Fix applied:* Switched to `>=` version ranges so pip resolves the latest compatible pre-built wheels (`pydantic>=2.10.0` which ships Python 3.14 wheels).

**2. Deprecated SQLAlchemy Import**

Used `from sqlalchemy.ext.declarative import declarative_base` which is deprecated in SQLAlchemy 2.0. This generated a `MovedIn20Warning` on every startup.

*Fix applied:* Changed to `from sqlalchemy.orm import declarative_base`.

**3. `GET /` Returns 404**

The initial instructions didn't make it clear that the FastAPI backend serves no HTML homepage. Users navigating to `http://localhost:8000` in a browser got a 404, causing confusion.

*Fix applied:* Clarified in documentation that the frontend is a separate HTML file and should be opened directly — not served by the backend.

**4. Token Auth Approach**

The first auth implementation attempted to use `python-jose` for JWT tokens. This library also has Python 3.14 build issues. 

*Fix applied:* Replaced with a custom SHA-256 + in-memory token store approach that has zero external dependencies and works on all Python versions.

---

### What Was Improved Beyond AI Output

- Added `@app.on_event("startup")` staff seeding so the demo account exists automatically
- Added `localStorage` session persistence so users don't have to log in again on refresh
- Added Enter key support on the login form for better UX
- Added Escape key to close the order detail modal
- Improved the garment price auto-fill behavior (price populates immediately on garment select)
- Added a "Ready for pickup" animated badge on customer order cards
- Pre-filled customer name on the "New Order" form using the logged-in user's name

---

## ⚖️ Tradeoffs & Decisions

### What Was Skipped

| Feature | Reason Skipped |
|---------|---------------|
| Email notifications | Requires SMTP config — out of scope for local demo |
| Payment integration | Razorpay/Stripe adds significant complexity and API keys |
| PDF invoice generation | Would need `reportlab` or `weasyprint`, adds setup complexity |
| Admin panel to manage staff accounts | Only one staff account needed for demo |
| Real JWT with expiry | `python-jose` has Python 3.14 build issues; custom tokens work fine |
| Garment image upload | Adds file storage complexity without core value |
| Multi-store / multi-branch support | Single store assumed for v1 |
| Unit tests | Would double the codebase size; skipped for time |
| Dark mode | Light theme chosen as primary; dark mode is a v2 feature |
| Pagination | All orders returned; acceptable for demo scale |

### Design Decisions & Their Tradeoffs

**SQLite over PostgreSQL**
- ✅ Zero setup, file-based, works everywhere
- ❌ Not suitable for concurrent multi-user production loads; would need migration to Postgres for scale

**Vanilla HTML/JS over React**
- ✅ No build step, no Node.js required, single file, runs directly in browser
- ❌ State management becomes complex as features grow; React/Vue would be cleaner at scale

**In-memory token store**
- ✅ Avoids external JWT library issues, simple to understand
- ❌ All sessions are lost when the server restarts; users must log in again

**SHA-256 password hashing over bcrypt**
- ✅ No compilation required, works on Python 3.14 out of the box
- ❌ SHA-256 is faster than bcrypt, making brute-force attacks easier; bcrypt is the production standard

**Single-file frontend**
- ✅ Dead simple to deploy and share — just open the file
- ❌ The HTML file becomes large (1,468 lines); harder to maintain as a team

---

## 🐛 Known Issues

1. **Session lost on server restart** — In-memory token store is cleared when `python main.py` is restarted. Users need to log in again. Fix: persist tokens in the database.

2. **No token expiry** — Tokens stay valid until the server restarts or the user explicitly logs out. Fix: add `created_at` timestamp to tokens and enforce a TTL.

3. **Concurrent write safety** — SQLite has limited write concurrency. Under high simultaneous load, writes may queue. Fix: switch to PostgreSQL.

4. **Garment prices not editable from UI** — Prices are hardcoded in `main.py`. Fix: add a settings page for staff to manage the price list.

---

## 🚀 Future Improvements

### Short Term (1–2 days)
- [ ] Persist tokens in the database with expiry timestamps
- [ ] Add bcrypt password hashing
- [ ] Add pagination to orders table
- [ ] Add a "Forgot Password" flow
- [ ] Allow staff to add/edit garment prices from the UI

### Medium Term (1 week)
- [ ] PDF invoice generation per order (download button)
- [ ] SMS/email notification when order status changes to READY
- [ ] Customer order history export (CSV)
- [ ] Analytics charts — revenue over time, popular garments, busiest days
- [ ] Dark mode toggle

### Long Term (Production-Ready)
- [ ] Migrate from SQLite to PostgreSQL
- [ ] Deploy backend to Railway / Render / AWS
- [ ] Build proper React frontend with component architecture
- [ ] Add payment integration (Razorpay for India)
- [ ] Multi-branch support with branch-level staff accounts
- [ ] Mobile app (React Native) for customers to track orders
- [ ] Real JWT authentication with refresh tokens
- [ ] Comprehensive unit + integration tests

---

## 📁 Project Structure

```
laundryos/
├── backend/
│   ├── main.py              # FastAPI app — all routes, models, auth
│   ├── requirements.txt     # Python dependencies
│   └── laundry.db           # SQLite database (auto-created on first run)
│
├── frontend/
│   └── index.html           # Complete frontend — auth, staff & customer UIs
│
└── README.md                # This file
```

---

## 📄 License

This project is licensed under the MIT License — free to use, modify, and distribute.

---

## 🙌 Acknowledgements

- Built with [FastAPI](https://fastapi.tiangolo.com/) — modern Python web framework
- Database ORM by [SQLAlchemy](https://www.sqlalchemy.org/)
- Fonts by [Google Fonts](https://fonts.google.com/) — Playfair Display & Outfit
- Developed interactively with [Claude](https://claude.ai) by Anthropic

---

## 📸 Screenshots of Application

### Login Page
![Login Page](Screen%20shot%20images/Login%20Page.png)

### Staff Dashboard
![Staff Dashboard](Screen%20shot%20images/Staff%20Dashboard.png)

### Staff Orders List
![Staff Orders List](Screen%20shot%20images/Staff%20Orders%20List.png)

### Customer Dashboard
![Customer Dashboard](Screen%20shot%20images/Customer%20Dashboard.png)

### Customer Orders
![Customer Orders](Screen%20shot%20images/Customer%20Orders.png)

### New Order Page
![New Order Page](Screen%20shot%20images/New%20Order%20Page.png)