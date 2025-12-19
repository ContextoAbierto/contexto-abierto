import feedparser
import requests
import os
import random
import re
from datetime import datetime

HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}"
}

# Usamos pocas fuentes para no gastar token
HUMOR_FEEDS = [
    "https://www.europapress.es/rss/rss.aspx",
    "https://feeds.reuters.com/reuters/worldNews"
]

PROMPT_HUMOR = """
A partir de la siguiente noticia real, escribe una noticia de HUMOR y SÁTIRA en español.

Normas IMPORTANTES:
- No insultes a personas concretas
- No incites al odio
- Usa ironía, exageración y humor inteligente
- Mantén relación clara con el hecho real
- No menciones el medio original
- No digas que es una parodia explícitamente
- Longitud: 350-500 palabras
- Estilo de periódico satírico serio

Noticia base:
\"\"\"{texto}\"\"\"
"""

def limpiar(texto):
    texto = re.sub(r'<[^>]+>', '', texto)
    return texto.replace('\n', ' ').strip()

def generar_humor(texto):
    prompt = PROMPT_HUMOR.replace("{texto}", texto)

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 600,
            "temperature": 0.8
        }
    }

    try:
        r = requests.post(HF_API_URL, headers=HEADERS, json=payload, timeout=90)
        if r.status_code == 200:
            return r.json()[0]["generated_text"]
    except:
        pass

    return texto

def main():
    feed = feedparser.parse(random.choice(HUMOR_FEEDS))
    entry = random.choice(feed.entries)

    titulo = entry.title
    resumen = limpiar(entry.get("summary", ""))

    texto_humor = generar_humor(resumen)

    fecha = datetime.now().strftime("%d-%m-%Y")
    ruta = "public/noticias/humor"
    os.makedirs(ruta, exist_ok=True)

    filename = f"{fecha}-humor.html"

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>{titulo}</title>
</head>
<body>

<h1>{titulo}</h1>

{''.join(f'<p>{p}</p>' for p in texto_humor.split('\\n') if p.strip())}

<hr>
<p><em>Artículo de humor generado automáticamente · {fecha}</em></p>

</body>
</html>
"""

    with open(f"{ruta}/{filename}", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    main()
