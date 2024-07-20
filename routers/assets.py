"""Assets module"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from db.models.user import User
from db.models.asset import Asset, NewAsset
from db.schemas.asset import asset_schema, assets_schema
from db.client import db_client
from routers.helpers.users_helper import get_current_user
from routers.helpers.assets_helper import search_asset

router = APIRouter(prefix="/asset",
                   tags=["asset"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})


@router.get("/", response_model=list[Asset])
async def assets(user: Annotated[User, Depends(get_current_user)],):
    """Get all assets for the user in session from the database"""
    return assets_schema(db_client.assets.find({"user_id": user.id}))

@router.post("/", response_model=Asset, status_code=status.HTTP_201_CREATED)
async def save_asset(asset: NewAsset, user: Annotated[User, Depends(get_current_user)],):
    """Saving a new asset in the database if the mnemonic is unique"""

    if isinstance(search_asset("mnemonic", asset.mnemonic, user), Asset):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The asset exists, please choose another mnemonic.")

    asset_dict = dict(asset)

    # Adding the user id to the asset dict
    asset_dict["user_id"] = user.id

    inserted_id = db_client.assets.insert_one(asset_dict).inserted_id

    new_asset = asset_schema(db_client.assets.find_one({"_id": inserted_id}))

    return Asset(**new_asset)
