async function cargarNoticias() {
  const response = await fetch('data/news_index.json');
  const data = await response.json();

  const grid = document.querySelector('.news-grid');
  grid.innerHTML = '';

  // ESPAÑA + INTERNACIONAL
  ['espana', 'internacional'].forEach(seccion => {
    Object.keys(data[seccion]).forEach(categoria => {
      data[seccion][categoria].forEach(ruta => {
        crearCard(ruta, seccion);
      });
    });
  });

  // HUMOR
  data.humor.forEach(ruta => {
    crearCard(ruta, 'humor');
  });
}

async function crearCard(ruta, tipo) {
  const res = await fetch(ruta);
  const html = await res.text();

  const parser = new DOMParser();
  const doc = parser.parseFromString(html, 'text/html');

  const titulo = doc.querySelector('h1')?.innerText || 'Sin título';
  const parrafo = doc.querySelector('p')?.innerText || '';
  const fecha = doc.querySelector('em')?.innerText || '';

  const card = document.createElement('article');
  card.className = `card ${tipo}`;

  card.innerHTML = `
    <img src="img/placeholder.jpg" alt="${titulo}">
    <div class="card-content">
      <span class="date">${fecha.replace('Artículo generado automáticamente el ', '')}</span>
      <h2>${titulo}</h2>
      <p>${parrafo}</p>
      <a href="${ruta}" class="read-more">Leer más</a>
    </div>
  `;

  document.querySelector('.news-grid').appendChild(card);
}

document.addEventListener('DOMContentLoaded', cargarNoticias);
