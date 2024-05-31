# Clase en vídeo: https://youtu.be/_y9qQZXE24A?t=20480

### Users DB API ###

from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from pymongo.errors import PyMongoError, OperationFailure, ConnectionFailure, InvalidOperation
from passlib.context import CryptContext
from db.models.user import User, UserDB, PasswordUpdateRequest
from db.schemas.user import user_schema, users_schema
from db.client import db_client

router = APIRouter(prefix="/user",
                   tags=["user"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})

crypt = CryptContext(schemes=["bcrypt"])


@router.get("/", response_model=list[User])
async def users():
    """Get all users from the database"""
    return users_schema(db_client.users.find())


@router.get("/{user_id}")  # Path
async def get_user(user_id: str):
    """Get the user from the database based on the Id"""
    check_id(user_id)

    return search_user("_id", ObjectId(user_id))


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def save_user(user: UserDB):
    """Saving a new user in the database if the email is unique"""

    if isinstance(search_user("email", user.email), User):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user exists, please choose another email.")

    user_dict = dict(user)
    del user_dict["id"]
    # Encrypt the password
    user_dict["password"] = crypt.hash(user_dict["password"])

    inserted_id = db_client.users.insert_one(user_dict).inserted_id

    new_user = user_schema(db_client.users.find_one({"_id": inserted_id}))

    return User(**new_user)


@router.put("/", response_model=User)
async def update_user(user: User):
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
async def update_password(user_id: str, request: PasswordUpdateRequest):
    """Update the password from the database based on the Id"""
    check_id(user_id) # Check if an Id is not a valid Id for ObjectId

    # The data I want to update
    user_dict = {
        "password": crypt.hash(request.password)
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


@router.delete("/{id_user}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id_user: str):
    """Delete the user from the database based on the Id"""
    found = db_client.users.find_one_and_delete({"_id": ObjectId(id_user)})

    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


# Helper

def search_user(field: str, key):
    """Search a user in the database"""
    try:
        found = db_client.users.find_one({field: key})

        if not found:
            return None

        return User(**user_schema(found))
    except OperationFailure as e:
        return {"error": f"Database operation failed: {e}"}
    except ConnectionFailure as e:
        return {"error": f"Failed to connect to database: {e}"}
    except InvalidOperation as e:
        return {"error": f"Invalid database operation: {e}"}
    except PyMongoError as e:
        return {"error": f"Unexpected MongoDB error: {e}"}


def check_id(user_id: str):
    """Check if an Id is not a valid Id for ObjectId"""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The ID does not exist.")
