import logging

from triage_api.core.logging import APPLICATION_NAME, ApplicationLogFormatter


def test_application_log_formatter_includes_standard_fields() -> None:
    formatter = ApplicationLogFormatter()
    record = logging.LogRecord(
        name="triage_api.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="Mensagem de teste.",
        args=(),
        exc_info=None,
    )
    record.step = "test_step"
    record.payload = {"age": 30}
    record.server_response = {"status": "ok"}

    log_text = formatter.format(record)

    assert f"[{APPLICATION_NAME}]" in log_text
    assert "[INFO]" in log_text
    assert "[test_step]" in log_text
    assert "[Mensagem de teste.]" in log_text
    assert '[payload={"age": 30}]' in log_text
    assert '[server_response={"status": "ok"}]' in log_text
