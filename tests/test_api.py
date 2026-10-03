import pytest
from app import app
from database import init_db

@pytest.fixture
def client(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    monkeypatch.setattr("database.DATABASE", str(db_file))
    init_db()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c

def test_home_page(client):
    r = client.get("/")
    assert r.status_code == 200

def test_create_and_get_task(client):
    r = client.post("/api/tasks", json={
        "title": "Learn Python",
        "priority": "High",
        "status": "To Do"
    })
    assert r.status_code == 201
    assert r.json["title"] == "Learn Python"
    
    tasks = client.get("/api/tasks")
    assert tasks.status_code == 200
    assert len(tasks.json) == 1

def test_stats(client):
    client.post("/api/tasks", json={"title": "Test"})
    r = client.get("/api/stats")
    assert r.status_code == 200
    assert r.json["total"] == 1

def test_empty_title_rejected(client):
    r = client.post("/api/tasks", json={"title": ""})
    assert r.status_code == 400