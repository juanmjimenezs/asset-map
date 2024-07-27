"""Assets module"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.errors import PyMongoError, OperationFailure, ConnectionFailure, InvalidOperation
from bson import ObjectId
from db.models.user import User
from db.models.asset import Asset, NewAsset, PortfolioItem
from db.schemas.asset import asset_schema, assets_schema
from db.client import db_client
from routers.helpers.users_helper import get_current_user
from routers.helpers.assets_helper import search_asset
from routers.helpers.helper import check_id

router = APIRouter(prefix="/asset",
                   tags=["asset"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})


@router.get("/", response_model=list[Asset])
async def assets(user: Annotated[User, Depends(get_current_user)],):
    """Get all assets for the user in session from the database"""
    return assets_schema(db_client.assets.find({"user_id": user.id}))


@router.get("/portfolio", response_model=list[PortfolioItem])
async def portfolio(user: Annotated[User, Depends(get_current_user)],):
    """Calculate the percentage of your portfolio for each asset"""
    assets_db = assets_schema(db_client.assets.find({"user_id": user.id}))
    # Total money in my portfolio
    total = sum(asset['shares']*asset['price'] for asset in assets_db)
    # Calculating the percentage by asset
    portfolio_items = []
    for asset in assets_db:
        portfolio_item = PortfolioItem()
        portfolio_item.mnemonic = asset['mnemonic']
        portfolio_item.percentage = (asset['shares']*asset['price']*100)/total
        portfolio_items.append(portfolio_item)

    return portfolio_items


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


@router.put("/", response_model=Asset)
async def update_user(asset: Asset, user: Annotated[User, Depends(get_current_user)]):
    """Update the asset from the database based on the Id"""
    check_id(asset.id) # Check if an Id is not a valid Id for ObjectId

    asset_dict = dict(asset)
    del asset_dict["id"]
    del asset_dict["user_id"]

    filters = {"_id": ObjectId(asset.id), "user_id": user.id}

    try:
        found = db_client.assets.update_one(filters, {"$set": asset_dict})
    except OperationFailure as e:
        return {"error": f"Database operation failed: {e}"}
    except ConnectionFailure as e:
        return {"error": f"Failed to connect to database: {e}"}
    except InvalidOperation as e:
        return {"error": f"Invalid database operation: {e}"}
    except PyMongoError as e:
        return {"error": f"Unexpected MongoDB error: {e}"}

    if found.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    return search_asset("_id", ObjectId(asset.id), user)


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(asset_id: str, user: Annotated[User, Depends(get_current_user)]):
    """Delete the asset from the database based on the Id"""
    check_id(asset_id) # Check if an Id is not a valid Id for ObjectId

    filters = {"_id": ObjectId(asset_id), "user_id": user.id}

    found = db_client.assets.find_one_and_delete(filters)

    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
