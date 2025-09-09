
from fastapi import APIRouter, Depends, HTTPException, Path, Body # pyright: ignore[reportMissingImports]
from typing import Annotated
from sqlalchemy.orm import Session # type: ignore
from starlette import status # type: ignore
from to_do_app.database import SessionLocal
from to_do_app.models import ToDos, ToDoCreate
from .auth import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependency = Annotated[Session,Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/",  status_code=status.HTTP_200_OK)
async def read_All(user: user_dependency, db: db_dependency): # type: ignore
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')
    return db.query(ToDos).filter(ToDos.owner_id == user.get('id')).all()

@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int):  # type: ignore
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')
    todo_model =  db.query(ToDos).filter(ToDos.id == todo_id).filter(ToDos.owner_id == user.get('id')).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail = 'Todo not found')

@router.post("/todo/add", status_code=status.HTTP_201_CREATED)
async def create_task(user: user_dependency, db: db_dependency, todo: ToDoCreate ): # type: ignore
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')
    to_do_model = ToDos ( #Use SQLAlchemy model here
        title = todo.title,
        description = todo.description,
        priority = todo.priority,
        complete = todo.complete, owner_id=user.get('id')
    )
    db.add(to_do_model)
    db.commit()
    db.refresh(to_do_model)

    return to_do_model
    

@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency,db: db_dependency, todo: ToDoCreate, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')
    todo_model = db.query(ToDos).filter(ToDos.id == todo_id).filter(ToDos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='To Do not found.')
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete
   
    
    db.add(todo_model)
    db.commit()
    
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency,db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')
    todo_model = db.query(ToDos).filter(ToDos.id == todo_id).filter(ToDos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found')
    db.query(ToDos).filter(ToDos.id == todo_id).filter(ToDos.owner_id == user.get('id')).delete()

    db.commit()