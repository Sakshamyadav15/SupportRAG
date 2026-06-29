"""
Auth Service

Business logic for authentication operations.
This service orchestrates repositories and does NOT know about FastAPI.
"""

from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.core.logging import get_logger


logger = get_logger(__name__)


class AuthServiceError(Exception):
    """Base exception for auth service errors."""
    pass


class EmailAlreadyExistsError(AuthServiceError):
    """Raised when trying to register with an existing email."""
    pass


class InvalidCredentialsError(AuthServiceError):
    """Raised when login credentials are invalid."""
    pass


class AuthService:
    """
    Service layer for authentication operations.
    
    Contains business logic for:
    - User registration
    - User login
    - Token generation
    
    This service is framework-agnostic and only uses repositories.
    """
    
    def __init__(self, user_repository: UserRepository):
        """
        Initialize auth service with required repositories.
        
        Args:
            user_repository: Repository for user database operations
        """
        self.user_repository = user_repository
    
    def register_user(self, email: str, password: str) -> User:
        """
        Register a new user.
        
        Business rules:
        - Email must be unique
        - Password is hashed before storage
        
        Args:
            email: User's email address
            password: Plain text password
            
        Returns:
            Created User instance
            
        Raises:
            EmailAlreadyExistsError: If email is already registered
        """
        # Check if email already exists
        if self.user_repository.exists_by_email(email):
            logger.warning(f"Registration attempt with existing email: {email}")
            raise EmailAlreadyExistsError(f"Email '{email}' is already registered")
        
        # Hash the password
        password_hash = hash_password(password)
        
        # Create user via repository
        user = self.user_repository.create(
            email=email,
            password_hash=password_hash
        )
        
        logger.info(f"User registered successfully: id={user.id}")
        return user
    
    def authenticate_user(self, email: str, password: str) -> str:
        """
        Authenticate a user and return a JWT token.
        
        Business rules:
        - User must exist
        - Password must match
        
        Args:
            email: User's email address
            password: Plain text password
            
        Returns:
            JWT access token string
            
        Raises:
            InvalidCredentialsError: If credentials are invalid
        """
        # Find user by email
        user = self.user_repository.get_by_email(email)
        
        if user is None:
            logger.warning(f"Login attempt for non-existent email: {email}")
            raise InvalidCredentialsError("Invalid email or password")
        
        # Verify password
        if not verify_password(password, user.password_hash):
            logger.warning(f"Failed login attempt for user: id={user.id}")
            raise InvalidCredentialsError("Invalid email or password")
        
        # Generate JWT token
        # The 'sub' claim contains the user ID as string (JWT standard)
        token = create_access_token(data={"sub": str(user.id)})
        
        logger.info(f"User authenticated successfully: id={user.id}")
        return token
    
    def get_user_by_id(self, user_id: int) -> User | None:
        """
        Retrieve a user by their ID.
        
        Used for getting current user from JWT token.
        
        Args:
            user_id: User's ID from JWT
            
        Returns:
            User if found, None otherwise
        """
        return self.user_repository.get_by_id(user_id)
