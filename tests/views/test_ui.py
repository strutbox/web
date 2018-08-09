def test_index_logged_out(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.template_name == "index.html"
    assert response.context_data == {}

    response = client.get("/?error=forbidden")
    assert response.status_code == 200
    assert response.template_name == "index.html"
    assert "error" in response.context_data
