# OSID — Toolkit OSINT interactivo para terminal

Lanzador interactivo de herramientas OSINT para Linux. Un solo menú en la
terminal reúne herramientas de inteligencia de fuentes abiertas (Open Source
Intelligence), con la descripción de cada una, sus limitaciones, ejemplos de
uso y reportes guardados automáticamente.

![interfaz](https://img.shields.io/badge/menu-interactivo-cyan) ![python](https://img.shields.io/badge/Python-3.10+-blue) ![license](https://img.shields.io/badge/license-MIT-green)

## Qué incluye

| Categoría | Herramienta | Qué hace |
|-----------|-------------|----------|
| 📞 Números de teléfono | PhoneInfoga | País de origen, operador, formato válido y reputación en bases públicas |
| 👤 Usuarios | Sherlock | Busca un nombre de usuario en +350 redes sociales |
| 👤 Usuarios | Maigret | Busca usuario en miles de fuentes y arma un perfil (complementa a Sherlock) |
| ✉️ Emails | Holehe | Detecta en qué plataformas está registrada una dirección de email |
| ✉️ Emails | h8mail | Cruza un email con bases de brechas y fuentes públicas |
| 🌐 Dominios | theHarvester | Emails, hosts y subdominios asociados a un dominio |
| 🌐 Dominios | Subfinder | Enumeración pasiva de subdominios |
| 🌐 Dominios | Httpx | Prueba qué hosts responden: estado, título, tecnologías |
| 🌐 Dominios | DNSRecon | Registros DNS: MX, TXT, NS, SOA y transferencia de zona |
| 🕸️ Sitios | WhatWeb | Detecta CMS, servidor, framework y plugins de un sitio |
| 🖼️ Metadatos | ExifTool | Metadatos EXIF de imágenes (cámara, fecha, GPS si están presentes) |
| 🖼️ Metadatos | Metagoofil | Descarga documentos públicos de un dominio y extrae sus metadatos |
| 🔍 Frameworks | SpiderFoot | Motor OSINT automatizado: cientos de módulos y correlaciones cruzadas |
| 🔍 Frameworks | Sn0int | Framework OSINT semi-automatizado con TUI (IPs, dominios, personas, fotos) |
| 🔍 Frameworks | GHunt | OSINT de cuentas Google a partir de un email (perfil, avatar, actividad) |
| 🧰 Panel web | PhoneInfoga serve | Interfaz web local para PhoneInfoga |
| 🧰 Panel web | SpiderFoot Web | Panel web de SpiderFoot con mapa de correlaciones |

Cada herramienta muestra al seleccionarla una **ficha** con su descripción,
sus limitaciones y un ejemplo del dato que necesita.

## Instalación automática

```bash
git clone git@github.com:anthra123x/OSID.git ~/osint-toolkit
cd ~/osint-toolkit
bash install.sh
osint-menu
```

`install.sh` instala todas las herramientas (pipx, binarios de GitHub y
paquetes del sistema según tu distro) y la propia app. Es idempotente: no
reinstala lo que ya está.

## Uso

**Modo menú:**
```bash
osint-menu
```
- Elegí una opción con su número, o `v` para ver el historial, `h` para el
  glosario, `0` para salir. `Ctrl+C` interrumpe cualquier ejecución.

**Modo directo** (para scripts o atajos):
```bash
osint-menu phoneinfoga +573234733415
osint-menu sherlock juanperez
osint-menu exiftool /ruta/foto.jpg
```

**Modo batch** (varios datos a la vez):
```bash
osint-menu holehe "a@gmail.com, b@gmail.com, c@gmail.com"
osint-menu subfinder "@lista-de-dominios.txt"   # un dominio por línea
```

## Reportes e historial (local por equipo)

Cada búsqueda se guarda automáticamente en el equipo donde se ejecuta (nada
se sube a internet):

```
~/osint-toolkit/resultados/
├── historial.tsv            # registro de todas las búsquedas
└── AAAA-MM-DD/
    └── <herramienta>-<hora>/
        ├── comando.txt      # comando ejecutado
        ├── entrada.txt      # dato buscado
        └── salida.txt       # salida completa de la herramienta
```

La opción `v` del menú muestra las últimas búsquedas de ese equipo.

## Configuración

La config se lee de `~/.config/osint/config.json` (por equipo). Copiá
`config.example.json` y completá tus API keys:

```json
{
  "resultados": "~/osint-toolkit/resultados",
  "env": {
    "HIBP_API_KEY": "...",     // ayuda a h8mail (brechas)
    "GITHUB_API_KEY": "...",   // h8mail y otras
    "HUNTER_API_KEY": "..."    // búsqueda de emails
  }
}
```

Las variables de `env` se inyectan a cada herramienta al ejecutarla.
`resultados` cambia la carpeta donde se guardan los reportes.
También se pueden pasar por entorno: `OSINT_CONFIG` y `OSINT_RESULTS`.

## Agregar herramientas propias

Editá el registro en `osint_toolkit/tools.py` y agregá un dict. El menú la
muestra automáticamente. Soporta los marcadores:

- `{input}` — el dato ingresado
- `{out}` — directorio del reporte actual (para tools que guardan archivos)

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
├── install.sh                  # instalador automático
├── pyproject.toml              # empaquetado + entry point (osint-menu)
├── config.example.json         # plantilla de API keys
└── osint_toolkit/
    ├── __init__.py
    ├── cli.py                  # menú, ejecución, reportes y modos
    ├── tools.py                # registro de herramientas (data-driven)
    └── ui.py                   # colores, banner y helpers de interfaz
```

## Aviso legal

Este proyecto es una herramienta de **investigación de fuentes abiertas**.
Úsala solo sobre datos propios o con autorización. La recopilación de
información pública no otorga derechos sobre las personas a las que pertenecen
esos datos. El uso de estas herramientas no localiza dispositivos en tiempo
real ni accede a información privada. El autor no se responsabiliza por el uso
indebido.

## Licencia

MIT — © 2026 anthra123x. Ver archivo [LICENSE](LICENSE).