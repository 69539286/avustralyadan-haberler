// Hangi kategoriler var
const SECTIONS = [
  "ekonomi","hukumet","emlak","goc",
  "spor","gelismeler","sosyalist","istihdam"
];

const state = {
  url: "data/news.json",
  data: null,
  timer: null,
  refreshMs: 60 * 60 * 1000 // SAATLİK otomatik kontrol
};

function $(sel, root=document){ return root.querySelector(sel); }
function $all(sel, root=document){ return [...root.querySelectorAll(sel)]; }

function fmtDate(iso){
  try{
    const d = new Date(iso);
    return d.toLocaleString("tr-TR", { dateStyle:"medium", timeStyle:"short" });
  }catch{ return iso || ""; }
}

function cardHTML(item){
  const img = item.image ? `<img loading="lazy" src="${item.image}" alt="">` : "";
  const src = item.source_host ? `<span class="pill">${item.source_host}</span>` : "";
  const sum = item.summary || "Özet bulunamadı.";
  return `
    <article class="item">
      ${img}
      <div>
        <h3>${item.title}</h3>
        <p>${sum}</p>
        <div class="meta">
          ${src}
          <span class="pill">${fmtDate(item.published)}</span>
          ${item.link ? `<a class="pill" href="${item.link}" target="_blank" rel="noopener">Habere git →</a>` : ""}
        </div>
      </div>
    </article>
  `;
}

function render(){
  if(!state.data) return;
  $("#year").textContent = new Date().getFullYear();
  $("#updatedAt").textContent = `Güncellendi: ${fmtDate(state.data.updated_at)} (otomatik)`;

  // Manşetler (tüm kategorilerden ilk 6)
  const mans = $("#mansetler");
  if(mans){
    const all = SECTIONS.flatMap(k => state.data[k] || []);
    mans.innerHTML = "";
    all.slice(0, 6).forEach(n=>{
      const div = document.createElement("div");
      div.className = "thumb";
      div.innerHTML = `
        ${n.image ? `<img loading="lazy" src="${n.image}" alt="">` : ""}
        <div>
          <div><strong>${n.title}</strong></div>
          <div style="font-size:.9em;color:#666">${fmtDate(n.published)} · ${n.source_host||""}</div>
        </div>
      `;
      mans.appendChild(div);
    });
  }

  // Kategoriler
  SECTIONS.forEach(key=>{
    const mount = document.querySelector(`.grid[data-section="${key}"]`);
    const items = state.data[key] || [];
    mount.innerHTML = items.length
      ? items.map(cardHTML).join("")
      : `<div class="item"><div><p>Şimdilik içerik yok.</p></div></div>`;
  });
}

async function fetchJSON(force=false){
  const url = state.url + (force ? `?t=${Date.now()}` : "");
  const res = await fetch(url, {cache: force ? "reload" : "default"});
  if(!res.ok) throw new Error("JSON indirilemedi");
  return res.json();
}

async function load(force=false){
  try{
    const data = await fetchJSON(force);
    state.data = data;
    render();
  }catch(e){
    $("#updatedAt").textContent = "Veri yüklenemedi. (news.json yok mu?)";
    console.error(e);
  }
}

function setupTabs(){
  const tabs = $("#tabs");
  tabs.addEventListener("click", (e)=>{
    const btn = e.target.closest(".tab");
    if(!btn) return;
    $all(".tab", tabs).forEach(b=>b.classList.remove("active"));
    btn.classList.add("active");
    const target = btn.dataset.target;
    $all(".section").forEach(s=>s.classList.remove("is-active"));
    const sec = document.getElementById(target);
    if(sec) sec.classList.add("is-active");
  });
}

function setupRefresh(){
  const btn = $("#refreshBtn");
  if(btn) btn.addEventListener("click", ()=> load(true));
  if(state.timer) clearInterval(state.timer);
  state.timer = setInterval(()=> load(true), state.refreshMs);
}

document.addEventListener("DOMContentLoaded", ()=>{
  setupTabs();
  setupRefresh();
  load(true);
});
