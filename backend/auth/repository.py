from typing import Optional, Dict, Any
from datetime import datetime
from backend.database import db

# Thread-safe fallback user store
IN_MEMORY_USERS: Dict[str, Dict[str, Any]] = {}

class UserRepository:
    @staticmethod
    async def create_user(user_data: Dict[str, Any]) -> bool:
        user_data["created_at"] = datetime.utcnow().isoformat()
        username = user_data["username"]
        
        if db.is_mongodb_active:
            try:
                await db.db.users.insert_one(user_data)
                return True
            except Exception:
                # Log warning and fallback
                pass
        
        IN_MEMORY_USERS[username] = user_data
        return True

    @staticmethod
    async def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
        if db.is_mongodb_active:
            try:
                return await db.db.users.find_one({"username": username})
            except Exception:
                pass
        return IN_MEMORY_USERS.get(username)

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        if db.is_mongodb_active:
            try:
                return await db.db.users.find_one({"email": email})
            except Exception:
                pass
        for u in IN_MEMORY_USERS.values():
            if u.get("email") == email:
                return u
        return None
