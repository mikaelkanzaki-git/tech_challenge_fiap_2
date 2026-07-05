from __future__ import annotations

import json
import logging
import sys
from typing import Any

APPLICATION_NAME = "triage_api"


class ApplicationLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        timestamp = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        step = getattr(record, "step", "-")
        payload = getattr(record, "payload", None)
        server_response = getattr(record, "server_response", None)
        payload_text = _to_json(payload)
        response_text = _to_json(server_response)
        return (
            f"[{timestamp}] - [{APPLICATION_NAME}] - [{record.levelname}] - "
            f"[{step}] - [{record.getMessage()}] - "
            f"[payload={payload_text}] - [server_response={response_text}]"
        )


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(ApplicationLogFormatter())
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


def _to_json(value: Any) -> str:
    if value is None:
        return "-"
    try:
        return json.dumps(value, ensure_ascii=False, default=str)
    except TypeError:
        return str(value)
