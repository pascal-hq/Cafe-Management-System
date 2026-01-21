# create_admin.py
from app.database import SessionLocal
from app.models import User
from app.auth import hash_password

def create_admin():
    db = SessionLocal()

    # Remove old admin if it exists
    old_admin = db.query(User).filter(User.username == "admin").first()
    if old_admin:
        db.delete(old_admin)
        db.commit()

    # Create a new admin user
    admin = User(
        username="admin",
        password_hash=hash_password("admin123"),  # hashed with argon2
        role="admin"
    )
    db.add(admin)
    db.commit()
    db.close()

    print("✅ Admin user created successfully!")
    print("Username: admin")
    print("Password: admin123")

if __name__ == "__main__":
    create_admin()
