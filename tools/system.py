import getpass
import platform
import socket
from datetime import datetime
from typing import Any


def get_system_info(field: str) -> dict[str, Any]:
    normalized_field = field.lower().strip()

    available_fields = {
        "time": lambda: datetime.now().strftime("%H:%M:%S"),
        "date": lambda: datetime.now().strftime("%d/%m/%Y"),
        "datetime": lambda: datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "user": getpass.getuser,
        "hostname": socket.gethostname,
        "os": lambda: platform.system(),
        "platform": platform.platform,
        "python": platform.python_version,
    }

    if normalized_field not in available_fields:
        return {
            "success": False,
            "error": f"Campo no disponible: {field}",
            "available_fields": list(available_fields.keys()),
        }

    try:
        value = available_fields[normalized_field]()

        return {
            "success": True,
            "field": normalized_field,
            "value": value,
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error),
        }
