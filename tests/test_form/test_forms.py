import pytest
from fastapi import FastAPI, Request
from httpx import ASGITransport, AsyncClient

from providers.data_teransfer.methods.forms import build_form_class, create_field
from providers.data_teransfer.strategy.fs import FormDataStrategy


@pytest.fixture
def test_app():
    app = FastAPI()

    fields = [
        create_field("username", str),
        create_field("password", str),
    ]
    DynamicLoginForm = build_form_class("DynamicLoginForm", fields, FormDataStrategy())

    @app.post("/test-login")
    async def test_login(request: Request):
        form = DynamicLoginForm()
        data = await form.from_request(request)
        return {"data": form.to_dict()}

    return app


@pytest.mark.asyncio
async def test_dynamic_form_submission(test_app):
    transport = ASGITransport(app=test_app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        response = await ac.post(
            "/test-login", data={"username": "testuser", "password": "secret123"}
        )

    assert response.status_code == 200
    assert response.json() == {
        "data": {"username": "testuser", "password": "secret123"}
    }
