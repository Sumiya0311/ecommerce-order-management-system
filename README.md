# E-Commerce Order Management System

## 📌 Project Overview

The E-Commerce Order Management System is a backend REST API built using FastAPI, SQLAlchemy, MySQL, Alembic, JWT authentication, and SMTP email notifications.

The system supports customer and admin roles with features for product management, cart management, order processing, payments, returns, refunds, reviews, email notifications, and admin reports.

---

## 🛠️ Technologies Used

- Python 3.12
- FastAPI
- Uvicorn
- SQLAlchemy
- MySQL
- PyMySQL
- Alembic
- Pydantic
- JWT Authentication
- Passlib
- Bcrypt
- Python-dotenv
- SMTP
- BackgroundTasks

---

## 📂 Project Structure

```text
ecommerce-order-management/
│
├── app/
│   ├── main.py
│   ├── database.py
│   │
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   ├── services/
│   ├── auth/
│   └── utils/
│
├── alembic/
├── alembic.ini
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md