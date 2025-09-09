from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine, text
from sqlalchemy.orm import sessionmaker
from to_do_app.database import Base
import pytest
from to_do_app.main import app
from to_do_app.models import ToDos


SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db" #create new database

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args= {"check_same_thread": False},
    poolclass = StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)



def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {'username' : 'rammy', 'id' : 1,  'user_role' : 'admin' }

client = TestClient(app) #creates a fake HTTP client that can talk to your FastAPI app without starting a real server (no uvicorn needed)

@pytest.fixture
def test_todo():
    todo = ToDos(
        title='Learn to Code!',
        description="Learn Everyday!",
        priority=5,
        complete=False,
        owner_id=1
    )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    db.refresh(todo) 
    yield todo

    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()