import json
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200


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
    assert response.status_code == 200



    # Add assertions for the response body


# Add similar tests for the GiftIdea routes