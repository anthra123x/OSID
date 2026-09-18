"""Registro central de herramientas OSINT.

Cada herramienta es un dict con:
  name        : clave corta usada en el menú
  title       : nombre visible
  binary      : ejecutable en PATH
  category    : categoría del menú
  desc        : qué hace (para que el usuario entienda)
  limits      : qué NO hace / advertencias
  example     : valor de ejemplo para el input
  input_label : qué se le pide al usuario
  runner      : argumentos para subprocess (shlex) con espacio {input}
  takes_input : False para herramientas sin input (ej: servidor web)
"""

CATEGORIES = [
    "📞  Números de teléfono",
    "👤  Usuarios y redes sociales",
    "✉️  Emails",
    "🌐  Dominios",
    "🖼️  Fotos y metadatos",
    "🧰  Panel web",
]

TOOLS = [
    # ── Números de teléfono ──────────────────────────────
    dict(
        name="phoneinfoga",
        title="PhoneInfoga",
        binary="phoneinfoga",
        category=CATEGORIES[0],
        desc="Investiga un número de teléfono: país de origen, operador, "
             "linea móvil/fija, formato válido y referencia en bases públicas.",
        limits="NO da ubicación GPS ni rastrea el celular en tiempo real. "
               "Solo datos públicos y reputación en blocklists.",
        example="+573234733415",
        input_label="Número (con país, ej: +57...)",
        runner="phoneinfoga scan -n {input}",
        takes_input=True,
    ),
    # ── Usuarios y redes sociales ────────────────────────
    dict(
        name="sherlock",
        title="Sherlock",
        binary="sherlock",
        category=CATEGORIES[1],
        desc="Busca un nombre de usuario en más de 350 plataformas y redes "
             "sociales, indicando en cuáles existe una cuenta.",
        limits="La cuenta puede ser otra persona con el mismo nombre. "
               "Es lento porque revisa cientos de sitios.",
        example="juanperez",
        input_label="Nombre de usuario",
        runner="sherlock {input}",
        takes_input=True,
    ),
    # ── Emails ───────────────────────────────────────────
    dict(
        name="holehe",
        title="Holehe",
        binary="holehe",
        category=CATEGORIES[2],
        desc="Comprueba si una dirección de email está registrada en "
             "plataformas (Google, Spotify, LinkedIn, etc.) sin enviar emails.",
        limits="Solo indica registros visibles desde públicos. Algunos sitios "
               "bloquean este tipo de consultas.",
        example="alguien@gmail.com",
        input_label="Dirección de email",
        runner="holehe {input}",
        takes_input=True,
    ),
    # ── Dominios ─────────────────────────────────────────
    dict(
        name="theharvester",
        title="theHarvester",
        binary="theHarvester",
        category=CATEGORIES[3],
        desc="Reúne emails, nombres de hosts y subdominios asociados a un "
             "dominio usando motores de búsqueda públicos.",
        limits="Resultados dependen de los motores y pueden tardar. "
               "No todos aceptan consultas ilimitadas.",
        example="ejemplo.com",
        input_label="Dominio (sin http://)",
        runner="theHarvester -d {input} -b all",
        takes_input=True,
    ),
    dict(
        name="subfinder",
        title="Subfinder",
        binary="subfinder",
        category=CATEGORIES[3],
        desc="Enumera subdominios ocultos de un dominio usando fuentes pasivas "
             "de internet (certificados, DNS, etc.).",
        limits="Solo subdominios públicos indexados; no descubre todo.",
        example="ejemplo.com",
        input_label="Dominio (sin http://)",
        runner="subfinder -d {input} -silent",
        takes_input=True,
    ),
    # ── Fotos y metadatos ────────────────────────────────
    dict(
        name="exiftool",
        title="ExifTool",
        binary="exiftool",
        category=CATEGORIES[4],
        desc="Lee los metadatos EXIF de una foto: cámara, fecha, software y, "
             "si la imagen los guarda, coordenadas GPS del lugar donde se tomó.",
        limits="Muchas apps y redes borran los metadatos al compartir. "
               "Solo funciona si la foto original los conserva.",
        example="/ruta/a/foto.jpg",
        input_label="Ruta del archivo de imagen",
        runner="exiftool {input}",
        takes_input=True,
    ),
    # ── Panel web ────────────────────────────────────────
    dict(
        name="webui",
        title="PhoneInfoga Web",
        binary="phoneinfoga",
        category=CATEGORIES[5],
        desc="Levanta un panel web local (navegador) para usar PhoneInfoga "
             "con interfaz gráfica. Se detiene con Ctrl+C.",
        limits="No genera resultados nuevos: es la misma herramienta en web.",
        example="",
        input_label="",
        runner="phoneinfoga serve",
        takes_input=False,
    ),
]