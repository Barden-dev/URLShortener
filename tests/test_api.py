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

    assert response.status_code == 422


async def test_404_not_found(client):
    response = await client.get("/abrakadabra")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


async def test_zero_link_clicks(client):
    response = await client.post("/shorten", json={"target_url": "https://youtube.com"})
    response_data = response.json()

    url_stats = await client.get(f"/stats/{response_data['secret_key']}")
    stats_data = url_stats.json()

    assert stats_data["clicks"] == 0


async def test_multiple_link_clicks(client):
    response = await client.post("/shorten", json={"target_url": "https://youtube.com"})
    response_data = response.json()

    for i in range(10):
        await client.get(
            f"/{response_data["secret_key"]}", follow_redirects=False
        )

    url_stats = await client.get(f"/stats/{response_data['secret_key']}")
    stats_data = url_stats.json()

    assert stats_data["clicks"] == 10
