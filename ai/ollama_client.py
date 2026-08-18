from typing import Any

import requests

from config.settings import (
    MODEL_NAME,
    OLLAMA_URL,
    REQUEST_TIMEOUT,
    TEMPERATURE,
)


class OllamaError(RuntimeError):
    pass


def chat_with_ollama(
    messages: list[dict[str, Any]],
    *,
    tools: list[dict[str, Any]] | None = None,
    think: bool = False,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        "think": think,
        "options": {
            "temperature": TEMPERATURE,
        },
    }

    if tools:
        payload["tools"] = tools

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()

    except requests.ConnectionError as error:
        raise OllamaError(
            "No pude conectarme con Ollama. "
            "Verifica que el servicio esté iniciado."
        ) from error

    except requests.Timeout as error:
        raise OllamaError(
            "Ollama tardó demasiado en responder."
        ) from error

    except requests.RequestException as error:
        raise OllamaError(
            f"Ocurrió un error al consultar Ollama: {error}"
        ) from error

    try:
        data = response.json()
        message = data["message"]

    except (ValueError, KeyError, TypeError) as error:
        raise OllamaError(
            "Ollama devolvió una respuesta inesperada."
        ) from error

    return {
        "content": str(message.get("content", "")).strip(),
        "thinking": str(message.get("thinking", "")).strip(),
        "tool_calls": message.get("tool_calls", []),
    }