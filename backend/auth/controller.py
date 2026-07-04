from fastapi import HTTPException
from backend.auth.models import RegisterRequest, LoginRequest
from backend.auth.repository import UserRepository
from backend.auth.service import AuthService

class AuthController:
    @staticmethod
    async def register(payload: RegisterRequest) -> dict:
        # Check duplicate username
        existing_username = await UserRepository.get_user_by_username(payload.username)
        if existing_username:
            raise HTTPException(status_code=400, detail="Username is already taken.")

        # Check duplicate email
        existing_email = await UserRepository.get_user_by_email(payload.email)
        if existing_email:
            raise HTTPException(status_code=400, detail="Email is already registered.")

        # Hash and store user
        password_hash = AuthService.hash_password(payload.password)
        user_data = {
            "fullname": payload.fullname,
            "username": payload.username,
            "email": payload.email,
            "password_hash": password_hash
        }
        
        success = await UserRepository.create_user(user_data)
        if not success:
            raise HTTPException(status_code=500, detail="Error creating user profile.")
        
        # Issue direct login token on successful signup for better user experience
        token = AuthService.generate_token(payload.username, payload.email, payload.fullname)
        return {
            "token": token,
            "username": payload.username,
            "fullname": payload.fullname
        }

    @staticmethod
    async def login(payload: LoginRequest) -> dict:
        # Retrieve user profile
        user = await UserRepository.get_user_by_username(payload.username)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid username or password.")

        # Verify bcrypt signature
        is_valid = AuthService.verify_password(payload.password, user.get("password_hash", ""))
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid username or password.")

        # Generate session token
        token = AuthService.generate_token(user["username"], user["email"], user.get("fullname", user["username"]))
        return {
            "token": token,
            "username": user["username"],
            "fullname": user.get("fullname", user["username"])
        }
