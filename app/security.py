from datetime import UTC, timedelta
import hashlib
import secrets

from fastapi import Depends, Header, HTTPException, Request, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Role, Session as UserSession, User, now_utc


PASSWORDS = CryptContext(schemes=["bcrypt"], deprecated="auto")
SESSION_COOKIE = "godzilla_session"
SESSION_DAYS = 7


def hash_password(password: str) -> str:
    return PASSWORDS.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return PASSWORDS.verify(password, password_hash)


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def create_session(db: Session, user: User) -> tuple[str, UserSession]:
    token = secrets.token_urlsafe(48)
    session = UserSession(
        user_id=user.id,
        token_hash=digest(token),
        csrf_token=secrets.token_urlsafe(32),
        expires_at=now_utc() + timedelta(days=SESSION_DAYS),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return token, session


def get_current_session(request: Request, db: Session = Depends(get_db)) -> UserSession:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Autenticação necessária.")
    session = db.query(UserSession).filter(UserSession.token_hash == digest(token)).first()
    expires_at = session.expires_at.replace(tzinfo=UTC) if session and session.expires_at.tzinfo is None else session.expires_at
    if not session or expires_at < now_utc():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessão expirada.")
    return session


def get_current_user(session: UserSession = Depends(get_current_session), db: Session = Depends(get_db)) -> User:
    user = db.get(User, session.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado.")
    return user


def verify_csrf(
    x_csrf_token: str | None = Header(default=None),
    session: UserSession = Depends(get_current_session),
) -> UserSession:
    if not x_csrf_token or not secrets.compare_digest(x_csrf_token, session.csrf_token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token CSRF inválido.")
    return session


def require_user(
    _: UserSession = Depends(verify_csrf), db: Session = Depends(get_db)
) -> User:
    user = db.get(User, _.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado.")
    return user


def require_admin(user: User = Depends(require_user)) -> User:
    if user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso administrativo necessário.")
    return user
