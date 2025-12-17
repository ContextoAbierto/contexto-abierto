import feedparser
from datetime import datetime
import os

# Fuentes RSS: España e Internacional
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

def create_article(section, title, summary, link, content_list=None):
    """
    Crea un archivo HTML con la noticia.
    - section: 'espana' o 'internacional'
    - title: título de la noticia
    - summary: resumen de la noticia
    - link: link a la fuente original
    - content_list: lista opcional de textos adicionales para alargar la noticia
    """
    fecha = datetime.now().strftime("%Y-%m-%d")
    ruta = f"public/noticias/{section}"
    os.makedirs(ruta, exist_ok=True)
    archivo = f"{ruta}/{fecha}-{title[:40].replace(' ', '_').replace('/', '_')}.html"

    # Generar texto completo
    summary_text = summary or ""
    if content_list:
        for c in content_list:
            summary_text += " " + c

    if len(summary_text) < 400:
        summary_text += " [...]"  # indicar que es resumen corto

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

def main():
    for section, urls in FEEDS.items():
        for url in urls:
            feed = feedparser.parse(url)
            for entry in feed.entries[:2]:  # tomar las 2 noticias más recientes
                # Obtener contenido adicional si existe
                content_list = []
                if hasattr(entry, "content"):
                    for c in entry.content:
                        content_list.append(c.value)
                create_article(section, entry.title, entry.get("summary", ""), entry.link, content_list)

if __name__ == "__main__":
    main()
