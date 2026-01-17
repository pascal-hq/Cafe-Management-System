# seed.py
from app.database import SessionLocal
from app import models, auth

def seed():
    db = SessionLocal()

    admin = models.User(
        username="admin",
        password_hash=auth.hash_password("admin123"),
        role="admin"
    )

    db.add(admin)
    db.commit()
    db.close()

    print("✅ Database seeded successfully")

if __name__ == "__main__":
    seed()
