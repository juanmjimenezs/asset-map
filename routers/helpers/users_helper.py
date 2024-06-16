"""Users helper"""

from typing import Annotated
import os
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from bson import ObjectId
import jwt
from jwt.exceptions import InvalidTokenError, DecodeError
from pymongo.errors import PyMongoError, OperationFailure, ConnectionFailure, InvalidOperation
from passlib.context import CryptContext
from db.models.user import User, UserDB
from db.schemas.user import user_schema, user_db_schema
from db.client import db_client

# Load environment variables from .env file
load_dotenv()
secret_key = os.getenv("SECRET_KEY")
algorithm = os.getenv("ALGORITHM")
access_token_duration = int(os.getenv("ACCESS_TOKEN_DURATION"))

router = APIRouter(prefix="/user",
                   tags=["user"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """This method check if the user is authenticated"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"})

    try:
        username = jwt.decode(token, secret_key, algorithms=[algorithm]).get("sub")
        if username is None:
            raise credentials_exception
    except DecodeError as exc:
        raise credentials_exception from exc
    except InvalidTokenError as exc:
        raise credentials_exception from exc

    user = search_user("username", username)
    if user is None:
        raise credentials_exception

    return user


def search_user(field: str, key, with_id=False):
    """Search a user in the database"""
    try:
        found = db_client.users.find_one({field: key})

        if not found:
            return None

        if with_id:
            return UserDB(**user_db_schema(found))

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
