from triage_api.repositories import user_repository
from triage_api.repositories.user_repository import PostgresUserRepository


class FakeCursor:
    def __init__(self, row):
        self.row = row
        self.query = None
        self.params = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def execute(self, query, params):
        self.query = query
        self.params = params

    def fetchone(self):
        return self.row


class FakeConnection:
    def __init__(self, row):
        self.cursor_instance = FakeCursor(row)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def cursor(self):
        return self.cursor_instance


def test_postgres_user_repository_returns_user(monkeypatch) -> None:
    row = {
        "email": "fiap@tech2.com",
        "password_hash": "hash",
        "password_salt": "salt",
        "password_iterations": 260000,
        "is_active": True,
    }
    connection = FakeConnection(row)
    monkeypatch.setattr(
        user_repository.psycopg,
        "connect",
        lambda database_url, row_factory: connection,
    )
    repository = PostgresUserRepository("postgresql://example")

    user = repository.get_user_by_email("fiap@tech2.com")

    assert user is not None
    assert user.email == "fiap@tech2.com"
    assert user.is_active
    assert connection.cursor_instance.params == {"email": "fiap@tech2.com"}


def test_postgres_user_repository_returns_none_when_user_is_missing(monkeypatch) -> None:
    monkeypatch.setattr(
        user_repository.psycopg,
        "connect",
        lambda database_url, row_factory: FakeConnection(None),
    )
    repository = PostgresUserRepository("postgresql://example")

    user = repository.get_user_by_email("missing@example.com")

    assert user is None
