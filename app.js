// Kategoriler
const SECTIONS = [
  "ekonomi","hukumet","emlak","goc",
  "spor","gelismeler","sosyalist","istihdam"
];

const JSON_URL = "data/news.json?ts=" + Date.now();

// Selector kısa yolları
function $(s, r=document){ return r.querySelector(s); }
function $all(s, r=document){ return [...r.querySelectorAll(s)]; }

// HTML şablonu
function itemView(n){
  return `
    <div class="item">
      <img src="${n.image}" alt="">
      <div>
        <h3><a href="${n.link}" target="_blank">${n.title}</a></h3>
        <p>${n.summary || ""}</p>
        <div class="pill">${n.published || ""}</div>
      </div>
    </div>
  `;
}

// Haberleri bölüme bas
function renderSection(key, arr){
  const root = document.querySelector(`[data-section="${key}"]`);
  if(!root) return;
  root.innerHTML = "";

  if(!arr || arr.length === 0){
    root.innerHTML = `<p>Bu kategoride haber yok.</p>`;
    return;
  }

  root.innerHTML = arr.map(itemView).join("");
}

// Manşetleri doldur (en çok 6 haber)
function renderHeadlines(data){
  const manset = $("#mansetler");
  manset.innerHTML = "";

  const all = [
    ...data.ekonomi,
    ...data.hukumet,
    ...data.emlak,
    ...data.goc,
    ...data.spor,
    ...data.gelismeler,
    ...data.sosyalist,
    ...data.istihdam
  ].slice(0, 6);

  manset.innerHTML = all.map(n => `
    <div class="thumb">
      <img src="${n.image}">
      <div><a href="${n.link}" target="_blank">${n.title}</a></div>
    </div>
  `).join("");
}

// JSON yükle
async function load(){
  try{
    const res = await fetch(JSON_URL);
    const data = await res.json();

    $("#updatedAt").textContent = "Güncellendi: " + new Date().toLocaleString("tr-TR");
    $("#year").textContent = new Date().getFullYear();

    SECTIONS.forEach(k => renderSection(k, data[k]));
    renderHeadlines(data);

  }catch(err){
    $("#updatedAt").textContent = "Veri yüklenemedi!";
    console.error(err);
  }
}

// Sekmeler
function setupTabs(){
  const tabs = $("#tabs");
  tabs.addEventListener("click", e => {
    const btn = e.target.closest(".tab");
    if(!btn) return;

    $all(".tab").forEach(t => t.classList.remove("active"));
    btn.classList.add("active");

    const target = btn.dataset.target;
    $all(".section").forEach(s => s.classList.remove("is-active"));
    $("#" + target).classList.add("is-active");
  });
}

// Yenile
function setupRefresh(){
  $("#refreshBtn").addEventListener("click", () => load());
}

// Başlat
document.addEventListener("DOMContentLoaded", () => {
  setupTabs();
  setupRefresh();
  load();
});
