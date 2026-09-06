def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_demo_dashboard(client):
    response = client.get("/demo", follow_redirects=True)
    assert response.status_code == 200
    assert "OSSentinel" in response.text

def test_public_pricing(client): assert client.get("/pricing").status_code == 200
