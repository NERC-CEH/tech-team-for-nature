// Upcoming and past events from events/events.json. Used on the Events page (#events-upcoming,
// #events-past) and the home page (#home-events: the next three, hidden when nothing is coming up).
// The page says where the site root is with <div data-site-root="../">.
(function () {
  const rootEl = document.querySelector("[data-site-root]");
  const root = rootEl ? rootEl.getAttribute("data-site-root") : "";
  const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const link = u => /^https?:\/\//.test(u || "") ? u : (u && !/^[a-z]+:/i.test(u) ? root + u : "");
  const dateOnly = s => /^\d{4}-\d{2}-\d{2}$/.test(s || "");
  const starts = e => new Date(dateOnly(e.start) ? e.start + "T00:00:00" : e.start);
  const ends = e => { const s = e.end || e.start; return dateOnly(s) ? new Date(s + "T23:59:59") : new Date(s); };
  const day = d => d.toLocaleDateString("en-GB", { weekday: "long", day: "numeric", month: "long", year: "numeric" });
  const clock = d => d.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", timeZone: "Europe/London" });

  function ics(e) {
    const stamp = d => d.toISOString().replace(/[-:]/g, "").replace(/\.\d{3}/, "");
    const text = s => String(s || "").replace(/[\\,;]/g, m => "\\" + m).replace(/\n/g, " ");
    const lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//UKCEH Tech for Nature//Events//EN", "BEGIN:VEVENT",
      "UID:" + stamp(starts(e)) + "-" + e.title.replace(/\W+/g, "") + "@tech-for-nature",
      "DTSTAMP:" + stamp(new Date()),
      dateOnly(e.start) ? "DTSTART;VALUE=DATE:" + e.start.replace(/-/g, "") : "DTSTART:" + stamp(starts(e))];
    if (e.end) lines.push(dateOnly(e.end) ? "DTEND;VALUE=DATE:" + e.end.replace(/-/g, "") : "DTEND:" + stamp(new Date(e.end)));
    lines.push("SUMMARY:" + text(e.title), "LOCATION:" + text(e.where),
      "DESCRIPTION:" + text((e.summary || "") + (e.link ? " " + e.link : "")), "END:VEVENT", "END:VCALENDAR");
    return "data:text/calendar;charset=utf-8," + encodeURIComponent(lines.join("\r\n"));
  }

  function card(e, upcoming) {
    const d = starts(e);
    const time = dateOnly(e.start) ? "" : " · " + clock(d) + (e.end && !dateOnly(e.end) ? "–" + clock(new Date(e.end)) : "") + " UK time";
    const more = link(e.story), book = link(e.link);
    const buttons = [
      upcoming && book ? `<a class="btn btn-warning btn-sm" href="${esc(book)}" target="_blank" rel="noopener">Book or join</a>` : "",
      upcoming ? `<a class="btn btn-outline-dark btn-sm" href="${ics(e)}" download="${esc(e.title.replace(/[^\w]+/g, "-"))}.ics">Add to calendar</a>` : "",
      more ? `<a class="btn btn-link btn-sm" href="${esc(more)}">${upcoming ? "More" : "Read about it"}</a>` : ""].join("");
    return `<article class="event${upcoming ? " soon" : ""}">
      <div class="cal" aria-hidden="true"><span class="m">${d.toLocaleDateString("en-GB", { month: "short" })}</span><span class="d">${d.getDate()}</span><span class="y">${d.getFullYear()}</span></div>
      <div class="ev-body"><span class="tag">${esc(e.kind || "Event")}</span>
        <h3>${more ? `<a href="${esc(more)}">${esc(e.title)}</a>` : esc(e.title)}</h3>
        <p class="ev-when">${esc(day(d) + time)}${e.where ? " · " + esc(e.where) : ""}</p>
        ${e.host ? `<p class="ev-host">${esc(e.host)}</p>` : ""}
        ${e.summary ? `<p>${esc(e.summary)}</p>` : ""}
        ${buttons.trim() ? `<p class="ev-links">${buttons}</p>` : ""}
      </div></article>`;
  }

  fetch(root + "events/events.json").then(r => r.json()).then(data => {
    const now = new Date(), all = data.events || [];
    const up = all.filter(e => ends(e) >= now).sort((a, b) => starts(a) - starts(b));
    const past = all.filter(e => ends(e) < now).sort((a, b) => starts(b) - starts(a));
    const fill = (id, list, upcoming, empty) => {
      const el = document.getElementById(id);
      if (el) el.innerHTML = list.length ? list.map(e => card(e, upcoming)).join("") : empty;
    };
    fill("events-upcoming", up, true, `<p>Nothing in the calendar just now. Check back soon, or read our <a href="${root}stories/index.html">latest stories</a>.</p>`);
    fill("events-past", past, false, "");
    const home = document.getElementById("home-events");
    if (home && up.length) {
      home.querySelector(".event-list").innerHTML = up.slice(0, 3).map(e => card(e, true)).join("");
      home.hidden = false;
    }
  }).catch(() => {});
})();
