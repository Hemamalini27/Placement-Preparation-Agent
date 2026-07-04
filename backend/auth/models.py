from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    fullname: str = Field(..., min_length=2, example="John Doe")
    username: str = Field(..., min_length=3, example="johndoe")
    email: EmailStr = Field(..., example="johndoe@example.com")
    password: str = Field(..., min_length=8, example="securepassword123")

class LoginRequest(BaseModel):
    username: str = Field(..., example="johndoe")
    password: str = Field(..., example="securepassword123")

class TokenResponse(BaseModel):
    token: str
    username: str
    fullname: str
