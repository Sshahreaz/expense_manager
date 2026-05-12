# 💰 Expense Manager

A full-stack **Expense Management System** built with FastAPI, Streamlit, and MySQL. Track your daily expenses by category, visualize spending patterns, and analyze trends with an interactive dashboard.

---

## Live Demo

> Start the backend and frontend locally to explore the full application.

---

## Features

- ➕ **Add & Update Expenses** — Log expenses by date and category
- 📊 **Analytics Dashboard** — Interactive pie and bar charts by category
- 📋 **Expense History** — Browse full spending history across date ranges
- ✅ **Automated Testing** — 11 Pytest tests with 100% pass rate
- 🔌 **REST API** — Auto-documented with Swagger UI

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI + Python 3.11 |
| **Frontend** | Streamlit + Plotly |
| **Database** | MySQL 8.0 |
| **Validation** | Pydantic v2 |
| **Testing** | Pytest |
| **Server** | Uvicorn |

---

## Project Structure

```
expense_project/
├── backend/
│   ├── db_helper.py         # Database CRUD operations with context manager
│   ├── logging_setup.py     # Logging configuration
│   └── server.py            # FastAPI server with Pydantic models
├── frontend/
│   ├── app.py               # Main Streamlit app with tabs
│   ├── add_update_ui.py     # Add/Update expenses UI
│   └── analytics_ui.py      # Analytics dashboard with charts
├── tests/
│   ├── conftest.py          # Pytest path configuration
│   └── backend/
│       └── test_db_helper.py  # Database layer tests
├── database/
│   └── expense_db_creation.sql  # MySQL schema
└── requirements.txt
```

---

##  Setup Instructions

### Prerequisites
- Python 3.11+
- MySQL 8.0 running on localhost
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/Sshahreaz/expense_manager.git
cd expense_manager
```

### 2. Create Virtual Environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate.ps1

# Mac/Linux
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup MySQL Database
```bash
# Windows
Get-Content database/expense_db_creation.sql | & "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -proot

# Mac/Linux
mysql -u root -p < database/expense_db_creation.sql
```

### 5. Start the Backend
```bash
cd backend
uvicorn server:app --reload
```

Backend runs at: `http://127.0.0.1:8000`  
API Docs at: `http://127.0.0.1:8000/docs`

### 6. Start the Frontend
Open a new terminal:
```bash
cd frontend
streamlit run app.py
```

Frontend runs at: `http://localhost:8501`

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/expenses/{date}` | Fetch expenses for a date |
| `POST` | `/expenses/{date}` | Add or update an expense |
| `POST` | `/analytics/` | Get summary by category |
| `GET` | `/categories/` | Get all unique categories |

### Example Request
```bash
# Add an expense
curl -X POST "http://127.0.0.1:8000/expenses/2026-05-08" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-05-08",
    "category": "Food",
    "amount": 25.50,
    "notes": "Lunch"
  }'
```

### Example Response
```json
{
  "status": "success",
  "expense": {
    "id": 1,
    "expense_date": "2026-05-08",
    "category": "Food",
    "amount": 25.50,
    "notes": "Lunch"
  }
}
```

---

##  Database Schema

```sql
CREATE TABLE expenses (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    expense_date    DATE            NOT NULL,
    category        VARCHAR(255)    NOT NULL,
    amount          DECIMAL(10, 2)  NOT NULL,
    notes           TEXT,
    UNIQUE KEY date_category (expense_date, category)
);
```

**Design Decisions:**
- `DECIMAL(10,2)` for exact monetary precision
- `UNIQUE KEY` on date + category enforces one entry per category per day
- `notes` field for optional context

---

##  Running Tests

```bash
# From project root
pytest tests/ -v
```

Expected output:
```
tests/backend/test_db_helper.py::test_get_categories_returns_list          PASSED
tests/backend/test_db_helper.py::test_get_categories_contains_strings      PASSED
tests/backend/test_db_helper.py::test_get_expenses_by_date_returns_list    PASSED
tests/backend/test_db_helper.py::test_get_expenses_by_date_filters_by_date PASSED
tests/backend/test_db_helper.py::test_get_expenses_by_date_has_required_fields PASSED
tests/backend/test_db_helper.py::test_add_or_update_expense_returns_dict   PASSED
tests/backend/test_db_helper.py::test_add_or_update_expense_creates_new    PASSED
tests/backend/test_db_helper.py::test_add_or_update_expense_updates_existing PASSED
tests/backend/test_db_helper.py::test_get_expenses_by_date_range_returns_list PASSED
tests/backend/test_db_helper.py::test_get_expenses_by_date_range_filters_dates PASSED
tests/backend/test_db_helper.py::test_full_workflow                        PASSED

11 passed in 0.48s
```

---

##  Architecture

```
Streamlit UI (localhost:8501)
        ↓  HTTP Requests
FastAPI Server (localhost:8000)
        ↓  Python Function Calls
db_helper.py (Context Manager)
        ↓  SQL Queries
MySQL Database (expense_manager)
```

**Key Patterns Used:**
- **Context Manager** — safe database connection handling
- **Pydantic v2** — request/response validation
- **Separation of Concerns** — backend, frontend, database layers isolated
- **Arrange-Act-Assert** — testing pattern for all unit tests

---

##  Future Enhancements

- [ ] User authentication (JWT tokens)
- [ ] CSV/PDF export
- [ ] Budget alerts and notifications
- [ ] Recurring expense automation
- [ ] Multi-currency support
- [ ] Mobile-responsive UI
- [ ] Docker containerization
- [ ] Cloud deployment (AWS/Railway)

---

##  Author

**Shadman Shahreaz (Rhythm)**
- GitHub: [@Sshahreaz](https://github.com/Sshahreaz)
- LinkedIn: [shadman-shahreaz](https://linkedin.com/in/shadman-shahreaz)

---

##  License

This project is open source and available under the [MIT License](LICENSE).

---

*Built with ❤️ using FastAPI • Streamlit • MySQL • Pytest*
