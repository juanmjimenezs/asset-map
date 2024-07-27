"""Asset model"""

from pydantic import BaseModel, Field


class NewAsset(BaseModel):
    """Class representing a new asset"""

    mnemonic: str
    price: float
    shares: int


class Asset(NewAsset):
    """Class representing an asset"""

    id: str = Field(default=None)
    user_id: str = Field(default=None)
    mnemonic: str
    price: float
    shares: int


class PortfolioItem(BaseModel):
    """Class representing a portfolio item"""

    mnemonic: str = Field(default=None)
    percentage: float = Field(default=None)
