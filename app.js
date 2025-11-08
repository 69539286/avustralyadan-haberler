// SİTEDEKİ KATEGORİLER
const SECTIONS = [
  "ekonomi","hukumet","emlak","goc",
  "spor","gelismeler","sosyalist","istihdam"
];

const JSON_URL = "data/news.json?ts=" + Date.now();

// Mini selector fonksiyonları
function $(s, r=document){ return r.querySelector(s); }
function el(html){ const t=document.createElement("template"); t.innerHTML=html.trim(); return t.content.firstChild; }

// Haber kartı
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

// Tek kategoriyi doldur
function renderSection(section, arr){
  const root = document.querySelector(`[data-section="${section}"]`);
  root.innerHTML = "";

  if(!arr || arr.length === 0){
    root.innerHTML = `<p class="meta">Bu kategoride haber yok.</p>`;
    return;
  }

  arr.forEach(n => root.appendChild(itemView(n)));
}

// Manşetler (ilk 6 haber)
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
    ...data.sosyalist,
    ...data.istihdam
  ].slice(0, 6);

  merged.forEach(n=>{
    mans.appendChild(el(`
      <div class="thumb">
        <img loading="lazy" src="${n.image}" alt="">
        <div><a href="${n.link}" target="_blank">${n.title}</a></div>
      </div>
    `));
  });
}

// JSON yükleme
async function load(force=false){
  try{
    const res = await fetch(JSON_URL, {cache: force ? "reload" : "default"});
    const data = await res.json();

    // Kategorileri doldur
    renderSection("ekonomi", data.ekonomi);
    renderSection("hukumet", data.hukumet);
    renderSection("emlak", data.emlak);
    renderSection("goc", data.goc);
    renderSection("spor", data.spor);
    renderSection("gelismeler", data.gelismeler);
    renderSection("sosyalist", data.sosyalist);
    renderSection("istihdam", data.istihdam);

    renderHeadlines(data);

    $("#updatedAt").textContent = "Güncellendi: " + (data.generated_at || "");
  }catch(e){
    console.error("JSON yüklenemedi:", e);
    $("#updatedAt").textContent = "Veri yüklenemedi.";
  }
}

// Sekme sistemi
function setupTabs(){
  const tabs = $("#tabs");
  tabs.addEventListener("click", (e)=>{
    const btn = e.target.closest(".tab");
    if(!btn) return;

    tabs.querySelectorAll(".tab").forEach(b=>b.classList.remove("active"));
    btn.classList.add("active");

    const target = btn.dataset.target;
    document.querySelectorAll(".section").forEach(s=>s.classList.remove("is-active"));
    $("#"+target).classList.add("is-active");
  });
}

// Yenile butonu
function setupRefresh(){
  $("#refreshBtn").addEventListener("click", ()=> load(true));
}

// Sayfa yüklendiğinde başlat
document.addEventListener("DOMContentLoaded", ()=>{
  setupTabs();
  setupRefresh();
  load(true);
});
