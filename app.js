const JSON_URL = "data/news.json?ts=" + Date.now();

function $(s, r=document){ return r.querySelector(s); }
function $all(s, r=document){ return [...r.querySelectorAll(s)]; }

function itemHTML(n){
  return `
    <div class="item">
      <img loading="lazy" src="${n.image}" alt="">
      <div>
        <h3><a href="${n.link}" target="_blank">${n.title}</a></h3>
        <p>${n.summary}</p>
        <div class="meta pill">${n.published || ""}</div>
      </div>
    </div>`;
}

function loadSection(section, arr){
  const root = document.querySelector('[data-section="'+section+'"]');
  if(!arr || arr.length === 0){
    root.innerHTML = "<p>Bu kategoride haber yok.</p>";
    return;
  }
  root.innerHTML = arr.map(itemHTML).join("");
}

async function loadJSON(){
  try {
    const res = await fetch(JSON_URL);
    const data = await res.json();

    // Başlıklar
    const manset = document.getElementById("mansetler");
    manset.innerHTML = "";
    const merged = [
      ...data.ekonomi,
      ...data.hukumet,
      ...data.emlak,
      ...data.goc,
      ...data.spor,
      ...data.gelismeler,
      ...data.sosyalist,
      ...data.istihdam
    ].slice(0, 8);

    manset.innerHTML = merged
      .map(n => `
        <div class="thumb">
          <img src="${n.image}">
          <div><a href="${n.link}" target="_blank">${n.title}</a></div>
        </div>
      `)
      .join("");

    // Kategoriler
    loadSection("ekonomi", data.ekonomi);
    loadSection("hukumet", data.hukumet);
    loadSection("emlak", data.emlak);
    loadSection("goc", data.goc);
    loadSection("spor", data.spor);
    loadSection("gelismeler", data.gelismeler);
    loadSection("sosyalist", data.sosyalist);
    loadSection("istihdam", data.istihdam);

    document.getElementById("updatedAt").textContent =
      "Güncellendi: " + (data.updated_at || "");

  } catch (err) {
    console.error("HATA:", err);
    document.getElementById("updatedAt").textContent = "Veri yüklenemedi.";
  }
}

function setupTabs(){
  document.getElementById("tabs").addEventListener("click", e=>{
    const btn = e.target.closest(".tab");
    if(!btn) return;

    $all(".tab").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");

    $all(".section").forEach(sec => sec.classList.remove("is-active"));
    document.getElementById(btn.dataset.target).classList.add("is-active");
  });
}

document.addEventListener("DOMContentLoaded", ()=>{
  setupTabs();
  loadJSON();
  document.getElementById("refreshBtn").addEventListener("click", ()=> loadJSON());
});
