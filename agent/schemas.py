from typing import Any


class InvalidDecisionError(ValueError):
    pass


def validate_decision(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise InvalidDecisionError("La decisión debe ser un objeto JSON.")

    decision_type = data.get("type")

    if decision_type == "response":
        content = data.get("content")

        if not isinstance(content, str) or not content.strip():
            raise InvalidDecisionError(
                "Una respuesta debe incluir un campo content válido."
            )

        return {
            "type": "response",
            "content": content.strip(),
        }

    if decision_type == "tool":
        tool_name = data.get("tool")
        arguments = data.get("arguments", {})

        if not isinstance(tool_name, str) or not tool_name.strip():
            raise InvalidDecisionError(
                "Una llamada de herramienta debe incluir tool."
            )

        if not isinstance(arguments, dict):
            raise InvalidDecisionError(
                "El campo arguments debe ser un objeto JSON."
            )

        return {
            "type": "tool",
            "tool": tool_name.strip(),
            "arguments": arguments,
        }

    raise InvalidDecisionError(
        'El campo type debe ser "response" o "tool".'
    )
