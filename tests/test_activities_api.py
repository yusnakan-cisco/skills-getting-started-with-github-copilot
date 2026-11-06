from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    original_activities = deepcopy(activities)
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        activities.clear()
        activities.update(original_activities)


def test_get_activities_returns_activity_details(client):
    response = client.get("/activities")

    assert response.status_code == 200
    activity = response.json()["Chess Club"]
    assert activity["description"]
    assert activity["schedule"]
    assert isinstance(activity["participants"], list)


def test_signup_adds_participant(client):
    email = "new.student@example.com"

    response = client.post("/activities/Art Club/signup", params={"email": email})

    assert response.status_code == 200
    assert email in client.get("/activities").json()["Art Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    email = "new.student@example.com"
    client.post("/activities/Art Club/signup", params={"email": email})

    response = client.post("/activities/Art Club/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_returns_not_found_for_unknown_activity(client):
    response = client.post("/activities/Unknown Club/signup", params={"email": "student@example.com"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    email = "new.student@example.com"
    client.post("/activities/Art Club/signup", params={"email": email})

    response = client.delete("/activities/Art Club/signup", params={"email": email})

    assert response.status_code == 200
    assert email not in client.get("/activities").json()["Art Club"]["participants"]


def test_unregister_returns_not_found_for_missing_participant(client):
    response = client.delete(
        "/activities/Art Club/signup",
        params={"email": "missing.student@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_returns_not_found_for_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown Club/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"