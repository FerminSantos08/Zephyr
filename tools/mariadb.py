from typing import Any

import mysql.connector
from mysql.connector import Error

from config.settings import (
    DB_HOST,
    DB_PASSWORD,
    DB_PORT,
    DB_USER,
)


SYSTEM_DATABASES = {
    "information_schema",
    "mysql",
    "performance_schema",
    "sys",
}


def get_connection(database: str | None = None):
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=database,
    )


def validate_identifier(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} no puede estar vacío.")

    normalized = value.strip()

    if not normalized.replace("_", "").isalnum():
        raise ValueError(
            f"{field_name} contiene caracteres no permitidos."
        )

    return normalized


def list_databases(
    include_system: bool = False,
) -> dict[str, Any]:
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("SHOW DATABASES")

        databases = [row[0] for row in cursor.fetchall()]

        if not include_system:
            databases = [
                database
                for database in databases
                if database not in SYSTEM_DATABASES
            ]

        return {
            "success": True,
            "databases": databases,
            "count": len(databases),
        }

    except Error as error:
        return {
            "success": False,
            "error": str(error),
        }

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


def list_tables(database: str) -> dict[str, Any]:
    connection = None
    cursor = None

    try:
        database = validate_identifier(database, "database")

        connection = get_connection(database)
        cursor = connection.cursor()

        cursor.execute("SHOW TABLES")

        tables = [row[0] for row in cursor.fetchall()]

        return {
            "success": True,
            "database": database,
            "tables": tables,
            "count": len(tables),
        }

    except (Error, ValueError) as error:
        return {
            "success": False,
            "error": str(error),
        }

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


def describe_table(
    database: str,
    table: str,
) -> dict[str, Any]:
    connection = None
    cursor = None

    try:
        database = validate_identifier(database, "database")
        table = validate_identifier(table, "table")

        connection = get_connection(database)
        cursor = connection.cursor(dictionary=True)

        cursor.execute(f"DESCRIBE `{table}`")

        columns = cursor.fetchall()

        return {
            "success": True,
            "database": database,
            "table": table,
            "columns": columns,
        }

    except (Error, ValueError) as error:
        return {
            "success": False,
            "error": str(error),
        }

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


def select_rows(
    database: str,
    table: str,
    limit: int = 5,
) -> dict[str, Any]:
    connection = None
    cursor = None

    try:
        database = validate_identifier(database, "database")
        table = validate_identifier(table, "table")

        if not isinstance(limit, int):
            raise ValueError("limit debe ser un número entero.")

        limit = max(1, min(limit, 50))

        connection = get_connection(database)
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            f"SELECT * FROM `{table}` LIMIT %s",
            (limit,),
        )

        rows = cursor.fetchall()

        return {
            "success": True,
            "database": database,
            "table": table,
            "returned_rows": len(rows),
            "limit": limit,
            "rows": rows,
        }

    except (Error, ValueError) as error:
        return {
            "success": False,
            "error": str(error),
        }

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


def count_rows(
    database: str,
    table: str,
) -> dict[str, Any]:
    connection = None
    cursor = None

    try:
        database = validate_identifier(database, "database")
        table = validate_identifier(table, "table")

        connection = get_connection(database)
        cursor = connection.cursor()

        cursor.execute(f"SELECT COUNT(*) FROM `{table}`")

        result = cursor.fetchone()
        count = result[0] if result else 0

        return {
            "success": True,
            "database": database,
            "table": table,
            "count": count,
        }

    except (Error, ValueError) as error:
        return {
            "success": False,
            "error": str(error),
        }

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()
