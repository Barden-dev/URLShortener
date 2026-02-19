async def test_success_created_link(client):
    response = await client.post("/shorten", json={"target_url": "https://youtube.com"})
    data = response.json()

    assert response.status_code == 200
    assert data["secret_key"]


async def test_success_redirect(client):
    response = await client.post("/shorten", json={"target_url": "https://youtube.com"})
    data = response.json()
    redirect = await client.get(f"/{data["secret_key"]}", follow_redirects=False)

    assert redirect.status_code == 307
    assert redirect.headers["location"] == data["target_url"]


async def test_create_invalid_url(client):
    response = await client.post("/shorten", json={"target_url": "some-garbage"})
    data = response.json()

    assert response.status_code == 422


async def test_404_not_found(client):
    response = await client.get("/abrakadabra")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
