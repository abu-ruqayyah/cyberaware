import os
from app import create_app
from run import seed_database

app = create_app()

# Initialize database schema and pre-seed initial admin data in production
try:
    seed_database()
except Exception as e:
    print(f"Database initialization notice: {e}")

if __name__ == "__main__":
    app.run()
