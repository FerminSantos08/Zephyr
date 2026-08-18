import json
from typing import Any

from agent.schemas import InvalidDecisionError
from ai.ollama_client import chat_with_ollama
from ai.prompt import SYSTEM_PROMPT
from memory.conversation import ConversationMemory
from tools.registry import execute_tool
from utils.json_parser import parse_decision

MAX_AGENT_STEPS = 12


class ZephyrAgent:
    def __init__(self) -> None:
        self.memory = ConversationMemory()

    def clear_memory(self) -> None:
        self.memory.clear()

    def build_messages(
        self,
        temporary_messages: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        return [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            *self.memory.get_messages(),
            *temporary_messages,
        ]

    def run(self, user_message: str) -> str:
        temporary_messages: list[dict[str, str]] = [
            {
                "role": "user",
                "content": user_message,
            }
        ]

        executed_calls: set[str] = set()

        for _ in range(MAX_AGENT_STEPS):
            messages = self.build_messages(
                temporary_messages
            )

            model_result = chat_with_ollama(
                messages,
                think=False,
            )

            raw_response = model_result.get(
                "content",
                "",
            ).strip()

            if not raw_response:
                response = (
                    "El modelo no devolvió una respuesta válida."
                )

                self._save_conversation(
                    user_message,
                    response,
                )

                return response

            try:
                decision = parse_decision(
                    raw_response
                )

            except InvalidDecisionError:
                self._save_conversation(
                    user_message,
                    raw_response,
                )

                return raw_response

            if decision["type"] == "response":
                response = decision["content"].strip()

                if not response:
                    response = (
                        "El modelo devolvió una respuesta vacía."
                    )

                self._save_conversation(
                    user_message,
                    response,
                )

                return response

            tool_name = decision["tool"]
            arguments = decision["arguments"]

            call_signature = self._build_call_signature(
                tool_name=tool_name,
                arguments=arguments,
            )

            if call_signature in executed_calls:
                temporary_messages.append({
                    "role": "assistant",
                    "content": json.dumps(
                        decision,
                        ensure_ascii=False,
                    ),
                })

                temporary_messages.append({
                    "role": "user",
                    "content": (
                        "La misma herramienta ya fue ejecutada "
                        "con exactamente los mismos argumentos.\n\n"
                        "No vuelvas a repetir esa llamada.\n"
                        "Revisa la solicitud original y decide entre:\n"
                        "1. Usar otra herramienta necesaria.\n"
                        "2. Responder si todas las acciones ya fueron "
                        "completadas.\n\n"
                        "No afirmes que una operación se realizó si no "
                        "existe un resultado real que lo confirme."
                    ),
                })

                continue

            executed_calls.add(
                call_signature
            )

            tool_result: dict[str, Any] = execute_tool(
                tool_name=tool_name,
                arguments=arguments,
            )

            temporary_messages.append({
                "role": "assistant",
                "content": json.dumps(
                    decision,
                    ensure_ascii=False,
                ),
            })

            temporary_messages.append({
                "role": "user",
                "content": self._build_tool_result_message(
                    original_request=user_message,
                    tool_name=tool_name,
                    arguments=arguments,
                    tool_result=tool_result,
                ),
            })

        response = (
            "No pude completar la solicitud porque se alcanzó "
            "el límite de acciones permitidas."
        )

        self._save_conversation(
            user_message,
            response,
        )


        return response

    def _save_conversation(
        self,
        user_message: str,
        assistant_response: str,
    ) -> None:
        self.memory.add(
            "user",
            user_message,
        )

        self.memory.add(
            "assistant",
            assistant_response,
        )

    def _build_call_signature(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> str:
        return json.dumps(
            {
                "tool": tool_name,
                "arguments": arguments,
            },
            ensure_ascii=False,
            sort_keys=True,
            default=str,
        )

    def _build_tool_result_message(
        self,
        original_request: str,
        tool_name: str,
        arguments: dict[str, Any],
        tool_result: dict[str, Any],
    ) -> str:
        serialized_arguments = json.dumps(
            arguments,
            ensure_ascii=False,
            default=str,
        )

        serialized_result = json.dumps(
            tool_result,
            ensure_ascii=False,
            default=str,
        )

        return (
            "Se ejecutó una herramienta y este es su resultado real.\n\n"
            f"Solicitud original del usuario:\n"
            f"{original_request}\n\n"
            f"Herramienta ejecutada:\n"
            f"{tool_name}\n\n"
            f"Argumentos utilizados:\n"
            f"{serialized_arguments}\n\n"
            f"Resultado real:\n"
            f"{serialized_result}\n\n"
            "REGLAS CRÍTICAS:\n"
            "- Usa exclusivamente los datos del resultado real.\n"
            "- Comprueba siempre el campo success.\n"
            "- Si success es false, explica el error y no afirmes que la operación se completó.\n"
            "- No inventes registros, nombres, rutas, archivos, correos ni valores.\n"
            "- No confundas crear una carpeta con mover, copiar, renombrar o crear archivos.\n"
            "- Una herramienta exitosa no significa necesariamente que toda la solicitud original haya terminado.\n"
            "- Revisa de nuevo la solicitud original e identifica si todavía quedan acciones pendientes.\n"
            "- Si quedan acciones pendientes, utiliza una sola herramienta adicional.\n"
            "- Solo confirma una acción después de ejecutarla y recibir success=true.\n"
            "- No repitas exactamente la misma herramienta con los mismos argumentos.\n"
            "- Si rows contiene una sola fila, presenta solamente esa fila.\n"
            "- Si rows está vacío, indica que no hay registros.\n"
            "- Si moved_count es 0, indica que no se movió ningún archivo.\n"
            "- Si existe skipped, revisa esos elementos antes de afirmar que todos los archivos fueron organizados.\n"
            "- Si todas las acciones ya fueron completadas, responde al usuario de manera clara y natural.\n"
            "- No muestres el JSON interno ni menciones nombres internos de herramientas."
        )
