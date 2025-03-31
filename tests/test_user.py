import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/user/", json={
            "full_name": "John Doe",
            "email": "johndoe@example.com",
            "phone": "+1234567890",
            "address": "123 Main St, New York",
            "dob": "1990-01-01"
        })
        assert response.status_code == 201
        assert "id" in response.json()

@pytest.mark.asyncio
async def test_get_user():
    user_id = "some_user_id"  # Thay thế bằng ID thực tế
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(f"/user/{user_id}")
        assert response.status_code == 200
        assert response.json()["email"] == "johndoe@example.com"

@pytest.mark.asyncio
async def test_update_user():
    user_id = "some_user_id"  # Thay thế bằng ID thực tế
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.put(f"/user/{user_id}", json={
            "full_name": "John Updated",
            "email": "johnupdated@example.com",
            "phone": "+9876543210",
            "address": "456 Another St, LA",
            "dob": "1990-01-02"
        })
        assert response.status_code == 200
        assert response.json()["message"] == "User updated successfully"

@pytest.mark.asyncio
async def test_delete_user():
    user_id = "some_user_id"  # Thay thế bằng ID thực tế
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete(f"/user/{user_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "User deleted successfully"
