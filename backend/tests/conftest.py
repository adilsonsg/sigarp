import hashlib
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_db
from app.core.config import settings
from app.database.base import Base
from app.main import app
from app.security.models import AccessRole, AuthPrincipalConfig

TEST_DATABASE_URL = "sqlite+pysqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

TEST_TOKENS = {
    "leitor": "test-reader-token-with-sufficient-entropy",
    "analista": "test-analyst-token-with-sufficient-entropy",
    "administrador": "test-admin-token-with-sufficient-entropy",
    "sem_papel": "test-no-role-token-with-sufficient-entropy",
}


@pytest.fixture(autouse=True)
def configure_authentication() -> Generator[None, None, None]:
    original = settings.auth_principals
    settings.auth_principals = [
        AuthPrincipalConfig(
            subject="reader@ifmt.test",
            name="Pessoa Leitora",
            role=AccessRole.LEITOR,
            token_sha256=hashlib.sha256(TEST_TOKENS["leitor"].encode()).hexdigest(),
        ),
        AuthPrincipalConfig(
            subject="analyst@ifmt.test",
            name="Pessoa Analista",
            role=AccessRole.ANALISTA,
            token_sha256=hashlib.sha256(TEST_TOKENS["analista"].encode()).hexdigest(),
        ),
        AuthPrincipalConfig(
            subject="admin@ifmt.test",
            name="Pessoa Administradora",
            role=AccessRole.ADMINISTRADOR,
            token_sha256=hashlib.sha256(
                TEST_TOKENS["administrador"].encode()
            ).hexdigest(),
        ),
        AuthPrincipalConfig(
            subject="no-role@ifmt.test",
            name="Pessoa sem papel",
            role=None,
            token_sha256=hashlib.sha256(TEST_TOKENS["sem_papel"].encode()).hexdigest(),
        ),
    ]
    yield
    settings.auth_principals = original


@pytest.fixture
def role_headers() -> dict[str, dict[str, str]]:
    return {
        role: {"Authorization": f"Bearer {token}"}
        for role, token in TEST_TOKENS.items()
    }


@pytest.fixture(autouse=True)
def reset_database() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app, raise_server_exceptions=False) as test_client:
        test_client.headers["Authorization"] = f"Bearer {TEST_TOKENS['administrador']}"
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def unauthenticated_client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client

    app.dependency_overrides.clear()
