from fastapi import APIRouter
from backend.auth.models import RegisterRequest, LoginRequest
from backend.auth.controller import AuthController

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register")
async def register(payload: RegisterRequest):
    return await AuthController.register(payload)

@router.post("/login")
async def login(payload: LoginRequest):
    return await AuthController.login(payload)
