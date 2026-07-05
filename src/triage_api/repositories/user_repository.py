from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import psycopg
from psycopg.rows import dict_row


@dataclass(frozen=True)
class UserRecord:
    email: str
    password_hash: str
    password_salt: str
    password_iterations: int
    is_active: bool


class UserRepository(Protocol):
    def get_user_by_email(self, email: str) -> UserRecord | None:
        """Return the API user registered with the given email."""


class PostgresUserRepository:
    def __init__(self, database_url: str):
        self.database_url = database_url

    def get_user_by_email(self, email: str) -> UserRecord | None:
        query = """
            SELECT
                email,
                password_hash,
                password_salt,
                password_iterations,
                is_active
            FROM api_users
            WHERE email = %(email)s
            LIMIT 1
        """
        with psycopg.connect(self.database_url, row_factory=dict_row) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, {"email": email})
                row = cursor.fetchone()

        if row is None:
            return None

        return UserRecord(
            email=row["email"],
            password_hash=row["password_hash"],
            password_salt=row["password_salt"],
            password_iterations=row["password_iterations"],
            is_active=row["is_active"],
        )
