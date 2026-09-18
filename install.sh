#!/bin/bash
# instalador automático del Toolkit OSINT
# uso: bash install.sh

set -e

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
BIN="$HOME/.local/bin"
SHARE="$HOME/.local/share"

GREEN='\033[32m'; CYAN='\033[36m'; YELLOW='\033[33m'; RED='\033[31m'; DIM='\033[2m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✔${NC} $1"; }
info() { echo -e "${CYAN}→${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
skip() { echo -e "${DIM}· $1 (ya presente, se omite)${NC}"; }

mkdir -p "$BIN"

need() { command -v "$1" >/dev/null 2>&1; }

# ── detección de distro ──────────────────────────────────────
distro=""
if [ -r /etc/os-release ]; then
    . /etc/os-release
    case "$ID_LIKE $ID" in
        *arch*|*cachyos*) distro="arch" ;;
        *debian*|*ubuntu*) distro="debian" ;;
    esac
fi

echo -e "${CYAN}═══ Toolkit OSINT — instalador automático ═══${NC}"
echo -e "${DIM}  Distribución detectada: ${distro:-indefinida}${NC}"
echo

# ── pipx + PATH ───────────────────────────────────────────────
if ! need pipx; then
    info "Instalando pipx..."
    if [ "$distro" = "arch" ]; then
        sudo pacman -S --noconfirm python-pipx
    elif [ "$distro" = "debian" ]; then
        sudo apt update && sudo apt install -y pipx
    else
        warn "Instalá pipx a mano y volvé a correr este script."
        exit 1
    fi
    pipx ensurepath >/dev/null 2>&1
    ok "pipx instalado"
else
    skip "pipx"
fi
case ":$PATH:" in *":$HOME/.local/bin:"*) ;; *) export PATH="$HOME/.local/bin:$PATH";; esac

pipx_install() {
    local name="$1"; shift
    if ! need "$name"; then
        info "Instalando $name..."
        pipx install "$@" >/dev/null
        ok "$name"
    else
        skip "$name"
    fi
}

# ── herramientas Python (pipx) ────────────────────────────────
pipx_install sherlock    sherlock-project
pipx_install holehe
pipx_install maigret
pipx_install h8mail
pipx_install theHarvester "git+https://github.com/laramies/theHarvester.git"
pipx_install dnsrecon

# ── metagoofil (git + venv, no es paquete pip) ────────────────
if ! need metagoofil; then
    info "Instalando metagoofil..."
    git clone -q --depth 1 https://github.com/opsdisk/metagoofil "$SHARE/metagoofil"
    python3 -m venv "$SHARE/metagoofil/venv"
    "$SHARE/metagoofil/venv/bin/pip" install -q -r "$SHARE/metagoofil/requirements.txt"
    cat > "$BIN/metagoofil" <<EOF
#!/bin/bash
exec "\$HOME/.local/share/metagoofil/venv/bin/python" "\$HOME/.local/share/metagoofil/metagoofil.py" "\$@"
EOF
    chmod +x "$BIN/metagoofil"
    ok "metagoofil"
else
    skip "metagoofil"
fi

# ── binarios Go (GitHub releases) ─────────────────────────────
go_get() {
    local repo="$1" bin="$2" pattern="$3" sub="$4"
    if need "$bin"; then skip "$bin"; return; fi
    info "Descargando $bin..."
    local tag
    tag="$(curl -sI -o /dev/null -w '%{redirect_url}' "https://github.com/$repo/releases/latest" | sed 's#.*/tag/##')"
    test -n "$tag" || tag="latest"
    local arch="amd64"
    case "$(uname -m)" in aarch64|arm64) arch="arm64";; esac
    local url="https://github.com/$repo/releases/download/$tag/$(printf "$pattern" "$tag" "$arch")"
    curl -sL "$url" -o /tmp/osint_dl.tmp
    case "$url" in
        *.zip) python3 -c "import zipfile; z=zipfile.ZipFile('/tmp/osint_dl.tmp'); [z.extract(n,'/tmp/osint_dl') for n in z.namelist() if n.endswith(('$bin','$bin.exe')) or n=='$sub']" ;;
        *.tar.gz) tar -xzf /tmp/osint_dl.tmp -C /tmp/osint_dl ;;
    esac
    chmod +x "/tmp/osint_dl/$sub"
    mv "/tmp/osint_dl/$sub" "$BIN/$bin"
    rm -rf /tmp/osint_dl /tmp/osint_dl.tmp
    ok "$bin"
}

go_get sundowndev/phoneinfoga phoneinfoga   "phoneinfoga_Linux_%s.tar.gz"            "phoneinfoga"
go_get projectdiscovery/subfinder subfinder "subfinder_%s_linux_%s.zip"              "subfinder"
go_get projectdiscovery/httpx httpx         "httpx_%s_linux_%s.zip"                  "httpx"

# ── paquetes del sistema ─────────────────────────────────────
pkg_install() {
    for p in "$@"; do
        if need "$p"; then skip "$p"; else
            info "Instalando $p..."
            if [ "$distro" = "arch" ]; then
                if command -v paru >/dev/null 2>&1; then
                    paru -S --noconfirm --needed "$p" >/dev/null
                else
                    sudo pacman -S --noconfirm "$p" >/dev/null 2>&1 || warn "$p no está en los repos oficiales (probalo con paru/yay)."
                fi
            elif [ "$distro" = "debian" ]; then
                sudo apt install -y "$p" >/dev/null
            else
                warn "Instalá $p con el gestor de tu distro."
            fi
            ok "$p"
        fi
    done
}
pkg_install whatweb dnsrecon
# exiftool
if need exiftool; then skip "exiftool"; else
    info "Instalando exiftool..."
    if [ "$distro" = "arch" ]; then sudo pacman -S --noconfirm perl-image-exiftool >/dev/null
    elif [ "$distro" = "debian" ]; then sudo apt install -y libimage-exiftool-perl >/dev/null
    else warn "Instalá exiftool con el gestor de tu distro."; fi
    ok "exiftool"
fi

# ── la propia app ─────────────────────────────────────────────
info "Instalando la app (osint-menu)..."
if [ ! -d "$APP_DIR/.git" ]; then
    warn "$APP_DIR no parece ser el repo; instalando igual."
fi
pipx install --editable --force "$APP_DIR" >/dev/null 2>&1 || pipx install --editable "$APP_DIR" >/dev/null
ok "osint-menu instalado"

echo
echo -e "${GREEN}═══ Instalación completa ═══${NC}"
echo "  Ejecutá  osint-menu  para abrir el menú."
echo "  Reportes e historial se guardan en ~/osint-toolkit/resultados (local de este equipo)."
echo
echo -e "${CYAN}  Estado:${NC}"
missing=0
for t in osint-menu phoneinfoga sherlock maigret theHarvester holehe h8mail subfinder httpx dnsrecon whatweb exiftool metagoofil; do
    if need "$t"; then echo -e "    ${GREEN}✔${NC} $t"; else echo -e "    ${RED}✘${NC} $t"; missing=1; fi
done
[ "$missing" = "1" ] && echo -e "${YELLOW}  Revisá los errores o instalá los faltantes a mano.${NC}"