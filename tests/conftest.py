import asyncio
from collections.abc import Generator, AsyncGenerator
from httpx import AsyncClient

import pytest
import pytest_asyncio
from src.config.database import custom_metadata, async_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


from src.main import app


test_async_session_maker = async_sessionmaker(
    async_engine, autocommit=False, autoflush=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://") as client:
        async with async_engine.begin() as conn:
            await conn.run_sync(custom_metadata.create_all)
        yield client

    async with async_engine.begin() as conn:
        await conn.run_sync(custom_metadata.drop_all)

    await async_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def session() -> AsyncGenerator[AsyncSession, None]:
    async with test_async_session_maker() as s:
        async with async_engine.begin() as conn:
            await conn.run_sync(custom_metadata.create_all)
        yield s

    async with async_engine.begin() as conn:
        await conn.run_sync(custom_metadata.drop_all)

    await async_engine.dispose()
