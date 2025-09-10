from fastapi.testclient import TestClient #lets you call your FastAPI endpoints directly in tests without needing to run the server with uvicorn
from to_do_app.main import app 
from fastapi import status

client  = TestClient(app) #connecting fastapi "app" to the client

def test_return_health_check():
    response = client.get("/healthy")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'status': 'Healthy'}