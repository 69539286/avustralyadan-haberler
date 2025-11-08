// Hangi kategoriler var
const SECTIONS = [
  "ekonomi","hukumet","emlak","goc",
  "spor","gelismeler","sosyalist","istihdam"
];

const JSON_URL = "data/news.json?ts=" + Date.now();

// Kısa selector fonksiyonları
function $(s, r=document){ return r.querySelector(s); }
function el(html){ const t=document.createElement("template"); t.innerHTML=html.trim(); return t.content.firstChild; }

// Haber kartı HTML
function itemView(n){
  return el(`
    <div class="item">
      <img loading="lazy" src="${n.image}" alt="">
      <div>
        <h3><a href="${n.link}" target="_blank">${n.title}</a></h3>
        <p>${n.summary || ""}</p>
        <div class="meta pill">${n.published || ""}</div>
      </div>
    </div>
  `);
}

// Bölümü doldur
function renderSection(section, arr){
  const root = document.querySelector(`[data-section="${section}"]`);
  root.innerHTML = "";

  if(!arr || arr.length === 0){
    root.innerHTML = `<p class="meta">Bu kategoride haber bulunamadı.</p>`;
    return;
  }

  arr.forEach(n => root.appendChild(itemView(n)));
}

// Manşetleri doldur
function renderHeadlines(data){
  const mans = $("#mansetler");
  mans.innerHTML = "";

  const merged = [
    ...data.ekonomi,
    ...data.hukumet,
    ...data.emlak,
    ...data.goc,
    ...data.spor,
    ...data.gelismeler,
    ...data.sosyali
