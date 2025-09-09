from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from to_do_app.database import SessionLocal
from to_do_app.models import Users
from passlib.context import CryptContext
from sqlalchemy.orm import Session # type: ignore
from starlette import status
from  fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt, JWTError

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = '9f82e34b1d8e4c61a3d9bb47f2c1aa27fb451c85b2d7d0e4dce9c1a8f82d63ef'
ALGORITHM = 'HS256'

bcrypt_context=CryptContext(schemes=[ 'bcrypt' ], deprecated='auto')#Use bcrypt for hashing. Bcrypt is one of the most secure hashing algorithms used for storing passwords.
oauth2_bearer = OAuth2PasswordBearer(tokenUrl = 'auth/token') #token route is where clients will go to exchange username/password for a JWT.

class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependency = Annotated[Session,Depends(get_db)]

def authenticate_user(username: str, password: str, db: db_dependency):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:  #if user is none
        return False
    if not bcrypt_context.verify( password,user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {'sub' : username, 'id': user_id, 'role': role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp' : expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
        return {'username': username, 'id': user_id, 'user_role': user_role}
    except JWTError:
      raise  HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
    



@router.post("/",status_code=status.HTTP_201_CREATED)
async def create_user(create_user_request: CreateUserRequest, db: db_dependency):
    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
       # hashed_password=create_user_request.password, #not hashing, saving as plain text
        hashed_password= bcrypt_context.hash(create_user_request.password),
        is_Active=True
    )
    db.add(create_user_model)
    db.commit()

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user =  authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    return {'access_token' :  token, 'token_type': 'bearer' }

