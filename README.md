# Expense Tracker API

A Django REST Framework backend that allows multiple users to track their expenses.

## Features
- User registration & login (JWT authentication)
- CRUD operations for expenses
- Filters: date range, category, amount range
- Pagination & sorting
- Monthly expense summary per user
- Unit tests included

## Tech Stack
- Python 3.11
- Django REST Framework
- PostgreSQL
- JWT Authentication (SimpleJWT)

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/<your-username>/expense-tracker-api.git
cd expensr
pip install -r requirements.txt

```
### 2. Configure environment variables in .env file
```bash
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=your-db-name
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432
```
### To generate a new secret key for Django:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
### 3. Run migrations
```bash
python manage.py migrate
```
### 4. Run Server
```bash
Start the server
```
