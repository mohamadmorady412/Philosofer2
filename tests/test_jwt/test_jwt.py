# python -m pytest tests\test_jwt\test_jwt.py

import time

import jwt
import pytest
from fastapi import Depends, FastAPI, Request
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport

from providers.auth.methods.a_jwt import JWTAuth

SECRET_KEY = "test-secret-key"
jwt_auth = JWTAuth(secret_key=SECRET_KEY)

app = FastAPI()


def create_jwt(payload: dict):
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


@app.get("/protected", dependencies=[Depends(jwt_auth.authenticate)])
async def protected_route(request: Request):
    if not hasattr(request.state, "user_payload"):
        return {"error": "Unauthorized"}
    return {"message": "Access granted", "user": request.state.user_payload}


@app.get("/public")
async def public_route():
    return {"message": "This is public"}


@pytest.mark.asyncio
async def test_valid_token():
    payload = {"sub": "test-user", "exp": int(time.time()) + 600}
    token = create_jwt(payload)
    headers = {"Authorization": f"Bearer {token}"}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/protected", headers=headers)
        assert response.status_code == 200
        assert response.json()["user"]["sub"] == "test-user"


@pytest.mark.asyncio
async def test_expired_token():
    payload = {"sub": "expired-user", "exp": int(time.time()) - 10}
    token = create_jwt(payload)
    headers = {"Authorization": f"Bearer {token}"}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/protected", headers=headers)
        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_invalid_token():
    headers = {"Authorization": "Bearer invalid.token.value"}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/protected", headers=headers)
        assert response.status_code == 401
        assert "invalid token" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_missing_token():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/protected")
        assert response.status_code == 200
        assert response.json() == {"error": "Unauthorized"}
