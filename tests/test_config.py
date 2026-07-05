import os

from triage_api.core.config import load_environment_file


def test_load_environment_file_reads_dotenv_values(tmp_path, monkeypatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "# local secrets",
                "DATABASE_URL=postgresql://user:secret@localhost:5432/tech_challenge_fiap_2",
                "MODEL_VERSION=test",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("MODEL_VERSION", raising=False)

    load_environment_file(env_file)

    assert os.environ["DATABASE_URL"].endswith("/tech_challenge_fiap_2")
    assert os.environ["MODEL_VERSION"] == "test"


def test_load_environment_file_keeps_existing_environment_value(tmp_path, monkeypatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("MODEL_VERSION=file_value", encoding="utf-8")
    monkeypatch.setenv("MODEL_VERSION", "shell_value")

    load_environment_file(env_file)

    assert os.environ["MODEL_VERSION"] == "shell_value"
