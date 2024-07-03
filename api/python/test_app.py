import requests

BASE_URL = "http://localhost:5000/api/data"


def test_post_data():
    payload = {"test_key": "test_value"}
    response = requests.post(BASE_URL, json=payload)
    assert response.status_code == 201
    assert response.json() == payload


def test_get_data():
    response = requests.get(f"{BASE_URL}/test_key")
    assert response.status_code == 200
    assert response.json() == {"test_key": "test_value"}


def test_put_data():
    payload = {"value": "new_value"}
    response = requests.put(f"{BASE_URL}/test_key", json=payload)
    assert response.status_code == 200
    assert response.json() == {"test_key": "new_value"}


def test_delete_data():
    response = requests.delete(f"{BASE_URL}/test_key")
    assert response.status_code == 200
    assert response.json() == {"message": "Deleted"}

    response = requests.get(f"{BASE_URL}/test_key")
    assert response.status_code == 404
