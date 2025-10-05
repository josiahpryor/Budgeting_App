from fastapi import FastAPI
from . import models
from .database import engine
from app.routers import auth

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Budgeting App Backend")

app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Budgeting App API running"}


from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.auth_utils import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise Exception("Invalid token")
        return user_id
    except JWTError:
        raise Exception("Invalid token")

@app.get("/protected")
def protected_route(current_user: str = Depends(get_current_user)):
    return {"message": f"Hello User {current_user}, you accessed a protected route!"}