import feedparser
from datetime import datetime
import os
import json

# Fuentes RSS por sección
FEEDS = {
    "espana": {
        "politica": ["https://www.europapress.es/rss/rss.aspx"],
        "economia": ["https://www.eldiario.es/rss/"],
        "deportes": ["https://www.marca.com/rss/futbol/primera-division.xml"]
    },
    "internacional": {
        "politica": ["https://feeds.reuters.com/reuters/worldNews"],
        "economia": ["http://feeds.bbci.co.uk/news/world/rss.xml"],
        "deportes": ["https://www.espn.com/espn/rss/news"]
    }
}

# Diccionario para almacenar enlaces de cada sección
news_index = {}

def create_article(section, category, title, summary, link, content_list=None):
    fecha = datetime.now().strftime("%Y-%m-%d")
    ruta = f"public/noticias/{section}/{category}"
    os.makedirs(ruta, exist_ok=True)
    filename = f"{fecha}-{title[:40].replace(' ', '_').replace('/', '_')}.html"
    archivo = f"{ruta}/{filename}"

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

    # Guardar en el índice de noticias
    if section not in news_index:
        news_index[section] = {}
    if category not in news_index[section]:
        news_index[section][category] = []
    news_index[section][category].append(f"noticias/{section}/{category}/{filename}")

def main():
    for section, categories in FEEDS.items():
        for category, urls in categories.items():
            for url in urls:
                feed = feedparser.parse(url)
                for entry in feed.entries[:2]:  # últimas 2 noticias
                    content_list = []
                    if hasattr(entry, "content"):
                        for c in entry.content:
                            content_list.append(c.value)
                    create_article(section, category, entry.title, entry.get("summary", ""), entry.link, content_list)

    # Guardar el JSON con los enlaces
    os.makedirs("public/data", exist_ok=True)
    with open("public/data/news_index.json", "w", encoding="utf-8") as f:
        json.dump(news_index, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
