const SECTIONS = [
  "ekonomi","hukumet","emlak","goc",
  "spor","gelismeler","sosyalist","istihdam"
];

const state = {
  url: "data/news.json",
  data: null,
  timer: null,
  refreshMs: 5 * 60 * 1000 // 5 dk’da bir otomatik kontrol
};

function $(sel, root=document){ return root.querySelector(sel); }
function $all(sel, root=document){ return [...root.querySelectorAll(sel)]; }

function fmtDate(iso){
  try {
    const d = new Date(iso);
    return d.toLocaleString("tr-TR", { dateStyle:"medium", timeStyle:"short" });
  } catch { return iso; }
}

function cardHTML(item){
  const badges = (item.tags||[]).map(t=>`<span class="badge">${t}</span>`).join("");
  const host = item.link ? (new URL(item.link)).hostname.replace(/^www\./,"") : (item.source||"Kaynak");
  return `
    <article class="card">
      <div class="src">${host} · ${fmtDate(item.published_at||item.collected_at||"")}</div>
      <h3>${item.title}</h3>
      <div class="badges">${badges}</div>
      <p>${item.summary||""}</p>
      ${item.link ? `<a href="${item.link}" target="_blank" rel="noopener">Habere git →</a>` : ""}
    </article>
  `;
}

function render(){
  if(!state.data) return;
  $("#year").textContent = new Date().getFullYear();
  $("#last-updated").textContent = `Son güncelleme: ${fmtDate(state.data.updated_at)} (otomatik)`;
  SECTIONS.forEach(key=>{
    const mount = document.querySelector(`.grid[data-section="${key}"]`);
    const items = state.data[key] || [];
    mount.innerHTML = items.length
      ? items.map(cardHTML).join("")
      : `<div class="card"><p>Şimdilik içerik yok.</p></div>`;
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
    $("#last-updated").textContent = "Veri yüklenemedi. (news.json yok mu?)";
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
    $(`#${target}`).classList.add("is-active");
  });
}

function setupRefresh(){
  $("#refresh").addEventListener("click", ()=> load(true));
  if(state.timer) clearInterval(state.timer);
  state.timer = setInterval(()=> load(true), state.refreshMs);
}

document.addEventListener("DOMContentLoaded", ()=>{
  setupTabs();
  setupRefresh();
  load(true);
});
