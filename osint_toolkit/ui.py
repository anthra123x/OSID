"""Utilidades de interfaz de terminal: colores, banner y helpers."""

import os


def _rgb(r: int, g: int, b: int) -> str:
    return f"\033[38;2;{r};{g};{b}m"


COL = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "ok": "\033[32m",
    "warn": "\033[33m",
    "err": "\033[31m",
    "cyan": "\033[36m",
    "magenta": "\033[35m",
    "phone": _rgb(255, 205, 88),
    "user": _rgb(94, 226, 231),
    "email": _rgb(138, 226, 148),
    "domain": _rgb(138, 144, 255),
    "photo": _rgb(255, 158, 220),
    "web": _rgb(109, 212, 160),
}


def c(code: str, text: str) -> str:
    return f"{COL[code]}{text}{COL['reset']}"


BANNER = r"""
   ██████  ███████ ██  ████
  ██    ██ ██      ██  ██  ██
  ██    ██ ███████ ██  ██  ██   Toolkit OSINT
  ██    ██      ██ ██  ██  ██
   ██████  ███████ ██ ██████    herramientas de terminal
"""


def banner() -> None:
    clear()
    print(c("domain", BANNER.rstrip("\n")))
    print(c("dim", "  Recopilación de información de código abierto — uso responsable."))
    print()


def clear() -> None:
    os.system("clear" if os.name != "nt" else "cls")


def header(text: str) -> None:
    width = 64
    print()
    print(c("bold", c("cyan", "─" * width)))
    print(c("bold", text.center(width)))
    print(c("cyan", "─" * width))


def tool_card(t: dict) -> None:
    """Ficha informativa de una herramienta."""
    header(c("bold", t["title"]))
    print(c("ok", "  ▸ QUÉ HACE:") + " " + t["desc"])
    print(c("warn", "  ▸ LIMITACIONES:") + " " + t["limits"])
    if t["takes_input"]:
        print(c("cyan", "  ▸ EJEMPLO:") + f'  {c("bold", t["example"])}')
    print(c("cyan", "  ▸ COMANDO:"),
          f'  {c("dim", t["runner"].format(input=t["example"]))}')
    print()


def pause() -> None:
    print()
    try:
        input(c("dim", "  [Enter] para volver al menú..."))
    except (KeyboardInterrupt, EOFError):
        pass


def confirm_exit() -> bool:
    try:
        ans = input(c("warn", "  ¿Salir? [s/N]: ")).strip().lower()
    except (KeyboardInterrupt, EOFError):
        return True
    return ans in ("s", "si", "y", "yes", "sí")


def color_category(cat: str) -> str:
    """Aplica color según el emoji/tema de la categoría."""
    cid = cat.split(" ")[0]
    theme = {
        "📞": "phone",
        "👤": "user",
        "✉️": "email",
        "🌐": "domain",
        "🕸️": "web",
        "🖼️": "photo",
        "🧰": "web",
    }.get(cid, "cyan")
    return c(theme, cat)