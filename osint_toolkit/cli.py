"""osint-menu: lanzador interactivo del toolkit OSINT."""

import shlex
import shutil
import subprocess
import sys

from osint_toolkit import tools
from osint_toolkit.ui import (
    BANNER,
    banner,
    c,
    clear,
    color_category,
    confirm_exit,
    header,
    pause,
    tool_card,
)


def expand_path() -> None:
    """Asegura que ~/.local/bin (pipx) esté en PATH para los hijos."""
    local_bin = f"{__import__('os').path.expanduser('~')}/.local/bin"
    parts = __import__("os").environ.get("PATH", "").split(":")
    if local_bin not in parts:
        __import__("os").environ["PATH"] = ":".join(parts + [local_bin])


def find_binary(binary: str) -> str | None:
    return shutil.which(binary) or shutil.which(
        f"{__import__('os').path.expanduser('~')}/.local/bin/{binary}"
    )


def show_menu() -> None:
    banner()
    print(c("bold", "  SELECCIONÁ UNA CATEGORÍA"))
    print(c("dim", "  ─────────────────────────────"))
    idx = 0
    for cat in tools.CATEGORIES:
        print(f"  {color_category(cat)}")
        for t in tools.TOOLS:
            if t["category"] == cat:
                idx += 1
                name = c("bold", f"[{idx}]")
                title = c("cyan", t["title"])
                print(f"      {name} {title} — {c('dim', t['desc'])}")
    print(c("dim", "  ─────────────────────────────"))
    print(f'  {c("bold", "[h]")} {c("cyan", "Ayuda / glosario")}')
    print(f'  {c("bold", "[0]")} {c("cyan", "Salir")}')
    print()


def tool_by_idx() -> dict:
    idx = 0
    for cat in tools.CATEGORIES:
        for t in tools.TOOLS:
            if t["category"] == cat:
                idx += 1
                yield idx, t


def run_tool(t: dict) -> None:
    clear()
    tool_card(t)

    binary = find_binary(t["binary"])
    if not binary:
        print(c("err", f'  ⚠ Herramienta "{t["binary"]}" no está instalada.'))
        print(c("warn", f'  Instalala con: pipx install {t["binary"]}  (o pacman)'))
        pause()
        return

    value = ""
    if t["takes_input"]:
        try:
            value = input(c("bold", f'  {t["input_label"]} > ')).strip()
        except (KeyboardInterrupt, EOFError):
            return
        if not value:
            print(c("warn", "  Sin entrada, se cancela."))
            pause()
            return

    args = shlex.split(t["runner"].replace("{input}", value))
    print(c("dim", f"\n  $ {' '.join(args)}"))
    print(c("cyan", "─" * 64))
    try:
        subprocess.run(args, check=False)
    except FileNotFoundError:
        print(c("err", f'  No se pudo ejecutar "{args[0]}".'))
    except KeyboardInterrupt:
        print(c("warn", "\n  Ejecución interrumpida."))
    print(c("cyan", "─" * 64))
    pause()


def show_help() -> None:
    clear()
    banner()
    header("GLOSARIO DE HERRAMIENTAS")
    for cat in tools.CATEGORIES:
        print()
        print(f"  {color_category(cat)}")
        for t in tools.TOOLS:
            if t["category"] == cat:
                print(c("bold", f'    • {t["title"]}') + f'   {c("dim", f"({t["binary"]})")}')
                print(f'        {t["desc"]}')
                print(c("warn", f'        ⚠ {t["limits"]}'))
                print()
    pause()


def main() -> None:
    expand_path()
    installs = sum(1 for t in tools.TOOLS if find_binary(t["binary"]))
    total = len(tools.TOOLS)
    if installs < total:
        print(c("warn", f"  ⚠ Herramientas disponibles: {installs}/{total}"))
        print(c("warn", "    Faltantes se indican al elegirlas, con cómo instalarlas.\n"))

    tools_list = list(tool_by_idx())

    while True:
        show_menu()
        try:
            option = input(c("bold", "  Opción > ")).strip().lower()
        except (KeyboardInterrupt, EOFError):
            print()
            break
        if option in ("0", "q", "salir", "exit"):
            if confirm_exit():
                print(c("dim", "  Hasta la próxima. 👋"))
                break
            continue
        if option in ("h", "help", "ayuda", "?"):
            show_help()
            continue
        if not option.isdigit():
            continue
        sel = int(option)
        entry = next((t for i, t in tools_list if i == sel), None)
        if entry is None:
            continue
        run_tool(entry)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        sys.exit(130)