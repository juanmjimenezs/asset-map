"""
The main entry point to use AssetMap

Some important notes:
- Local url: http://127.0.0.1:8000
- Running server: python3 -m uvicorn main:app --reload
- Stop server: CTRL+C
- Swagger doc: http://127.0.0.1:8000/docs
- Redocly doc: http://127.0.0.1:8000/redoc
"""

from fastapi import FastAPI
from routers import users, assets

app = FastAPI()
app.include_router(users.router)
app.include_router(assets.router)

@app.get("/")
async def root():
    """The root of the API"""

    return {"message": "Hi AssetMap 2024!"}
