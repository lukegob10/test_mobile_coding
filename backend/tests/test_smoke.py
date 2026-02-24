import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[2]))
from backend.app.main import app


client = TestClient(app)


def test_healthz():
    r = client.get('/api/v1/healthz')
    assert r.status_code == 200
    assert r.json()['ok'] is True
