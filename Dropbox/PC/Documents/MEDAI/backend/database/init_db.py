"""
MedAI - Database Initialization
Creates tables, seeds default users, and loads initial data.
"""

from backend.database.connection import engine, Base, SessionLocal
from backend.database.models import User, UserRole
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Default users to seed
DEFAULT_USERS = [
    {
        "username": "admin",
        "email": "admin@medai.com",
        "full_name": "System Administrator",
        "role": UserRole.ADMIN,
        "password": "admin123",
    },
    {
        "username": "dr.smith",
        "email": "dr.smith@medai.com",
        "full_name": "Dr. Sarah Smith",
        "role": UserRole.DOCTOR,
        "password": "doctor123",
    },
    {
        "username": "nurse.jones",
        "email": "nurse.jones@medai.com",
        "full_name": "Nurse Emily Jones",
        "role": UserRole.NURSE,
        "password": "nurse123",
    },
    {
        "username": "analyst.lee",
        "email": "analyst.lee@medai.com",
        "full_name": "David Lee",
        "role": UserRole.ANALYST,
        "password": "analyst123",
    },
]


def init_database():
    """Create all tables and seed default data."""
    print("[*] Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("[+] Database tables created successfully.")

    # Seed default users
    db = SessionLocal()
    try:
        existing_users = db.query(User).count()
        if existing_users == 0:
            print("[*] Seeding default users...")
            for user_data in DEFAULT_USERS:
                user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    full_name=user_data["full_name"],
                    role=user_data["role"],
                    hashed_password=pwd_context.hash(user_data["password"]),
                )
                db.add(user)
            db.commit()
            print(f"[+] Seeded {len(DEFAULT_USERS)} default users.")
        else:
            print(f"[i] {existing_users} users already exist, skipping seed.")
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
