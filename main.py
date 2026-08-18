import itertools
import sys
import threading
import time
import random

from agent.loop import ZephyrAgent


APP_NAME = "ZEPHYR"
APP_VERSION = "0.3.0"


EXIT_COMMANDS = {
    "exit",
    "quit",
    "salir",
}

CLEAR_COMMANDS = {
    "clear",
    "limpiar",
}


RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

USER_COLOR = "\033[38;5;114m"
ZEPHYR_COLOR = "\033[38;5;141m"
SYSTEM_COLOR = "\033[38;5;221m"
ERROR_COLOR = "\033[38;5;203m"
LOADING_COLOR = "\033[38;5;147m"
SECONDARY_COLOR = "\033[38;5;245m"
ACCENT_COLOR = "\033[38;5;183m"
SUCCESS_COLOR = "\033[38;5;114m"

GOODBYE_MESSAGES = [
    "Hasta luego.",
    "Nos vemos pronto.",
    "Fue un gusto ayudarte.",
    "Cuídate mucho.",
    "Que tengas un excelente día.",
    "Aquí estaré cuando me necesites.",
    "Hasta la próxima.",
    "Nos vemos. Fue un placer conversar contigo.",
]


def random_goodbye() -> str:
    return random.choice(GOODBYE_MESSAGES)


class Spinner:
    def __init__(self, message: str = "Zephyr está pensando") -> None:
        self.message = message
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def _animate(self) -> None:
        frames = itertools.cycle([
            "⠋", "⠙", "⠹", "⠸", "⠼",
            "⠴", "⠦", "⠧", "⠇", "⠏",
        ])

        while not self._stop_event.is_set():
            sys.stdout.write(
                f"\r{LOADING_COLOR}{BOLD}{next(frames)} {self.message}...{RESET}"
            )
            sys.stdout.flush()
            time.sleep(0.08)

    def start(self) -> None:
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join()
        sys.stdout.write("\r\033[2K")
        sys.stdout.flush()


def print_banner() -> None:
    logo = [
        "███████╗███████╗██████╗ ██╗  ██╗██╗   ██╗██████╗ ",
        "╚══███╔╝██╔════╝██╔══██╗██║  ██║╚██╗ ██╔╝██╔══██╗",
        "  ███╔╝ █████╗  ██████╔╝███████║ ╚████╔╝ ██████╔╝",
        " ███╔╝  ██╔══╝  ██╔═══╝ ██╔══██║  ╚██╔╝  ██╔══██╗",
        "███████╗███████╗██║     ██║  ██║   ██║   ██║  ██║",
        "╚══════╝╚══════╝╚═╝     ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝",
    ]

    info = [
        f"{ACCENT_COLOR}{BOLD}Agent{RESET}   Local AI Assistant",
        f"{ACCENT_COLOR}{BOLD}Version{RESET} {APP_VERSION}",
        f"{ACCENT_COLOR}{BOLD}Runtime{RESET} Linux",
        f"{ACCENT_COLOR}{BOLD}Status{RESET}  {SUCCESS_COLOR}● Ready{RESET}",
        f"{ACCENT_COLOR}{BOLD}Commands{RESET} salir · limpiar",
        "",
    ]

    print()
    for logo_line, info_line in zip(logo, info):
        print(f"{ZEPHYR_COLOR}{BOLD}{logo_line}{RESET}    {info_line}")
    print()


def print_system_message(message: str) -> None:
    print(f"\n{SYSTEM_COLOR}{BOLD}Sistema > {RESET}{message}\n")


def print_error(message: str) -> None:
    print(f"\n{ERROR_COLOR}{BOLD}Error > {RESET}{message}\n")


def print_zephyr_response(response: str) -> None:
    typing_delay = 0.030

    print(f"\n{ZEPHYR_COLOR}{BOLD}Zephyr >{RESET}")
    print("\033[?25l", end="", flush=True)

    try:
        for line in response.splitlines():
            print(f"{ACCENT_COLOR}│{RESET} ", end="", flush=True)
            for character in line:
                print(character, end="", flush=True)
                time.sleep(typing_delay)
            print()
    finally:
        print("\033[?25h", end="", flush=True)

    print()


def main() -> None:

    agent = ZephyrAgent()

    print_banner()

    while True:
        try:
            user_message = input(
                f"{USER_COLOR}{BOLD}Tú > {RESET}"
            ).strip()

        except KeyboardInterrupt:
            print_system_message("Zephyr fue interrumpido. Hasta luego.")
            break

        except EOFError:
            print_system_message("Entrada finalizada. Hasta luego.")
            break

        if not user_message:
            continue

        normalized_message = user_message.lower()

        if normalized_message in EXIT_COMMANDS:
            print_system_message(random_goodbye())
            break

        if normalized_message in CLEAR_COMMANDS:
            agent.clear_memory()
            print_system_message("Conversación eliminada.")
            continue

        spinner = Spinner()

        try:
            spinner.start()
            response = agent.run(user_message)
        except Exception as error:
            spinner.stop()
            print_error(str(error))
            continue

        spinner.stop()

        print_zephyr_response(response)


if __name__ == "__main__":
    main()
