"""
User Repository

Data access layer for User entity.
Contains all database queries related to users.
This layer ONLY talks to SQLAlchemy, no business logic here.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.logging import get_logger


logger = get_logger(__name__)


class UserRepository:
    """
    Repository for User database operations.
    
    All methods accept a Session and perform atomic operations.
    No business logic should be placed here.
    """
    
    def __init__(self, db: Session):
        """
        Initialize repository with database session.
        
        Args:
            db: SQLAlchemy session instance
        """
        self.db = db
    
    def create(self, email: str, password_hash: str) -> User:
        """
        Create a new user in the database.
        
        Args:
            email: User's email address
            password_hash: Already hashed password
            
        Returns:
            Created User instance
        """
        user = User(
            email=email,
            password_hash=password_hash
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"Created user with id={user.id}")
        return user
    
    def get_by_id(self, user_id: int) -> User | None:
        """
        Retrieve a user by their ID.
        
        Args:
            user_id: User's primary key
            
        Returns:
            User if found, None otherwise
        """
        stmt = select(User).where(User.id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()
    
    def get_by_email(self, email: str) -> User | None:
        """
        Retrieve a user by their email address.
        
        Args:
            email: User's email address
            
        Returns:
            User if found, None otherwise
        """
        stmt = select(User).where(User.email == email)
        return self.db.execute(stmt).scalar_one_or_none()
    
    def exists_by_email(self, email: str) -> bool:
        """
        Check if a user with the given email exists.
        
        Args:
            email: Email address to check
            
        Returns:
            True if user exists, False otherwise
        """
        stmt = select(User.id).where(User.email == email)
        result = self.db.execute(stmt).scalar_one_or_none()
        return result is not None
