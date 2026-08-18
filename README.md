# Zephyr

Zephyr es un asistente local de terminal para Linux. Usa Ollama como modelo de lenguaje y puede ejecutar herramientas locales controladas para consultar el sistema, trabajar con archivos, abrir aplicaciones y leer datos de MariaDB.

## Funciones

- Chat en terminal con historial de conversacion.
- Conexion con Ollama mediante API HTTP.
- Herramientas para archivos y carpetas.
- Consultas seguras de MariaDB orientadas a lectura.
- Apertura de aplicaciones del sistema.
- Modulo de voz preparado para TTS.

## Requisitos

- Python 3.12 o superior.
- Ollama corriendo en la maquina o en red.
- Dependencias Python usadas por el proyecto, como `requests` y `mysql-connector-python`.
- MariaDB opcional si se usan las herramientas de base de datos.

## Configuracion

Copia `.env.example` como `.env` o exporta las variables en tu shell:

```bash
export ZEPHYR_OLLAMA_URL="http://localhost:11434/api/chat"
export ZEPHYR_DB_HOST="localhost"
export ZEPHYR_DB_PORT="3306"
export ZEPHYR_DB_USER="zephyr_reader"
export ZEPHYR_DB_PASSWORD="tu_password"
```

El modelo se configura en `config/settings.py`.

## Ejecutar

```bash
python main.py
```

Comandos dentro del chat:

- `salir`
- `limpiar`

## Notas

Las credenciales no deben guardarse en el codigo. Usa variables de entorno para contrasenas, tokens o rutas privadas.
