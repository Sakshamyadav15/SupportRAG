"""
Auth Routes

API endpoints for authentication (register, login).
This layer handles HTTP parsing, validation, and response formatting.
Business logic is delegated to AuthService.
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    TokenResponse,
)
from app.services.auth_service import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
)
from app.dependencies import AuthSvc


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password."
)
def register(
    request: RegisterRequest,
    auth_service: AuthSvc
) -> RegisterResponse:
    """
    Register a new user.
    
    - **email**: Valid email address (must be unique)
    - **password**: Password (min 8 characters)
    """
    try:
        user = auth_service.register_user(
            email=request.email,
            password=request.password
        )
        
        return RegisterResponse(
            id=user.id,
            email=user.email,
            message="User registered successfully"
        )
        
    except EmailAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and get access token",
    description="Authenticate with email and password to receive JWT token."
)
def login(
    request: LoginRequest,
    auth_service: AuthSvc
) -> TokenResponse:
    """
    Authenticate user and return JWT access token.
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns JWT token that must be included in Authorization header
    for protected endpoints.
    """
    try:
        token = auth_service.authenticate_user(
            email=request.email,
            password=request.password
        )
        
        return TokenResponse(
            access_token=token,
            token_type="bearer"
        )
        
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
