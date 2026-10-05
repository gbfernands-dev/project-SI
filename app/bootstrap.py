"""Provisionamento idempotente das contas administrativas configuradas."""
import os
from collections.abc import Mapping

from app.database import SessionLocal
from app.models import AdminScope, Role, Session as UserSession, User
from app.security import hash_password, verify_password


ADMIN_ACCOUNT_VARIABLES = (
    ("ADMIN_EMAIL", "ADMIN_PASSWORD", "Administrador do site", AdminScope.SITE),
    ("ATHLETICS_ADMIN_EMAIL", "ATHLETICS_ADMIN_PASSWORD", "Administrador da atlética", AdminScope.ATHLETICS),
)


def provision_admin_accounts(db, environment: Mapping[str, str] | None = None) -> int:
    values = os.environ if environment is None else environment
    configured_accounts = []
    for email_key, password_key, name, scope in ADMIN_ACCOUNT_VARIABLES:
        email = values.get(email_key, "").strip().lower()
        password = values.get(password_key, "")
        if bool(email) != bool(password):
            raise RuntimeError(f"Defina {email_key} e {password_key} em conjunto.")
        if not email:
            continue
        if len(password) < 8:
            raise RuntimeError(f"{password_key} deve ter pelo menos oito caracteres.")
        configured_accounts.append((name, email, password, scope))

    for name, email, password, scope in configured_accounts:
        user = db.query(User).filter(User.email == email.lower()).first()
        credentials_changed = False
        if user:
            if user.role != Role.ADMIN or user.admin_scope != scope or user.name != name:
                user.role = Role.ADMIN
                user.admin_scope = scope
                user.name = name
                credentials_changed = True
            try:
                password_matches = verify_password(password, user.password_hash)
            except (TypeError, ValueError):
                password_matches = False
            if not password_matches:
                user.password_hash = hash_password(password)
                credentials_changed = True
        else:
            user = User(
                name=name,
                email=email,
                password_hash=hash_password(password),
                role=Role.ADMIN,
                admin_scope=scope,
            )
            db.add(user)
            db.flush()
            credentials_changed = True
        if credentials_changed:
            db.query(UserSession).filter(UserSession.user_id == user.id).delete(synchronize_session=False)
    db.commit()
    return len(configured_accounts)


def main() -> None:
    db = SessionLocal()
    try:
        if provision_admin_accounts(db) == 0:
            raise SystemExit("Defina ao menos uma conta administrativa antes de executar o bootstrap.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
