"""osint-menu: lanzador interactivo del toolkit OSINT.

Funciones: menú interactivo, ficha por herramienta, reportes guardados por
equipo (historial), modo batch (varios datos a la vez), modo directo
(osint-menu <tool> <dato>) y configuración de API keys por equipo.
"""

import json
import os
import shlex
import shutil
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path

from osint_toolkit import __version__, tools
from osint_toolkit.ui import (
    banner,
    c,
    clear,
    color_category,
    confirm_exit,
    header,
    pause,
    tool_card,
)

# ── Rutas locales por equipo ─────────────────────────────
HOME = Path.home()
CONFIG_PATH = Path(
    os.environ.get("OSINT_CONFIG")
    or f"{HOME}/.config/osint/config.json"
)
RESULTS_ROOT = Path(
    os.environ.get("OSINT_RESULTS") or f"{HOME}/osint-toolkit/resultados"
)
HISTORY_FILE = RESULTS_ROOT / "historial.tsv"


def load_config() -> dict:
    """Lee la config local del equipo: env de API keys y rutas opcionales."""
    cfg = {}
    if CONFIG_PATH.exists():
        try:
            cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    results = cfg.get("resultados", "")
    if results:
        globals()["RESULTS_ROOT"] = Path(
            results.replace("~", str(HOME))).expanduser()
        globals()["HISTORY_FILE"] = RESULTS_ROOT / "historial.tsv"
    RESULTS_ROOT.mkdir(parents=True, exist_ok=True)
    return cfg


def expand_path() -> None:
    local_bin = f"{HOME}/.local/bin"
    parts = os.environ.get("PATH", "").split(":")
    if local_bin not in parts:
        os.environ["PATH"] = ":".join(parts + [local_bin])


def find_binary(binary: str) -> str | None:
    return shutil.which(binary) or shutil.which(f"{HOME}/.local/bin/{binary}")


def parse_inputs(value: str) -> list[str]:
    """Soporta: un dato, varios separados por comas, o un archivo con @archivo."""
    value = value.strip()
    if not value:
        return []
    if value.startswith("@"):
        path = Path(value[1:]).expanduser()
        if not path.exists():
            return []
        return [ln.strip() for ln in path.read_text().splitlines() if ln.strip()]
    if "," in value:
        return [x.strip() for x in value.split(",") if x.strip()]
    return [value]


def record_history(t: dict, value: str, status: str, log: str) -> None:
    """Agrega una entrada al historial local del equipo."""
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    new = not HISTORY_FILE.exists()
    with open(HISTORY_FILE, "a", encoding="utf-8") as fh:
        if new:
            fh.write("fecha\therramienta\tentrada\testado\treporte\n")
        fh.write(f"{datetime.now():%F %T}\t{t['title']}\t{value}\t{status}\t{log}\n")


def child_env(cfg: dict) -> dict:
    """Environment para procesos hijos: el del sistema + API keys del equipo."""
    env = os.environ.copy()
    env.update(cfg.get("env", {}))
    return env


def run_process(args: list[str], env: dict, log_path: Path) -> int:
    """Ejecuta con salida en vivo (tee) y guarda todo en el reporte."""
    with open(log_path, "a", encoding="utf-8") as log:
        proc = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=env,
        )
        try:
            assert proc.stdout is not None
            for line in proc.stdout:
                sys.stdout.write(line)
                sys.stdout.flush()
                log.write(line)
            proc.wait()
        except KeyboardInterrupt:
            proc.terminate()
            proc.wait()
            print(c("warn", "\n  Ejecución interrumpida."))
            return 130
    return proc.returncode


def run_tool(t: dict, cfg: dict, value: str | None = None) -> None:
    clear()
    tool_card(t)

    binary = find_binary(t["binary"])
    if not binary:
        print(c("err", f'  ⚠ Herramienta "{t["binary"]}" no está instalada.'))
        print(c("warn", f'  Instalala con: pipx install {t["binary"]}  (o consultá install.sh)'))
        pause()
        return

    inputs = [value] if value else None
    if inputs is None and t["takes_input"]:
        try:
            raw = input(c("bold", f'  {t["input_label"]} > ')).strip()
        except (KeyboardInterrupt, EOFError):
            return
        inputs = parse_inputs(raw)
        if not inputs:
            print(c("warn", "  Sin entrada, se cancela."))
            pause()
            return
    elif inputs is None:
        inputs = [""]

    for each in inputs:
        # Herramientas interactivas (TUI / servidores web) heredan la
        # terminal directamente: no se guarda salida, solo el comando.
        if t.get("interactive"):
            args_it = shlex.split(t["runner"].replace("{input}", each))
            print(c("dim", f"\n  $ {' '.join(args_it)}"))
            print(c("cyan", "─" * 64))
            url = t.get("url")
            if url:
                print(c("bold", "  🌐 Panel disponible en:"))
                print(c("ok", f"    {url}"))
                print(c("dim", "  (Ctrl+C detiene el servidor)"))
                print(c("cyan", "─" * 64))
                if shutil.which("xdg-open"):
                    threading.Timer(
                        2.0,
                        lambda: subprocess.Popen(
                            ["xdg-open", url],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        ),
                    ).start()
            try:
                sys.stdout.flush()
                code = subprocess.run(args_it, env=child_env(cfg)).returncode
            except KeyboardInterrupt:
                code = 130
            print(c("cyan", "─" * 64))
            record_history(t, each, "ok" if code == 0 else f"salida {code}", "interactivo")
            print(c("ok", "  📄 Sesión interactiva finalizada."))
            pause()
            return

        stamp = datetime.now().strftime("%H%M%S-%f")[:-3]
        date_dir = datetime.now().strftime("%Y-%m-%d")
        run_dir = RESULTS_ROOT / date_dir / f"{t['name']}-{stamp}"
        run_dir.mkdir(parents=True, exist_ok=True)
        log_path = run_dir / "salida.txt"

        args_t = t["runner"].replace("{input}", each).replace(
            "{out}", str(run_dir))
        args = shlex.split(args_t)
        (run_dir / "comando.txt").write_text(" ".join(args), encoding="utf-8")
        if each:
            (run_dir / "entrada.txt").write_text(each, encoding="utf-8")

        print(c("dim", f"\n  $ {' '.join(args)}"))
        print(c("cyan", "─" * 64))
        code = run_process(args, child_env(cfg), log_path)
        print(c("cyan", "─" * 64))
        status = "ok" if code == 0 else f"salida {code}"
        record_history(t, each, status, str(log_path))
        print(c("ok", f"  📄 Reporte guardado: {run_dir}"))

    pause()


def tool_by_idx() -> list[tuple[int, dict]]:
    idx = 0
    out = []
    for cat in tools.CATEGORIES:
        for t in tools.TOOLS:
            if t["category"] == cat:
                idx += 1
                out.append((idx, t))
    return out


TOOLS_LIST = tool_by_idx()


def find_tool(key: str) -> dict | None:
    key = key.lower()
    return next(
        (t for _, t in TOOLS_LIST if t["name"] == key or t["title"].lower() == key),
        None,
    )


def show_menu() -> None:
    banner()
    print(c("bold", "  SELECCIONÁ UNA CATEGORÍA"))
    print(c("dim", "  ─────────────────────────────"))
    for cat in tools.CATEGORIES:
        print(f"  {color_category(cat)}")
        for t in tools.TOOLS:
            if t["category"] == cat:
                idx = next(i for i, tt in TOOLS_LIST if tt is t)
                name = c("bold", f"[{idx}]")
                title = c("cyan", t["title"])
                print(f"      {name} {title} — {c('dim', t['desc'])}")
    print(c("dim", "  ─────────────────────────────"))
    print(f'  {c("bold", "[v]")} {c("cyan", "Ver historial / reportes")}')
    print(f'  {c("bold", "[h]")} {c("cyan", "Ayuda / glosario")}')
    print(f'  {c("bold", "[0]")} {c("cyan", "Salir")}')
    print(c("dim", "  Tip: osint-menu <herramienta> <dato> para uso directo"))
    print()


def show_history() -> None:
    clear()
    banner()
    header("HISTORIAL DE REPORTES")
    print(c("dim", f"  Ubicación: {RESULTS_ROOT}\n"))
    if not HISTORY_FILE.exists():
        print(c("warn", "  Aún no hay historial en este equipo."))
        pause()
        return
    lines = HISTORY_FILE.read_text(encoding="utf-8").splitlines()
    header_line = lines[0]
    entries = [ln.split("\t") for ln in lines[1:] if ln.strip()]
    print(c("bold", f"  Últimas {min(len(entries), 15)} búsquedas:\n"))
    for row in entries[-15:][::-1]:
        fecha, tool, entrada, estado, reporte = (row + [""] * 5)[:5]
        color = "ok" if estado == "ok" else "warn"
        print(f"  {c('dim', fecha)}  {c('cyan', tool):<16} "
              f"{c('bold', entrada[:28]):<30} "
              f"{c(color, estado):<9} {c('dim', reporte)}")
    print()
    print(c("dim", "  El historial se guarda local en cada equipo donde se usa."))
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
                print(c("bold", f'    • {t["title"]}') + f'   {c("dim", f"({t["name"]})")}')
                print(f'        {t["desc"]}')
                print(c("warn", f'        ⚠ {t["limits"]}'))
                print()
    pause()


def direct_mode(t: dict, raw: str) -> None:
    cfg = load_config()
    inputs = parse_inputs(raw) if t["takes_input"] else [""]
    if not inputs:
        print(c("err", "  Falta el dato de entrada (modo directo)."))
        return
    for each in inputs:
        run_tool(t, cfg, each or None)


def main() -> None:
    expand_path()

    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ("-v", "--version", "version"):
            print(f"osint-toolkit v{__version__}")
            return
        tool = find_tool(arg)
        if not tool:
            print(c("err", f'  Herramienta desconocida: "{arg}"'))
            print(c("dim", "  Disponibles: " + ", ".join(t["name"] for t in tools.TOOLS)))
            sys.exit(1)
        direct_mode(tool, sys.argv[2] if len(sys.argv) > 2 else "")
        return

    env = load_config()
    if CONFIG_PATH.exists():
        print(c("dim", f"  Config cargada: {CONFIG_PATH}"))

    installs = sum(1 for t in tools.TOOLS if find_binary(t["binary"]))
    total = len(tools.TOOLS)
    if installs < total:
        print(c("warn", f"  ⚠ Herramientas disponibles: {installs}/{total}"))
        print(c("warn", "    Faltantes se indican al elegirlas (o usá install.sh).\n"))

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
        if option in ("v", "historial", "reportes"):
            show_history()
            continue
        if option in ("h", "help", "ayuda", "?"):
            show_help()
            continue
        if option.isdigit():
            entry = next((t for i, t in TOOLS_LIST if i == int(option)), None)
            if entry is not None:
                run_tool(entry, env)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        sys.exit(130)