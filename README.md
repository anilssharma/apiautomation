# Order Management API
This FastAPI service reads order status history from Microsoft SQL Server through SQLAlchemy and `pyodbc`. Each record includes its order number, user ID, status, and UTC change time.

## Requirements

- Python 3.9 or newer
- Microsoft SQL Server and Microsoft ODBC Driver 18 for SQL Server

## Create the database

In SQL Server Management Studio, create or select the `OrderManagement` database. Open and execute these scripts in order:

1. `sql/001_create_tables_mssql.sql`
2. `sql/002_seed_sample_data_mssql.sql`

The schema script creates the tables, constraints, and indexes if they do not already exist. The seed script inserts four orders and twelve status events and can be rerun safely.

## Install and run (Windows PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install ".[test]"
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

The database URL is read from the project-root `.env` file. Edit `ORDER_API_DATABASE_URL` there to replace `localhost` with your SQL Server instance name. The example uses Windows integrated authentication. SQL authentication is also supported; URL-encode reserved characters in credentials. Keep `.env` local and do not commit credentials. The API is available at `http://127.0.0.1:8000`, with interactive documentation at `http://127.0.0.1:8000/docs`.
The API logs startup/shutdown, request method, response status, and elapsed time to the console without logging request paths or credentials. The API is available at `http://127.0.0.1:8000`, with interactive documentation at `http://127.0.0.1:8000/docs`.

The API creates missing tables on startup. For an existing database, it leaves existing tables unchanged. To load the sample records through the Python helper instead of executing the seed SQL in SSMS, run `python -m scripts.seed_sample_data`; it reads the same `.env` file.

## Endpoints

All list endpoints accept `limit` (default 100, maximum 500) and `offset` (default 0). Responses contain `items`, the filtered `total`, and the pagination values. Results are ordered by status change time.

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/v1/order-statuses` | All order status history |
| GET | `/api/v1/orders/{order_number}/statuses` | Status history for an order; returns 404 if the order does not exist |
| GET | `/api/v1/users/{user_id}/order-statuses` | Status history for all orders belonging to a user |
| GET | `/api/v1/order-statuses/by-date-range?start_date=2026-06-01&end_date=2026-06-03` | Status history changed during the inclusive UTC calendar-date range |

The supported statuses are `PENDING`, `PROCESSING`, `SHIPPED`, `DELIVERED`, `CANCELLED`, and `RETURNED`.

## API automation tests

The pytest suite uses FastAPI's `TestClient` and an isolated SQLite database through the same SQLAlchemy models, so tests do not require a running SQL Server instance:
The pytest suite uses FastAPI's `TestClient` and an isolated SQLite database through the same SQLAlchemy models, so tests do not require a running SQL Server instance. `pytest` prints each test's progress and a final pass/fail summary to the console:

```powershell
python -m pip install ".[test]"
python -m pytest
```