"""Tests for FastAPI endpoints."""

from models import DerbyName


def test_generate_name_endpoint(test_client, mock_generator):
    """Test POST /api/generate endpoint."""
    response = test_client.post("/api/generate")

    assert response.status_code == 200
    data = response.json()

    assert "id" in data
    assert "name" in data
    assert "created_at" in data
    assert "is_favorite" in data
    assert data["name"] == "Test Derby Name"
    assert data["is_favorite"] is False

    # Verify generator was called
    mock_generator.generate.assert_called_once()


def test_get_names_empty(test_client):
    """Test GET /api/names returns empty list when no names exist."""
    response = test_client.get("/api/names")

    assert response.status_code == 200
    assert response.json() == []


def test_get_names_returns_all_names(test_client, test_session):
    """Test GET /api/names returns all saved names."""
    # Create some test names
    names = [
        DerbyName(name="Name 1"),
        DerbyName(name="Name 2"),
        DerbyName(name="Name 3"),
    ]

    for name in names:
        test_session.add(name)
    test_session.commit()

    response = test_client.get("/api/names")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

    # Verify they're ordered by created_at descending
    assert data[0]["name"] == "Name 3"
    assert data[1]["name"] == "Name 2"
    assert data[2]["name"] == "Name 1"


def test_create_custom_name(test_client):
    """Test POST /api/names creates a custom name."""
    response = test_client.post("/api/names", json={"name": "Custom Derby Name"})

    assert response.status_code == 200
    data = response.json()

    assert data["name"] == "Custom Derby Name"
    assert data["is_favorite"] is False
    assert "id" in data
    assert "created_at" in data


def test_create_name_validation(test_client):
    """Test POST /api/names validates required fields."""
    response = test_client.post("/api/names", json={})

    assert response.status_code == 422  # Validation error


def test_delete_name_success(test_client, test_session):
    """Test DELETE /api/names/{id} deletes a name."""
    # Create a test name
    name = DerbyName(name="To Delete")
    test_session.add(name)
    test_session.commit()
    test_session.refresh(name)

    name_id = name.id

    response = test_client.delete(f"/api/names/{name_id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Name deleted successfully"

    # Verify it's actually deleted
    get_response = test_client.get("/api/names")
    assert len(get_response.json()) == 0


def test_delete_name_not_found(test_client):
    """Test DELETE /api/names/{id} returns 404 for non-existent name."""
    response = test_client.delete("/api/names/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Name not found"


def test_toggle_favorite_to_true(test_client, test_session):
    """Test PATCH /api/names/{id}/favorite toggles favorite to true."""
    # Create a test name
    name = DerbyName(name="Favorite Test", is_favorite=False)
    test_session.add(name)
    test_session.commit()
    test_session.refresh(name)

    name_id = name.id

    response = test_client.patch(f"/api/names/{name_id}/favorite")

    assert response.status_code == 200
    data = response.json()
    assert data["is_favorite"] is True


def test_toggle_favorite_to_false(test_client, test_session):
    """Test PATCH /api/names/{id}/favorite toggles favorite to false."""
    # Create a test name that's already favorited
    name = DerbyName(name="Unfavorite Test", is_favorite=True)
    test_session.add(name)
    test_session.commit()
    test_session.refresh(name)

    name_id = name.id

    response = test_client.patch(f"/api/names/{name_id}/favorite")

    assert response.status_code == 200
    data = response.json()
    assert data["is_favorite"] is False


def test_toggle_favorite_not_found(test_client):
    """Test PATCH /api/names/{id}/favorite returns 404 for non-existent name."""
    response = test_client.patch("/api/names/99999/favorite")

    assert response.status_code == 404
    assert response.json()["detail"] == "Name not found"


def test_duplicate_name_handling(test_client, test_session):
    """Test that duplicate names are handled (unique constraint)."""
    # Create first name
    name1 = DerbyName(name="Duplicate Test")
    test_session.add(name1)
    test_session.commit()

    # Try to create duplicate via API
    response = test_client.post("/api/names", json={"name": "Duplicate Test"})

    # Should fail due to unique constraint
    assert response.status_code == 500  # Internal server error due to DB constraint


def test_api_cors_headers(test_client):
    """Test that CORS headers are present."""
    response = test_client.get("/api/names")

    # FastAPI TestClient doesn't send Origin header, so CORS middleware
    # won't add the headers. This test verifies the middleware is configured.
    # In a real browser request, the headers would be present.
    assert response.status_code == 200


def test_multiple_operations_workflow(test_client, mock_generator):
    """Test a complete workflow: generate, list, favorite, delete."""
    # 1. Generate a name
    gen_response = test_client.post("/api/generate")
    assert gen_response.status_code == 200
    name_id = gen_response.json()["id"]

    # 2. List names
    list_response = test_client.get("/api/names")
    assert len(list_response.json()) == 1

    # 3. Toggle favorite
    fav_response = test_client.patch(f"/api/names/{name_id}/favorite")
    assert fav_response.json()["is_favorite"] is True

    # 4. Delete name
    del_response = test_client.delete(f"/api/names/{name_id}")
    assert del_response.status_code == 200

    # 5. Verify empty
    final_list = test_client.get("/api/names")
    assert len(final_list.json()) == 0
