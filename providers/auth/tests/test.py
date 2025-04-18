# TODO: In utils, a tool should be built to prevent RY from building clients and their behavior.

from typing import Optional

import jwt
import pytest
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from ..strategy.jwt_strategy import AuthStrategy


# Define a mock AuthStrategy for testing purposes if the original is complex
class MockAuthStrategy(AuthStrategy):
    def __init__(self, is_authenticated: bool = True, payload: Optional[dict] = None):
        self.is_authenticated = is_authenticated
        self.payload = payload

    async def authenticate(self, request: Request) -> bool:
        if self.is_authenticated:
            if self.payload:
                request.state.user_payload = self.payload
            return True
        return False


# Use the actual JWTAuth for more realistic testing
class JWTAuthForTesting(AuthStrategy):
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm

    async def authenticate(self, request: Request) -> bool:
        authorization_header = request.headers.get("Authorization")
        if not authorization_header:
            return False
        try:
            scheme, token = authorization_header.split()
            if scheme.lower() != "bearer":
                return False
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Authorization header format",
            )
        if not token:
            return False
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            request.state.user_payload = payload
            return True
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )


SECRET_KEY = "test-secret-key"
ALGORITHM = "HS256"


def create_jwt(payload: dict, secret_key: str = SECRET_KEY, algorithm: str = ALGORITHM):
    return jwt.encode(payload, secret_key, algorithm=algorithm)


@pytest.fixture
def app():
    _app = FastAPI(
        routes=[
            APIRoute("/public", lambda: {"message": "Public endpoint"}),
            APIRoute(
                "/protected",
                lambda request: {
                    "message": "Protected endpoint",
                    "user": request.state.user_payload,
                },
                dependencies=[Depends(JWTAuthForTesting(secret_key=SECRET_KEY))],
            ),
        ]
    )
    return _app


@pytest.fixture
def client(app):
    return TestClient(app)


def test_public_endpoint(client):
    response = client.get("/public")
    assert response.status_code == 200
    assert response.json() == {"message": "Public endpoint"}


def test_protected_endpoint_no_auth(client):
    response = client.get("/protected")
    assert response.status_code == 401
    assert "detail" in response.json()
    assert response.json()["detail"] == "Not authenticated"  # Default FastAPI message


def test_protected_endpoint_invalid_scheme(client):
    token = create_jwt({"sub": "testuser"})
    response = client.get("/protected", headers={"Authorization": f"Basic {token}"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid Authorization header format"


def test_protected_endpoint_invalid_token(client):
    response = client.get(
        "/protected", headers={"Authorization": "Bearer invalid-token"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


def test_protected_endpoint_valid_token(client):
    payload = {"sub": "testuser", "user_id": 123}
    token = create_jwt(payload)
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Protected endpoint"
    assert response.json()["user"] == payload


def test_protected_endpoint_expired_token(client):
    expired_payload = {
        "sub": "testuser",
        "exp": 1,
    }  # Token expires in 1 second (very short for testing)
    expired_token = create_jwt(expired_payload)
    import time

    time.sleep(2)  # Wait for the token to expire
    response = client.get(
        "/protected", headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert (
        response.json()["detail"] == "Invalid token"
    )  # jwt library might just say invalid if expired


# More robust expired token test if you want to catch the ExpiredSignatureError specifically
def test_protected_endpoint_expired_token_explicit_check(client):
    expired_payload = {"sub": "testuser", "exp": 1600000000}  # An old timestamp
    expired_token = create_jwt(expired_payload)
    response = client.get(
        "/protected", headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"
