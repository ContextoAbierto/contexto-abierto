import feedparser
from datetime import datetime
import os

# ----------------------------
# Fuentes RSS organizadas por sección
# ----------------------------
FEEDS = {
    "espana": {
        "politica": [
            "https://www.europapress.es/rss/rss.aspx"
        ],
        "economia": [
            "https://www.eldiario.es/rss/"
        ],
        "deportes": [
            "https://www.marca.com/rss/futbol/primera-division.xml"
        ]
    },
    "internacional": {
        "politica": [
            "https://feeds.reuters.com/reuters/worldNews"
        ],
        "economia": [
            "http://feeds.bbci.co.uk/news/world/rss.xml"
        ],
        "deportes": [
            "https://www.espn.com/espn/rss/news"
        ]
    }
}

# ----------------------------
# Función para crear un artículo HTML
# ----------------------------
def create_article(section, category, title, summary, link, content_list=None):
    fecha = datetime.now().strftime("%Y-%m-%d")
    ruta = f"public/noticias/{section}/{category}"
    os.makedirs(ruta, exist_ok=True)
    archivo = f"{ruta}/{fecha}-{title[:40].replace(' ', '_').replace('/', '_')}.html"

    # Generar texto completo
    summary_text = summary or ""
    if content_list:
        for c in content_list:
            summary_text += " " + c

    if len(summary_text) < 400:
        summary_text += " [...]"

    contenido = f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
</head>
<body>
  <h1>{title}</h1>

  <h2>Noticia</h2>
  <p>{summary_text}</p>

  <h2>Información adicional</h2>
  <p>El lector puede interpretar los hechos directamente a partir de la noticia. Se omiten juicios o opiniones de la plataforma.</p>

  <p><a href="{link}">Fuente original</a></p>
  <p><em>Publicado automáticamente el {fecha}</em></p>
</body>
</html>
"""
    with open(archivo, "w", encoding="utf-8") as f:
        f.write(contenido)

# ----------------------------
# Función principal
# ----------------------------
def main():
    for section, categories in FEEDS.items():
        for category, urls in categories.items():
            for url in urls:
                feed = feedparser.parse(url)
                for entry in feed.entries[:2]:  # tomamos las 2 noticias más recientes
                    content_list = []
                    if hasattr(entry, "content"):
                        for c in entry.content:
                            content_list.append(c.value)
                    create_article(section, category, entry.title, entry.get("summary", ""), entry.link, content_list)

if __name__ == "__main__":
    main()
