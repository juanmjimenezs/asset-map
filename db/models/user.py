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


class NewUser(UserDB):
    """Class representing a new user"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # Initialize the attributes of the base class
        del self.id  # Remove the attribute that we do not want to inherit (It's because a new user don't have id)


class PasswordUpdateRequest(BaseModel):
    """Class representing a password in database"""

    password: str
