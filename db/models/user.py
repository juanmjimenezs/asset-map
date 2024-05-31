"""User model"""

from pydantic import BaseModel, Field

class User(BaseModel):
    """Class representing a user"""

    id: str = Field(default=None)
    username: str
    email: str


class UserDB(User):
    """Class representing a user in the database"""

    password: str


class PasswordUpdateRequest(BaseModel):
    """Class representing a password in database"""

    password: str
