import feedparser
from datetime import datetime
import os

FEEDS = {
    "espana": [
        "https://www.europapress.es/rss/rss.aspx",
        "https://www.eldiario.es/rss/"
    ],
    "internacional": [
        "https://feeds.reuters.com/reuters/worldNews",
        "http://feeds.bbci.co.uk/news/world/rss.xml"
    ]
}

def create_article(section, title, summary, link):
    fecha = datetime.now().strftime("%Y-%m-%d")
    ruta = f"public/noticias/{section}"
    os.makedirs(ruta, exist_ok=True)
    archivo = f"{ruta}/{fecha}-{title[:40].replace(' ', '_')}.html"

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
  <p>{summary[:600]}</p>
  <h2>Análisis</h2>
  <p>Desde una perspectiva centrista, esta noticia presenta elementos positivos y desafíos que requieren equilibrio institucional.</p>
  <p><a href="{link}">Fuente original</a></p>
  <p><em>Publicado automáticamente el {fecha}</em></p>
</body>
</html>
"""
    with open(archivo, "w", encoding="utf-8") as f:
        f.write(contenido)

def main():
    for section, urls in FEEDS.items():
        for url in urls:
            feed = feedparser.parse(url)
            for entry in feed.entries[:2]:  # las 2 noticias más recientes
                create_article(section, entry.title, entry.get("summary", ""), entry.link)

if __name__ == "__main__":
    main()
