
import shutil
from pathlib import Path
from typing import Any


HOME = Path.home().resolve()


def resolve_safe_path(path: str) -> Path:
    expanded = Path(path).expanduser()

    if not expanded.is_absolute():
        expanded = HOME / expanded

    resolved = expanded.resolve()

    try:
        resolved.relative_to(HOME)
    except ValueError as error:
        raise ValueError(
            "Solo se permiten rutas dentro del HOME del usuario."
        ) from error

    return resolved


def create_folder(path: str) -> dict[str, Any]:
    try:
        target = resolve_safe_path(path)
        target.mkdir(parents=True, exist_ok=True)

        return {
            "success": True,
            "path": str(target),
            "created": True,
        }

    except (OSError, ValueError) as error:
        return {
            "success": False,
            "error": str(error),
        }


def list_directory(path: str = "~") -> dict[str, Any]:
    try:
        target = resolve_safe_path(path)

        if not target.exists():
            raise FileNotFoundError(
                "La ruta no existe."
            )

        if not target.is_dir():
            raise NotADirectoryError(
                "La ruta no es una carpeta."
            )

        entries: list[dict[str, str]] = []

        for item in sorted(
            target.iterdir(),
            key=lambda value: (
                not value.is_dir(),
                value.name.lower(),
            ),
        ):
            entries.append({
                "name": item.name,
                "path": str(item),
                "type": (
                    "directory"
                    if item.is_dir()
                    else "file"
                ),
            })

        return {
            "success": True,
            "path": str(target),
            "count": len(entries),
            "entries": entries,
        }

    except (OSError, ValueError) as error:
        return {
            "success": False,
            "error": str(error),
        }


def move_by_extension(
    source: str,
    destination: str,
    extensions: list[str],
) -> dict[str, Any]:
    try:
        source_path = resolve_safe_path(source)
        destination_path = resolve_safe_path(destination)

        if not source_path.exists():
            raise FileNotFoundError(
                "La carpeta de origen no existe."
            )

        if not source_path.is_dir():
            raise NotADirectoryError(
                "La ruta de origen no es una carpeta."
            )

        destination_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        normalized_extensions = {
            (
                extension.lower()
                if extension.startswith(".")
                else f".{extension.lower()}"
            )
            for extension in extensions
        }

        moved: list[dict[str, str]] = []
        skipped: list[dict[str, str]] = []

        for item in source_path.iterdir():
            if not item.is_file():
                continue

            if item.suffix.lower() not in normalized_extensions:
                continue

            destination_file = destination_path / item.name

            if destination_file.exists():
                skipped.append({
                    "file": item.name,
                    "reason": (
                        "Ya existe en el destino."
                    ),
                })
                continue

            shutil.move(
                str(item),
                str(destination_file),
            )

            moved.append({
                "name": item.name,
                "from": str(item),
                "to": str(destination_file),
            })

        return {
            "success": True,
            "source": str(source_path),
            "destination": str(destination_path),
            "moved_count": len(moved),
            "moved": moved,
            "skipped": skipped,
        }

    except (OSError, ValueError) as error:
        return {
            "success": False,
            "error": str(error),
        }


def rename_path(
    path: str,
    new_name: str,
) -> dict[str, Any]:
    try:
        source = resolve_safe_path(path)

        if not source.exists():
            raise FileNotFoundError(
                "El archivo o carpeta no existe."
            )

        new_name = new_name.strip()

        if not new_name:
            raise ValueError(
                "El nuevo nombre no puede estar vacío."
            )

        if "/" in new_name or "\\" in new_name:
            raise ValueError(
                "El nuevo nombre no debe contener rutas."
            )

        destination = source.parent / new_name
        destination = resolve_safe_path(
            str(destination)
        )

        if destination.exists():
            raise FileExistsError(
                "Ya existe un archivo o carpeta "
                "con ese nombre."
            )

        source.rename(destination)

        return {
            "success": True,
            "old_path": str(source),
            "new_path": str(destination),
        }

    except (OSError, ValueError) as error:
        return {
            "success": False,
            "error": str(error),
        }


def search_files(
    query: str,
    path: str = "~",
    extension: str | None = None,
    file_type: str = "all",
    max_results: int = 50,
) -> dict[str, Any]:
    try:
        root = resolve_safe_path(path)

        if not root.exists():
            raise FileNotFoundError(
                "La ruta de búsqueda no existe."
            )

        if not root.is_dir():
            raise NotADirectoryError(
                "La ruta de búsqueda no es una carpeta."
            )

        normalized_query = query.strip().lower()

        if not normalized_query:
            raise ValueError(
                "Debes indicar un nombre o término "
                "de búsqueda."
            )

        file_type = file_type.strip().lower()

        valid_file_types = {
            "all",
            "file",
            "directory",
        }

        if file_type not in valid_file_types:
            raise ValueError(
                "file_type debe ser: "
                "all, file o directory."
            )

        try:
            max_results = int(max_results)
        except (TypeError, ValueError) as error:
            raise ValueError(
                "max_results debe ser un número entero."
            ) from error

        if max_results < 1:
            raise ValueError(
                "max_results debe ser mayor que cero."
            )

        max_results = min(
            max_results,
            200,
        )

        normalized_extension: str | None = None

        if extension:
            normalized_extension = (
                extension
                .strip()
                .lower()
            )

            if not normalized_extension.startswith("."):
                normalized_extension = (
                    f".{normalized_extension}"
                )

        ignored_directories = {
            ".git",
            ".cache",
            ".local",
            ".npm",
            ".venv",
            "venv",
            "node_modules",
            "__pycache__",
        }

        results: list[dict[str, Any]] = []
        scanned_count = 0
        truncated = False

        for item in root.rglob("*"):
            try:
                relative_parts = item.relative_to(
                    root
                ).parts

                if any(
                    part in ignored_directories
                    for part in relative_parts
                ):
                    continue

                scanned_count += 1

                if (
                    normalized_query
                    not in item.name.lower()
                ):
                    continue

                if (
                    file_type == "file"
                    and not item.is_file()
                ):
                    continue

                if (
                    file_type == "directory"
                    and not item.is_dir()
                ):
                    continue

                if normalized_extension:
                    if not item.is_file():
                        continue

                    if (
                        item.suffix.lower()
                        != normalized_extension
                    ):
                        continue

                results.append({
                    "name": item.name,
                    "path": str(item),
                    "type": (
                        "directory"
                        if item.is_dir()
                        else "file"
                    ),
                    "extension": (
                        item.suffix.lower()
                        if item.is_file()
                        else None
                    ),
                })

                if len(results) >= max_results:
                    truncated = True
                    break

            except OSError:
                continue

        return {
            "success": True,
            "query": query,
            "root": str(root),
            "extension": normalized_extension,
            "file_type": file_type,
            "count": len(results),
            "scanned_count": scanned_count,
            "truncated": truncated,
            "results": results,
        }

    except (OSError, ValueError) as error:
        return {
            "success": False,
            "error": str(error),
        }
