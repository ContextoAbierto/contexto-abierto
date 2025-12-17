from datetime import datetime
import os

fecha = datetime.now().strftime("%Y-%m-%d")
ruta = "public/noticias/espana"
os.makedirs(ruta, exist_ok=True)

archivo = f"{ruta}/{fecha}-noticia-prueba.html"

contenido = f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Noticia de prueba</title>
</head>
<body>
  <h1>Noticia de prueba</h1>

  <h2>Noticia</h2>
  <p>Este es un ejemplo de noticia generada automáticamente por Contexto Abierto.</p>

  <h2>Análisis</h2>
  <p>Desde una perspectiva centrista, este contenido sirve para comprobar que el sistema funciona correctamente.</p>

  <p><em>Publicado automáticamente el {fecha}</em></p>
</body>
</html>
"""

with open(archivo, "w", encoding="utf-8") as f:
    f.write(contenido)

print("Noticia de prueba creada")
