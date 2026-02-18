async def test_404_not_found(client):
    response = await client.get("/abrakadabra")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not found."}