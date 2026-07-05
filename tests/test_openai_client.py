from triage_api.services.openai_client import OpenAIResponseClient, _extract_output_text


def test_openai_response_client_is_not_configured_without_api_key() -> None:
    client = OpenAIResponseClient(api_key=None, model="test-model")

    assert not client.is_configured()
    assert client.create_message("instructions", "user input") is None


def test_extract_output_text_reads_output_text() -> None:
    response_payload = {"output_text": "Resposta final."}

    assert _extract_output_text(response_payload) == "Resposta final."


def test_extract_output_text_reads_nested_content() -> None:
    response_payload = {
        "output": [
            {
                "content": [
                    {"text": "Resposta aninhada."},
                ],
            }
        ]
    }

    assert _extract_output_text(response_payload) == "Resposta aninhada."


def test_extract_output_text_returns_none_when_text_is_missing() -> None:
    assert _extract_output_text({"output": []}) is None
