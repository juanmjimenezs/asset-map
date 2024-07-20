"""Assets helper"""

from pymongo.errors import PyMongoError, OperationFailure, ConnectionFailure, InvalidOperation
from db.models.asset import Asset
from db.models.user import User
from db.schemas.asset import asset_schema
from db.client import db_client


def search_asset(field: str, key: str, user: User):
    """Search an asset in the database, it should be from the same user"""
    try:
        found = db_client.assets.find_one({field: key, "user_id": user.id})

        if not found:
            return None

        return Asset(**asset_schema(found))
    except OperationFailure as e:
        return {"error": f"Database operation failed: {e}"}
    except ConnectionFailure as e:
        return {"error": f"Failed to connect to database: {e}"}
    except InvalidOperation as e:
        return {"error": f"Invalid database operation: {e}"}
    except PyMongoError as e:
        return {"error": f"Unexpected MongoDB error: {e}"}
