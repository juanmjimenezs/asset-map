"""Testing all User module endpoints"""

from fastapi.testclient import TestClient
from main import app
from db.models.user import User
from db.client import db_client
from db.schemas.user import user_schema
from routers.helpers.users_helper import pwd_context
from bson import ObjectId

client = TestClient(app)

user_dict = {
    "username": "juanma_test",
    "email": "juanma_test@gmail.com",
    "password": "juamma_test"
}

def test_user_list_not_authenticated():
    """
    Test case to verify that an unauthenticated user cannot access the user list endpoint.
    """
    response = client.get("/user/")
    assert response.status_code == 401
    assert response.json() == {'detail': 'Not authenticated'}

    token = "my_test_bearer_token"
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/user/", headers=headers)
    assert response.status_code == 401
    assert response.json() == {'detail': 'Invalid authentication credentials'}

def test_user_login_without_credentials():
    """
    Test case to verify that you can't login without valid credentials.
    """
    response = client.post("/user/login")
    assert response.status_code == 422
    assert response.json()['detail'][0]['msg'] == 'Field required'

def test_user_login_with_wrong_credentials():
    """
    Test case to verify that you can't login with invalid credentials.
    """
    login_data = {
        "username": "test_user",
        "password": "test_password"
    }
    response = client.post("/user/login", data=login_data)

    assert response.status_code == 400
    assert response.json() == {'detail': 'Username is incorrect'}

def test_user_login():
    """
    Test case to verify that login works.
    """
    #Inserting a user to use in the test
    save_user(user_dict)

    login_data = {
        "username": user_dict['username'],
        "password": user_dict['password']
    }
    response = client.post("/user/login", data=login_data)

    assert response.status_code == 200
    assert response.json()['access_token']
    assert response.json()['token_type'] == 'bearer'
    #Cleaning up
    delete_user(user_dict)

# HELPER #

def save_user(user: dict):
    """Saving a new user in the database to use in tests"""

    new_user = user.copy()
    # Encrypt the password
    new_user["password"] = pwd_context.hash(new_user["password"])

    inserted_id = db_client.users.insert_one(new_user).inserted_id

    new_user = user_schema(db_client.users.find_one({"_id": inserted_id}))

    return User(**new_user)

def delete_user(user: dict):
    """Deleting a user from the database after using it in tests"""

    result = db_client.users.delete_one({"username": user['username']})

    return result.deleted_count
