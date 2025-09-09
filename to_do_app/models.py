from to_do_app.database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey # type: ignore
from pydantic import BaseModel, Field # type: ignore

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True) #primary key id with indexing = True
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name= Column(String)
    last_name=Column(String)
    hashed_password=Column (String)
    is_Active = Column(Boolean, default=True)
    role= Column(String)


class ToDos(Base):
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))



class ToDoCreate(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool 
