"""Comando seguro para provisionar a primeira conta administrativa."""
import os

from app.database import Base, SessionLocal, engine
from app.models import Role, User
from app.security import hash_password


def main() -> None:
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")
    if not email or not password:
        raise SystemExit("Defina ADMIN_EMAIL e ADMIN_PASSWORD antes de executar o bootstrap.")
    if len(password) < 8:
        raise SystemExit("ADMIN_PASSWORD deve ter pelo menos oito caracteres.")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email.lower()).first()
        if user:
            user.role = Role.ADMIN
            user.password_hash = hash_password(password)
            print(f"Conta existente promovida a administradora: {email}")
        else:
            db.add(User(name="Administrador Godzilla", email=email.lower(), password_hash=hash_password(password), role=Role.ADMIN))
            print(f"Conta administradora criada: {email}")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()
