from passlib.context import CryptContext
from dotenv import load_dotenv
import os
from fastapi.security import OAuth2PasswordBearer

load_dotenv()

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ.get("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

bcrypt_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="bcrypt")
oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login-form")
