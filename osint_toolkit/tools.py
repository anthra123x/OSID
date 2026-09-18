"""Registro central de herramientas OSINT.

Cada herramienta es un dict con:
  name        : clave corta usada en el menú y modo directo
  title       : nombre visible
  binary      : ejecutable en PATH
  category    : categoría del menú
  desc        : qué hace (para que el usuario entienda)
  limits      : qué NO hace / advertencias
  example     : valor de ejemplo para el input
  input_label : qué se le pide al usuario
  runner      : argumentos para subprocess con espacios {input} y {out}
                ({out} se reemplaza por el directorio del reporte actual)
  takes_input : False para herramientas sin input (ej: servidor web)
"""

CATEGORIES = [
    "📞  Números de teléfono",
    "👤  Usuarios y redes sociales",
    "✉️  Emails",
    "🌐  Dominios y subdominios",
    "🕸️  Sitios y tecnología",
    "🖼️  Metadatos (fotos y archivos)",
    "🔍  Frameworks OSINT",
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
        limits="La cuenta puede ser de otra persona con el mismo nombre. "
               "Es lento porque revisa cientos de sitios.",
        example="juanperez",
        input_label="Nombre de usuario",
        runner="sherlock {input}",
        takes_input=True,
    ),
    dict(
        name="maigret",
        title="Maigret",
        binary="maigret",
        category=CATEGORIES[1],
        desc="Igual que Sherlock pero con otra cobertura de sitios: busca la "
             "presencia de un usuario en miles de fuentes y arma un perfil.",
        limits="Al igual que Sherlock, puede tardar y dar falsos positivos. "
               "Complementa a Sherlock, no lo reemplaza.",
        example="juanperez",
        input_label="Nombre de usuario",
        runner="maigret {input}",
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
        limits="Solo indica registros visibles desde fuentes públicas. "
               "Algunos sitios bloquean este tipo de consultas.",
        example="alguien@gmail.com",
        input_label="Dirección de email",
        runner="holehe {input}",
        takes_input=True,
    ),
    dict(
        name="h8mail",
        title="h8mail",
        binary="h8mail",
        category=CATEGORIES[2],
        desc="Cruza una dirección de email con bases de brechas y fuentes "
             "públicas (GitHub, pastebins) buscando filtraciones.",
        limits="Sin API keys (config del proyecto) los resultados son "
               "limitados. No toda filtración está indexada.",
        example="alguien@gmail.com",
        input_label="Dirección de email",
        runner="h8mail -t {input}",
        takes_input=True,
    ),
    # ── Dominios y subdominios ───────────────────────────
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
    dict(
        name="httpx",
        title="Httpx",
        binary="httpx",
        category=CATEGORIES[3],
        desc="Prueba cuáles dominios o subdominios responden realmente y "
             "reporta código de estado, título, tecnologías y redirección.",
        limits="Solo ve lo que un navegador puede ver. Requiere la URL "
               "completa (con http:// o https://).",
        example="https://ejemplo.com",
        input_label="URL completa (con http/https)",
        runner="httpx -u {input} -sc -title -tech-detect -location",
        takes_input=True,
    ),
    dict(
        name="dnsrecon",
        title="DNSRecon",
        binary="dnsrecon",
        category=CATEGORIES[3],
        desc="Identifica los registros DNS de un dominio: MX, TXT, NS, SOA y "
             "prueba transferencias de zona.",
        limits="Una transferencia de zona casi nunca está abierta en sitios "
               "bien configurados.",
        example="ejemplo.com",
        input_label="Dominio (sin http://)",
        runner="dnsrecon -d {input} -t std",
        takes_input=True,
    ),
    # ── Sitios y tecnología ──────────────────────────────
    dict(
        name="whatweb",
        title="WhatWeb",
        binary="whatweb",
        category=CATEGORIES[4],
        desc="Detecta la tecnología de un sitio: CMS, servidor web, framework, "
             "lenguaje y plugins que usa.",
        limits="La detección puede fallar en sitios con WAF o contenido "
               "dinámico pesado.",
        example="https://ejemplo.com",
        input_label="URL completa (con http/https)",
        runner="whatweb -a 3 {input}",
        takes_input=True,
    ),
    # ── Metadatos (fotos y archivos) ─────────────────────
    dict(
        name="exiftool",
        title="ExifTool",
        binary="exiftool",
        category=CATEGORIES[5],
        desc="Lee los metadatos EXIF de una foto: cámara, fecha, software y, "
             "si están presentes, coordenadas GPS del lugar donde se tomó.",
        limits="Muchas apps y redes borran los metadatos al compartir. "
               "Solo funciona si la foto original los conserva.",
        example="/ruta/a/foto.jpg",
        input_label="Ruta del archivo de imagen",
        runner="exiftool {input}",
        takes_input=True,
    ),
    dict(
        name="metagoofil",
        title="Metagoofil",
        binary="metagoofil",
        category=CATEGORIES[5],
        desc="Descarga documentos públicos (PDF, DOC, XLS...) de un dominio y "
             "les extrae los metadatos ocultos (autores, software, rutas).",
        limits="Descarga un límite de archivos y depende de los motores de "
               "búsqueda. Los archivos quedan en el reporte.",
        example="ejemplo.com",
        input_label="Dominio (sin http://)",
        runner="metagoofil -d {input} -t pdf,doc,xls,docx,pptx -l 5 -n 10 -o {out}",
        takes_input=True,
    ),
    # ── Frameworks OSINT ─────────────────────────────────
    dict(
        name="spiderfoot",
        title="SpiderFoot",
        binary="spiderfoot",
        category=CATEGORIES[6],
        desc="Motor OSINT automatizado: corre cientos de módulos sobre un "
             "objetivo (dominio, email o IP), cruza los datos entre sí y "
             "reporta todo correlacionado en CSV.",
        limits="Análisis pasivo recomendado: puede tardar varios minutos. "
               "Las correlaciones completas se ven mejor en la UI web.",
        example="ejemplo.com",
        input_label="Objetivo (dominio, email o IP)",
        runner="spiderfoot -s {input} -u passive -o csv",
        takes_input=True,
    ),
    dict(
        name="sn0int",
        title="Sn0int",
        binary="sn0int",
        category=CATEGORIES[6],
        desc="Framework OSINT semi-automatizado con interfaz propia (TUI): "
             "módulos para IPs, dominios, personas y fotos, con identidades "
             "y anonimato por VPN.",
        limits="Abre su propia interfaz interactiva: no se puede encadenar. "
               "El primer uso pide instalar/actualizar módulos del registro.",
        example="",
        input_label="",
        runner="sn0int",
        takes_input=False,
        interactive=True,
    ),
    dict(
        name="ghunt",
        title="GHunt",
        binary="ghunt",
        category=CATEGORIES[6],
        desc="OSINT de cuentas de Google a partir de un email: nombre, avatar, "
             "edad estimada, actividad y perfil público.",
        limits="Las funciones de geolocalización requieren un token de "
               "Firebase (ghunt login la primera vez). Google puede limitar "
               "consultas.",
        example="alguien@gmail.com",
        input_label="Email de la cuenta Google",
        runner="ghunt email {input}",
        takes_input=True,
    ),
    # ── Panel web ────────────────────────────────────────
    dict(
        name="webui",
        title="PhoneInfoga Web",
        binary="phoneinfoga",
        category=CATEGORIES[7],
        desc="Levanta un panel web local (navegador) para usar PhoneInfoga "
             "con interfaz gráfica. Se detiene con Ctrl+C.",
        limits="No genera resultados nuevos: es la misma herramienta en web.",
        example="",
        input_label="",
        runner="phoneinfoga serve",
        takes_input=False,
        interactive=True,
    ),
    dict(
        name="sfweb",
        title="SpiderFoot Web",
        binary="spiderfoot",
        category=CATEGORIES[7],
        desc="Levanta la interfaz web de SpiderFoot (http://127.0.0.1:5001) "
             "para lanzar scans y ver el mapa de correlaciones en el navegador.",
        limits="Primer uso: la UI pide crear una contraseña y descargar "
               "plugins de geolocalización opcionales.",
        example="",
        input_label="",
        runner="spiderfoot -l 127.0.0.1:5001",
        takes_input=False,
        interactive=True,
    ),
]