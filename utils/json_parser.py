import json
from typing import Any

from agent.schemas import InvalidDecisionError, validate_decision


def extract_json_object(text: str) -> str:
    cleaned = text.strip()

    if cleaned.startswith("```"):
        lines = cleaned.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        cleaned = "\n".join(lines).strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1 or end < start:
        raise InvalidDecisionError(
            "No se encontró un objeto JSON en la respuesta."
        )

    return cleaned[start:end + 1]


def parse_decision(text: str) -> dict[str, Any]:
    json_text = extract_json_object(text)

    try:
        data = json.loads(json_text)

    except json.JSONDecodeError as error:
        raise InvalidDecisionError(
            f"JSON inválido: {error}"
        ) from error

    return validate_decision(data)
