# OSID — Toolkit OSINT interactivo para terminal

Lanzador interactivo de herramientas OSINT para Linux. Un solo menú en la
terminal reúne varias herramientas de inteligencia de fuentes abiertas
(Open Source Intelligence), con la descripción de cada una, sus limitaciones,
ejemplos de uso y manejo de errores.

![interfaz](https://img.shields.io/badge/menu-interactivo-cyan) ![python](https://img.shields.io/badge/Python-3.10+-blue) ![license](https://img.shields.io/badge/license-MIT-green)

## Qué incluye

| Categoría | Herramienta | Qué hace |
|-----------|-------------|----------|
| 📞 Números de teléfono | PhoneInfoga | País de origen, operador, formato válido y reputación en bases públicas |
| 👤 Usuarios | Sherlock | Busca un nombre de usuario en +350 redes sociales |
| ✉️ Emails | Holehe | Detecta en qué plataformas está registrada una dirección de email |
| 🌐 Dominios | theHarvester | Emails, hosts y subdominios asociados a un dominio |
| 🌐 Dominios | Subfinder | Enumeración pasiva de subdominios |
| 🖼️ Fotos | ExifTool | Metadatos EXIF de imágenes (cámara, fecha, GPS si están presentes) |
| 🧰 Panel web | PhoneInfoga serve | Interfaz web local para PhoneInfoga |

Cada herramienta muestra al seleccionarla una **ficha** con su descripción,
sus limitaciones y un ejemplo del dato que necesita.

## Instalación

### 1. Herramientas OSINT

Instaladas en `~/.local/bin` (pipx) o por el gestor de paquetes:

```bash
# Números de teléfono
pipx install phoneinfoga          # o binario desde GitHub releases

# Usuarios
pipx install sherlock-project

# Emails
pipx install holehe

# Dominios
pipx install theHarvester         # desde git
pipx install "git+https://github.com/laramies/theHarvester.git"
# subfinder (binario desde GitHub releases de projectdiscovery)

# Metadatos
sudo pacman -S perl-image-exiftool   # Arch/CachyOS (exiftool)
sudo apt install libimage-exiftool-perl  # Debian/Ubuntu
```

### 2. La app

```bash
pipx install --editable ~/osint-toolkit
osint-menu
```

## Uso

```bash
osint-menu
```

- Elegí una opción del menú (tecleando el número) o `h` para el glosario.
- La app te pide el dato (número, usuario, email, dominio o ruta de imagen),
  muestra la ficha de la herramienta y la ejecuta en vivo.
- `0` para salir. `Ctrl+C` interrumpe cualquier ejecución.

## Agregar herramientas propias

Edita el registro en `osint_toolkit/tools.py` y agregá un dict con la información
de la herramienta. El menú la muestra automáticamente. No hace falta tocar la
lógica del launcher.

```python
dict(
    name="mi-tool",
    title="Mi Tool",
    binary="mi-tool",
    category=CATEGORIES[2],
    desc="Qué hace...",
    limits="Qué no hace...",
    example="dato-de-ejemplo",
    input_label="Qué se pide al usuario",
    runner="mi-tool {input}",
    takes_input=True,
)
```

## Estructura del proyecto

```
osint-toolkit/
├── pyproject.toml               # empaquetado + entry point (osint-menu)
└── osint_toolkit/
    ├── __init__.py
    ├── cli.py                   # launcher, menú y ejecución
    ├── tools.py                 # registro de herramientas (data-driven)
    └── ui.py                    # colores, banner y helpers de interfaz
```

## Aviso legal

Este proyecto es una herramienta de **investigación de fuentes abiertas**.
Úsala solo sobre datos propios o con autorización. La recopilación de
información pública no otorga derechos sobre las personas a las que pertenecen
esos datos. El uso de estas herramientas no localiza dispositivos en tiempo
real ni accede a información privada. El autor no se responsabiliza por el uso
indebido.

## Licencia

MIT