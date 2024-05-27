"""User model"""

from pydantic import BaseModel, Field

class User(BaseModel):
    """Class representing a user"""

    id: str = Field(default=None)
    username: str
    email: str
