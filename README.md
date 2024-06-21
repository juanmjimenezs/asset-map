# Asset-map
Asset-map is an API built with Python (3.12.3) and FastAPI (0.111.0) that allows users to visualize and analyze the diversification of their investment portfolios. The database used is MongoDB.

## Features

- **User Authentication**: Secure user authentication system implemented using OAuth2PasswordBearer and JSON Web Tokens (JWT) to protect sensitive data and endpoints.
- **Asset Management**: Add, update, and remove assets from your portfolio, tracking their performance and contribution to your overall investment strategy.

## Technologies Used

- **Python**: The application is written in Python, a versatile and powerful programming language.
- **FastAPI**: A modern, fast (high-performance), web framework for building APIs with Python.
- **PyMongo**: PyMongo is a Python distribution containing tools for working with MongoDB.
- **OAuth2PasswordBearer**: A security scheme for authenticating users and protecting endpoints.
- **JWT (JSON Web Tokens)**: Used for securely transmitting information between parties as a JSON object, enabling user authentication and authorization.

## Getting Started
After clone the repository you need to clone the ***.env.example*** file and rename it as ***.env*** and update the values for the variables there. The variables you will find here are:
1. **MONGO_URI**: this is the URI from the server where your Database is located. I used *Atlas* from MongoDB cloud.
2. **SECRET_KEY**: this is the key you will use to encode or decode your access token.
3. **ALGORITHM**: this is the algorihm used, maybe you don't have to change this value.
4. **ACCESS_TOKEN_DURATION**: how long do you want the session to be alive?

After you finish with *.env* file, you need to install all packages on *requirements.txt* file.

Now you can **uvicorn** web server to start using the endpoints:
```bash
python3 -m uvicorn main:app --reload
```

**API documentation**:
- Swagger doc: http://127.0.0.1:8000/docs
- Redocly doc: http://127.0.0.1:8000/redoc