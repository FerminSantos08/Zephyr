from typing import Any, Callable
from tools.system import get_system_info
from tools.apps import open_application

from tools.filesystem import (
    create_folder,
    list_directory,
    move_by_extension,
    rename_path,
    search_files,
)
from tools.mariadb import (
    count_rows,
    describe_table,
    list_databases,
    list_tables,
    select_rows,
)

ToolFunction = Callable[..., dict[str, Any]]


TOOLS: dict[str, ToolFunction] = {
    "get_system_info": get_system_info,

    "list_databases": list_databases,
    "list_tables": list_tables,
    "describe_table": describe_table,
    "select_rows": select_rows,
    "count_rows": count_rows,

    "create_folder": create_folder,
    "list_directory": list_directory,
    "move_by_extension": move_by_extension,
    "rename_path": rename_path,
    "search_files": search_files,

    "open_application": open_application,
}


def execute_tool(
    tool_name: str,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    tool = TOOLS.get(tool_name)

    if tool is None:
        return {
            "success": False,
            "error": f"Herramienta desconocida: {tool_name}",
        }

    try:
        return tool(**arguments)

    except TypeError as error:
        return {
            "success": False,
            "error": (
                f"Argumentos inválidos para {tool_name}: {error}"
            ),
        }

    except Exception as error:
        return {
            "success": False,
            "error": (
                f"Error ejecutando {tool_name}: {error}"
            ),
        }
