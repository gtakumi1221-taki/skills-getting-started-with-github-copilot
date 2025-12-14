import copy

from fastapi.testclient import TestClient
import pytest

from src import app as app_module

client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    # keep isolated state: deep copy original and restore after test
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(original)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # known activity from seed data
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    email = "teststudent@example.com"
    activity = "Chess Club"

    # signup
    r = client.post(f"/activities/{activity}/signup?email={email}")
    assert r.status_code == 200
    assert email in app_module.activities[activity]["participants"]

    # signup duplicate should fail
    r2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert r2.status_code == 400

    # unregister
    r3 = client.post(f"/activities/{activity}/unregister?email={email}")
    assert r3.status_code == 200
    assert email not in app_module.activities[activity]["participants"]

    # unregistering again should fail
    r4 = client.post(f"/activities/{activity}/unregister?email={email}")
    assert r4.status_code == 400
