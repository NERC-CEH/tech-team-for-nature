// The deployment map: one marker per country, never where the systems really are. Click a marker to
// see that country's systems, each with a few of its photos. Data: deployments.json (made by
// tools/build_map.py from the deployment list; it holds no coordinates or site names).
(function () {
  const esc = s => String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const num = n => n.toLocaleString("en-GB");
  const NUDGE = { "Costa Rica": [-22, -14], "Panama": [22, 14], "Singapore": [10, 18], "Thailand": [-8, -14] };
  const KIND = { moths: "Moth camera", sound: "Sound recorder", bats: "Bat detector" };
  const panel = document.getElementById("map-panel");
  const map = L.map("deployment-map", { scrollWheelZoom: false, worldCopyJump: true, minZoom: 1, maxZoom: 6 })
    .fitBounds([[-35, -110], [62, 145]]);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 6, attribution: "&copy; OpenStreetMap contributors"
  }).addTo(map);

  function carousel(photos) {
    if (!photos.length) return `<div class="carousel empty">No photos yet</div>`;
    const slides = photos.map((p, i) => `<img src="${esc(p)}" alt="A night photo from this system" loading="lazy">`).join("");
    const nav = photos.length > 1 ? `<button class="cprev" aria-label="Previous photo">&#8249;</button><button class="cnext" aria-label="Next photo">&#8250;</button>` +
      `<div class="cdots">${photos.map((_, i) => `<span${i ? "" : ' class="on"'}></span>`).join("")}</div>` : "";
    return `<div class="carousel"><div class="ctrack">${slides}</div>${nav}</div>`;
  }

  function wire(root) {
    root.querySelectorAll(".carousel").forEach(c => {
      const track = c.querySelector(".ctrack"), dots = c.querySelectorAll(".cdots span");
      if (!track || !dots.length) return;
      const go = d => track.scrollBy({ left: d * track.clientWidth, behavior: "smooth" });
      c.querySelector(".cprev").onclick = () => go(track.scrollLeft < 5 ? dots.length - 1 : -1);
      c.querySelector(".cnext").onclick = () => go(track.scrollLeft + track.clientWidth >= track.scrollWidth - 5 ? -(dots.length - 1) : 1);
      track.addEventListener("scroll", () => {
        const i = Math.round(track.scrollLeft / track.clientWidth);
        dots.forEach((d, j) => d.classList.toggle("on", i === j));
      }, { passive: true });
    });
  }

  function show(c) {
    const kinds = Object.entries(c.kinds).filter(([, n]) => n).map(([k, n]) => `${n} ${KIND[k].toLowerCase()}${n === 1 ? "" : "s"}`);
    panel.innerHTML =
      `<div class="panel-head"><h3>${esc(c.country)}</h3><button class="panel-close" aria-label="Close">&times;</button></div>` +
      `<p><strong>${c.systems}</strong> system${c.systems === 1 ? "" : "s"}` + (c.images ? ` · <strong>${num(c.images)}</strong> photos` : "") + `</p>` +
      (kinds.length ? `<p class="small">${esc(kinds.join(", "))}</p>` : "") +
      `<div class="systems">` + c.deployments.map(d =>
        `<div class="system">${carousel(d.photos)}<div class="system-text"><strong>${esc(d.label)}</strong>` +
        `<span class="kinds">${d.records.map(k => `<span>${KIND[k]}</span>`).join("")}</span>` +
        `<span class="small">${esc(d.when || "")}${d.images ? ` · ${num(d.images)} photos` : ""}</span></div></div>`).join("") +
      `</div>`;
    panel.hidden = false;
    map.invalidateSize();
    panel.querySelector(".panel-close").onclick = () => { panel.hidden = true; map.invalidateSize(); };
    wire(panel);
    panel.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  fetch("deployments.json").then(r => r.json()).then(data => {
    let systems = 0, imgs = 0;
    data.countries.forEach(c => {
      systems += c.systems; imgs += c.images;
      const [dx, dy] = NUDGE[c.country] || [0, 0];       // neighbours that would overlap on the world view
      const icon = L.divIcon({ className: "", html: `<div class="country-marker">${c.systems}</div>`, iconSize: [40, 40], iconAnchor: [20 - dx, 20 - dy] });
      L.marker([c.lat, c.lon], { icon, title: `${c.country}: ${c.systems} systems`, keyboard: true })
        .addTo(map).on("click", () => show(c));
    });
    document.getElementById("map-stats").innerHTML =
      `<div><strong>${data.countries.length}</strong>countries</div><div><strong>${systems}</strong>systems</div>` +
      `<div><strong>${(imgs / 1e6).toFixed(1)} million</strong>photos</div>`;
    document.getElementById("map-asof").textContent = data.as_of;
    const slug = s => s.toLowerCase().replace(/[^a-z]+/g, "-");
    const want = decodeURIComponent(location.hash.slice(1));
    const pick = data.countries.find(c => slug(c.country) === want);
    if (pick) show(pick);
  }).catch(() => {
    document.getElementById("deployment-map").innerHTML = "<p>The map couldn't load. Please try again later.</p>";
  });
})();
