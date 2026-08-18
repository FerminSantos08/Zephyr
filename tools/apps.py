import shutil
import subprocess
from typing import Any


def open_application(app: str) -> dict[str, Any]:
    app = app.strip()

    if not app:
        return {
            "success": False,
            "error": "Debes indicar una aplicación."
        }

    executable = shutil.which(app)

    if executable is None:
        return {
            "success": False,
            "error": f"No encontré '{app}' en el PATH."
        }

    try:
        process = subprocess.Popen(
            [executable],
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        return {
            "success": True,
            "application": app,
            "executable": executable,
            "pid": process.pid,
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error),
        }
