"""Asset model"""

from pydantic import BaseModel, Field

class Asset(BaseModel):
    """Class representing an asset"""

    id: str = Field(default=None)
    user_id: str = Field(default=None)
    mnemonic: str
    price: float
    shares: int


class NewAsset(Asset):
    """Class representing a new asset"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # Initialize the attributes of the base class
        del self.id  # Remove the attribute that we do not want to inherit (It's because a new user don't have id)
