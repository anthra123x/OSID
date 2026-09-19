#!/usr/bin/env python3
"""Parche para dnsrecon en Python >= 3.13 (urllib.FancyURLopener fue removido).

Reconstruye el bloque de imports de los módulos enum para que la herramienta
arranque en Python 3.13+. Idempotente: repara cualquier estado previo.
"""
import shutil
import subprocess
from pathlib import Path

SHIM = [
    "",
    "try:",
    "    url_opener = urllib.request.FancyURLopener",
    "except AttributeError:",
    "    class _CompatOpener:  # Python >= 3.13 eliminó FancyURLopener",
    "        version = \"Mozilla/5.0\"",
    "",
    "        def open(self, fullurl, data=None):  # noqa: A001",
    "            return urllib.request.urlopen(fullurl, data)",
    "",
    "    url_opener = _CompatOpener",
]

home = Path.home()
base = home / ".local/share/pipx/venvs/dnsrecon/lib"
if not base.exists():
    print("dnsrecon no está instalado por pipx; nada que parchear.")
    raise SystemExit(0)


def rebuild(path: Path) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    # índice donde arranca la clase AppURLopener
    start = next(
        (i for i, l in enumerate(lines) if l.startswith("class AppURLopener")),
        None,
    )
    if start is None:
        return "\n".join(lines)
    # bloque de imports = comentarios del encabezado + imports existentes,
    # garantizando siempre los básicos (urllib.request) aunque falten.
    base_imports = ["import re", "import time", "import urllib.request"]
    comments, found = [], []
    for l in lines[:start]:
        s = l.strip()
        if s.startswith("#"):
            comments.append(l)
            continue
        if s.startswith("import ") or s.startswith("from "):
            found.append(l)
            continue
        if not s:
            continue
        break  # primera línea de código: se acabó el bloque
    imports = []
    for l in base_imports + found:
        if l not in imports:
            imports.append(l)
    tail = lines[start:]
    return "\n".join(comments + imports + SHIM + [""] + tail) + "\n"


patched = 0
for py in sorted(base.iterdir()):
    for f in (py / "site-packages/dnsrecon/lib").glob("*enum.py"):
        before = f.read_text(encoding="utf-8")
        after = rebuild(f)
        if before != after:
            f.write_text(after, encoding="utf-8")
            patched += 1
            print(f"reparado: {f}")

if shutil.which("dnsrecon"):
    probe = subprocess.run(
        ["dnsrecon", "-h"], capture_output=True, text=True, timeout=30
    )
    bad = "FancyURLopener" in probe.stderr or "Traceback" in probe.stderr
    if not bad:
        print(f"OK: dnsrecon funcional ({patched} archivo(s) reparado(s)).")
    else:
        print("ERROR: dnsrecon sigue fallando:")
        print(probe.stderr[-500:])
        raise SystemExit(1)