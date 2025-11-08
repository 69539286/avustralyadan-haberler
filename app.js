// Kategoriler
const SECTIONS = [
  "ekonomi", "hukumet", "emlak", "goc",
  "spor", "gelismeler", "sosyalist", "istihdam"
];

const JSON_URL = "data/news.json?ts=" + Date.now();

// Küçük yardımcılar
function $(s, r=document){ return r.querySelector(s); }
function $all(s, r=document){ return [...r.querySelectorAll(s)]; }

function fmtDate(t){
  if(!t) return "";
  try {
    return new Date(t).toLocaleString("tr-TR", {
      dateStyle:"medium",
      timeStyle:"short"
    });
  } catch { return t; }
}

// Haber HTML kartı
function itemView(n){
  return `
    <div class="item">
      <img loading="lazy" src="${n.image}" alt="">
      <div>
        <h3><a href="${n.link}" target="_blank">${n.title}</a></h3>
        <p>${n.summary || ""}</p>
        <div class="meta pill">${fmtDate(n.published)}</div>
      </div>
    </div>
  `;
}

// Bölümleri doldur
function renderSection(section, arr){
  const root = document.querySelector(`[data-section="${section}"]`);
  root.innerHTML = "";

  if(!arr || arr.length === 0){
    root.innerHTML = `<p class="meta">Bu kategoride haber yok.</p>`;
    return;
  }

  arr.forEach(n => {
    root.insertAdjacentHTML("beforeend", itemView(n));
  });
}

// Manşet (üst sağ sütun)
function renderHeadlines(data){
  const mans = $("#mansetler");
  mans.innerHTML = "";

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

  all.forEach(n => {
    mans.insertAdjacentHTML("beforeend", `
      <div class="thumb">
        <img src="${n.image}">
        <div><a href="${n.link}" target="_blank">${n.title}</a></div>
      </div>
    `);
  });
}

// JSON yükleme
async function load(){
  try {
    const res = await fetch(JSON_URL);
    const data = await res.json();

    // Güncelleme zamanı
    $("#last-updated").textContent = "Son güncelleme: " + (data.generated_at || "");

    // Kategorileri doldur
    SECTIONS.forEach(sec => {
      renderSection(sec, data[sec]);
    });

    renderHeadlines(data);

  }catch(e){
    console.error(e);
    $("#last-updated").textContent = "Veri yüklenemedi.";
  }
}

// Sekmeler
function setupTabs(){
  const tabs = $("#tabs");
  tabs.addEventListener("click", e=>{
    const btn = e.target.closest(".tab");
    if(!btn) return;

    $all(".tab").forEach(t=>t.classList.remove("active"));
    btn.classList.add("active");

    const target = btn.dataset.target;
    $all(".section").forEach(s=>s.classList.remove("is-active"));
    $("#"+target).classList.add("is-active");
  });
}

// Yenile
function setupRefresh(){
  $("#refresh").addEventListener("click", ()=> load());
}

// Sayfa hazır olunca
document.addEventListener("DOMContentLoaded", ()=>{
  setupTabs();
  setupRefresh();
  load();
});
