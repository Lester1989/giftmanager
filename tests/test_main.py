import json
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_get_friends():
    response = client.get("/friends")
    assert response.status_code == 200
    # Add assertions for the response body


def test_get_friend():
    response = client.get("/friends/string")
    assert response.status_code == 200
    # Add assertions for the response body


def test_get_friend_not_found():
    response = client.get("/friends/999")
    assert response.status_code == 404
    # Add assertions for the response body


def test_create_friend():
    friend_data = {"name": "John Doe", "age": 30}
    response = client.post("/friends", json=friend_data)
    assert response.status_code == 200
    # Add assertions for the response body


def test_update_friend():
    friend_data = {"name": "John Doe", "age": 30}
    response = client.put("/friends/1", json=friend_data)
    assert response.status_code == 200
    # Add assertions for the response body


def test_update_friend_not_found():
    friend_data = {"name": "John Doe", "age": 30}
    response = client.put("/friends/999", json=friend_data)
    assert response.status_code == 404
    # Add assertions for the response body


def test_delete_friend():
    response = client.delete("/friends/1")
    assert response.status_code == 200
    # Add assertions for the response body


def test_delete_friend_not_found():
    response = client.delete("/friends/999")
    assert response.status_code == 404
    # Add assertions for the response body


# Add similar tests for the GiftIdea routes