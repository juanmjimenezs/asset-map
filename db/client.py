"""MongoDB client"""

import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import certifi

# Load environment variables from .env file
load_dotenv()

# Getting the MongoDB URI from the environment variable
mongo_uri = os.getenv("MONGO_URI")

# Create a MongoDB client (if there is no URI, use the default connection)
if not mongo_uri:
    db_client = MongoClient().asset_map
else:
    ca = certifi.where()
    db_client = MongoClient(mongo_uri, tlsCAFile=ca).asset_map

# Send a ping to confirm a successful connection
try:
    db_client.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except ConnectionFailure as e:
    print(f"Error connecting to MongoDB: {e}")
except OperationFailure as e:
    print(f"Error executing ping command on MongoDB: {e}")
