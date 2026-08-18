from config.settings import MAX_HISTORY_MESSAGES


class ConversationMemory:
    def __init__(self) -> None:
        self._messages: list[dict[str, str]] = []

    def add(self, role: str, content: str) -> None:
        self._messages.append({
            "role": role,
            "content": content,
        })

        self._messages = self._messages[-MAX_HISTORY_MESSAGES:]

    def get_messages(self) -> list[dict[str, str]]:
        return self._messages.copy()

    def clear(self) -> None:
        self._messages.clear()
