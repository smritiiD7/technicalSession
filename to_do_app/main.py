
from fastapi import FastAPI
from to_do_app import models 
from to_do_app.database import engine
from to_do_app.routers import auth, todos, admin

app = FastAPI()

models.Base.metadata.create_all(bind=engine) #will create everything from db.py and model.py files

@app.get("/healthy")
def health_check():
    return {'status': 'Healthy'}



app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)


