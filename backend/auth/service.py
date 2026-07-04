import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional

# Configuration parameters
JWT_SECRET = "placement-preparation-agent-super-secret-key-123!"
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 600  # 10 Hours session lifetime

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False

    @staticmethod
    def generate_token(username: str, email: str, fullname: str) -> str:
        payload = {
            "sub": username,
            "email": email,
            "name": fullname,
            "exp": datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None
