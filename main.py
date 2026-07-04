from fastapi import FastAPI
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
from fastapi.security import OAuth2PasswordBearer

load_dotenv()

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ.get("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

app = FastAPI()

bcrypt_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="bcrypt")
oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login-form")

from auth_routes import auth_router
from order_routes import order_router

app.include_router(auth_router)
app.include_router(order_router)
