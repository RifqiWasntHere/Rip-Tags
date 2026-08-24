const REPO = "RifqiWasntHere/Rip-Tags";
const API_LATEST = `https://api.github.com/repos/${REPO}/releases/latest`;
const API_REPO = `https://api.github.com/repos/${REPO}`;

function detectOS(){
  const p = navigator.platform.toLowerCase();
  const ua = navigator.userAgent.toLowerCase();
  if (p.includes("mac") || ua.includes("mac")) return "mac";
  if (p.includes("win") || ua.includes("win")) return "win";
  return "other";
}

function bindNav(){
  const btn = document.querySelector(".nav-toggle");
  const menu = document.getElementById("nav-mobile");
  if (!btn || !menu) return;
  btn.addEventListener("click", () => {
    const open = menu.classList.toggle("open");
    btn.setAttribute("aria-expanded", String(open));
    btn.textContent = open ? "✕" : "☰";
  });
  menu.querySelectorAll("a").forEach(a => a.addEventListener("click", () => {
    menu.classList.remove("open");
    btn.setAttribute("aria-expanded", "false");
    btn.textContent = "☰";
  }));
}

function bindCopy(){
  document.querySelectorAll(".copy-btn").forEach(btn => {
    btn.addEventListener("click", async () => {
      const text = btn.getAttribute("data-copy") || "";
      try {
        await navigator.clipboard.writeText(text);
        const orig = btn.textContent;
        btn.textContent = "Copied!";
        setTimeout(() => btn.textContent = orig, 1200);
      } catch {
        btn.textContent = "Copy failed";
      }
    });
  });
}

async function fetchJSON(url){
  try {
    const r = await fetch(url, { headers: { "Accept": "application/vnd.github+json" } });
    if (!r.ok) throw new Error(String(r.status));
    return await r.json();
  } catch {
    return null;
  }
}

async function hydrateReleases(){
  const macVersionEl = document.getElementById("dl-mac-version");
  const heroVersionEl = document.getElementById("hero-version");
  const releasesExtra = document.getElementById("releases-extra");
  const macBtn = document.getElementById("dl-mac-btn");
  const heroMac = document.getElementById("hero-mac");

  const rel = await fetchJSON(API_LATEST);
  if (!rel || !rel.tag_name) return;

  const tag = rel.tag_name;
  const published = rel.published_at ? new Date(rel.published_at).toLocaleDateString(undefined, { year:"numeric", month:"short", day:"numeric"}) : "";
  const assets = Array.isArray(rel.assets) ? rel.assets : [];
  const macAsset = assets.find(a => /mac|darwin|\.app|Rip.*\.zip/i.test(a.name)) || assets[0];

  if (macVersionEl) macVersionEl.textContent = `Latest: ${tag}${published ? " · " + published : ""}`;
  if (heroVersionEl) heroVersionEl.textContent = tag;

  if (macAsset && macAsset.browser_download_url) {
    if (macBtn) macBtn.href = macAsset.browser_download_url;
    if (heroMac) heroMac.href = macAsset.browser_download_url;
    if (releasesExtra && macAsset.size) {
      const mb = (macAsset.size / (1024*1024)).toFixed(1);
      releasesExtra.textContent = `— ${macAsset.name} · ${mb} MB`;
    }
  } else {
    if (releasesExtra && published) releasesExtra.textContent = `— ${tag} · ${published}`;
  }
}

async function hydrateStars(){
  const el = document.getElementById("star-count");
  const navEl = document.getElementById("nav-stars");
  const textEl = document.getElementById("star-text");
  const repo = await fetchJSON(API_REPO);
  if (!repo || typeof repo.stargazers_count !== "number") return;
  const n = repo.stargazers_count;
  const label = n >= 1000 ? (n/1000).toFixed(1).replace(/\.0$/,"") + "k" : String(n);
  if (el) el.textContent = label;
  if (navEl) navEl.textContent = label;
  if (textEl) textEl.textContent = "Star";
}

function highlightOS(){
  const os = detectOS();
  const macCard = document.getElementById("dl-mac");
  const winCard = document.getElementById("dl-win");
  const macBadge = macCard ? macCard.querySelector(".dl-badge") : null;
  if (os === "win" && winCard) {
    winCard.style.outline = "2px dashed #3776AB";
    winCard.style.outlineOffset = "2px";
    if (macBadge) macBadge.textContent = "Also available";
  }
  if (os === "mac" && macCard) {
    macCard.style.outline = "2px solid #FFD43B";
    macCard.style.outlineOffset = "2px";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  bindNav();
  bindCopy();
  highlightOS();
  hydrateReleases();
  hydrateStars();
});
