import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from backend.main import app


@pytest_asyncio.fixture()
async def async_client():
    """Provides a test client with the recommended ASGITransport."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        app.state.testing = True
        yield client
        app.state.testing = False 