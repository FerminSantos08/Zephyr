import os

MODEL_NAME = "gemma4:12b"

OLLAMA_URL = os.getenv("ZEPHYR_OLLAMA_URL", "http://192.168.3.11:11434/api/chat")

TEMPERATURE = 0.2

MAX_HISTORY_MESSAGES = 50

REQUEST_TIMEOUT = 120

#conexion de la bd 
DB_HOST = os.getenv("ZEPHYR_DB_HOST", "localhost")
DB_PORT = int(os.getenv("ZEPHYR_DB_PORT", "3306"))
DB_USER = os.getenv("ZEPHYR_DB_USER", "zephyr_reader")
DB_PASSWORD = os.getenv("ZEPHYR_DB_PASSWORD", "")
