"""Users module"""

from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from bson import ObjectId
import jwt
from pymongo.errors import PyMongoError, OperationFailure, ConnectionFailure, InvalidOperation
from db.models.user import User, NewUser, PasswordUpdateRequest
from db.schemas.user import user_schema, users_schema
from db.client import db_client
from routers.helpers.users_helper import secret_key, algorithm, access_token_duration, pwd_context
from routers.helpers.users_helper import get_current_user, search_user, check_id

router = APIRouter(prefix="/user",
                   tags=["user"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})


@router.get("/", response_model=list[User])
async def users(_: Annotated[User, Depends(get_current_user)],):
    """Get all users from the database"""
    return users_schema(db_client.users.find())


@router.get("/{user_id}")  # Path
async def get_user(user_id: str, _: Annotated[User, Depends(get_current_user)]):
    """Get the user from the database based on the Id"""
    check_id(user_id)

    return search_user("_id", ObjectId(user_id))


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def save_user(user: NewUser):
    """Saving a new user in the database if the email is unique,
       it's not necesary to be authenticated"""

    if isinstance(search_user("email", user.email), User):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user exists, please choose another email.")

    user_dict = dict(user)

    # Encrypt the password
    user_dict["password"] = pwd_context.hash(user_dict["password"])

    inserted_id = db_client.users.insert_one(user_dict).inserted_id

    new_user = user_schema(db_client.users.find_one({"_id": inserted_id}))

    return User(**new_user)


@router.put("/", response_model=User)
async def update_user(user: User, _: Annotated[User, Depends(get_current_user)]):
    """Update the user from the database based on the Id"""
    check_id(user.id) # Check if an Id is not a valid Id for ObjectId

    user_dict = dict(user)
    del user_dict["id"]

    try:
        found = db_client.users.update_one({"_id": ObjectId(user.id)}, {"$set": user_dict})
    except OperationFailure as e:
        return {"error": f"Database operation failed: {e}"}
    except ConnectionFailure as e:
        return {"error": f"Failed to connect to database: {e}"}
    except InvalidOperation as e:
        return {"error": f"Invalid database operation: {e}"}
    except PyMongoError as e:
        return {"error": f"Unexpected MongoDB error: {e}"}

    if found.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return search_user("_id", ObjectId(user.id))


@router.patch("/password/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_password(user_id: str, request: PasswordUpdateRequest, _: Annotated[User, Depends(get_current_user)]):
    """Update the password from the database based on the Id"""
    check_id(user_id) # Check if an Id is not a valid Id for ObjectId

    # The data I want to update
    user_dict = {
        "password": pwd_context.hash(request.password)
    }

    try:
        found = db_client.users.update_one({"_id": ObjectId(user_id)}, {"$set": user_dict})
    except OperationFailure as e:
        return {"error": f"Database operation failed: {e}"}
    except ConnectionFailure as e:
        return {"error": f"Failed to connect to database: {e}"}
    except InvalidOperation as e:
        return {"error": f"Invalid database operation: {e}"}
    except PyMongoError as e:
        return {"error": f"Unexpected MongoDB error: {e}"}

    if found.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, _: Annotated[User, Depends(get_current_user)]):
    """Delete the user from the database based on the Id"""
    check_id(user_id) # Check if an Id is not a valid Id for ObjectId

    found = db_client.users.find_one_and_delete({"_id": ObjectId(user_id)})

    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@router.post("/login")
async def login(form: Annotated[OAuth2PasswordRequestForm, Depends()],):
    """This method allow you to login in the app"""
    user = search_user("username", form.username, True)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username is incorrect")

    if not pwd_context.verify(form.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Please verify your credentials")

    access_token = {"sub": user.username,
                    "exp": datetime.now(timezone.utc) + timedelta(minutes=access_token_duration)}

    return {
        "access_token": jwt.encode(access_token, secret_key, algorithm=algorithm),
        "token_type": "bearer"
    }
