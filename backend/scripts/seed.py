from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import Subscription, User

db = SessionLocal()
try:
    email = "demo@example.com"
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, full_name="Demo User", hashed_password=hash_password("ChangeMe123!"))
        db.add(user); db.flush(); db.add(Subscription(user_id=user.id)); db.commit()
    print(f"Seeded {email} / ChangeMe123!")
finally:
    db.close()
