from typing import Dict, Optional

from app.core.security import get_password_hash, verify_password
from app.models.user import User, UserCreate, UserInDB

# In-memory user database for simplicity
# In a production environment, this would be replaced with a database
fake_users_db: Dict[str, Dict] = {
    "admin": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "full_name": "Administrator",
        "hashed_password": get_password_hash("admin"),
        "is_active": True,
        "is_superuser": True,
    },
    "user": {
        "id": 2,
        "username": "user",
        "email": "user@example.com",
        "full_name": "Regular User",
        "hashed_password": get_password_hash("user"),
        "is_active": True,
        "is_superuser": False,
    },
}


def get_user_by_username(username: str) -> Optional[User]:
    """Get a user by username."""
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return User(**user_dict)
    return None


def get_user_by_email(email: str) -> Optional[User]:
    """Get a user by email."""
    for username, user_dict in fake_users_db.items():
        if user_dict.get("email") == email:
            return User(**user_dict)
    return None


def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate a user by username and password."""
    user = get_user_by_username(username)
    if not user:
        return None
    user_dict = fake_users_db[username]
    if not verify_password(password, user_dict.get("hashed_password")):
        return None
    return user


def create_user(user_create: UserCreate) -> User:
    """Create a new user."""
    # Check if user already exists
    if get_user_by_username(user_create.username) or get_user_by_email(user_create.email):
        return None
    
    # Create new user
    user_id = max(u["id"] for u in fake_users_db.values()) + 1
    user_dict = user_create.dict()
    hashed_password = get_password_hash(user_create.password)
    user_in_db = UserInDB(
        **user_dict,
        id=user_id,
        hashed_password=hashed_password,
    )
    
    # Add to database
    fake_users_db[user_create.username] = user_in_db.dict()
    
    return User(**user_in_db.dict())
