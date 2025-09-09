
from fastapi import APIRouter, Depends, HTTPException, Path, Body # pyright: ignore[reportMissingImports]
from typing import Annotated
from sqlalchemy.orm import Session # type: ignore
from starlette import status # type: ignore
from to_do_app.database import SessionLocal
from to_do_app.models import ToDos, ToDoCreate
from .auth import get_current_user

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependency = Annotated[Session,Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]



@router.get("/todo", status_code=status.HTTP_200_OK) # type: ignore
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication failed')
    return db.query(ToDos).all()