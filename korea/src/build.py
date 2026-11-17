"""Builds EasyModeKorea: checker page, topic pages and a changelog page, in each language.
Run from the repo root:  python korea/src/build.py
Content: data.py (answers) and data_extra.py (hook, short labels, icons, phrases, first 24 hours,
changelog, host-stay strings). Host stay details travel in the link's #g= hash: never sent to a
server or to analytics, and rendered with textContent only.
"""
import html, json, os, sys

sys.path.insert(0, os.path.dirname(__file__))
from data import CHECKED, CHECKED_ISO, LANGS, SOURCES, TASK_META  # noqa: E402
from data_extra import BRAND, ICONS, PHRASES, SHORT, X  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
SITE = "https://eddpositive.github.io/korea/"
GOAT = "https://eddpositive.goatcounter.com/count"
CSS = open(os.path.join(os.path.dirname(__file__), "style.css"), encoding="utf-8").read()
e = lambda s: html.escape(str(s), quote=True)
icon = lambda tid: f'<svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[tid]}</svg>'


def head(lang, title, desc, path, alt_paths, extra=""):
    alts = "".join(f'<link rel="alternate" hreflang="{LANGS[k]["html_lang"]}" href="{SITE}{p}">' for k, p in alt_paths.items())
    alts += f'<link rel="alternate" hreflang="x-default" href="{SITE}{alt_paths["en"]}">'
    return f"""<!DOCTYPE html>
<html lang="{LANGS[lang]['html_lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#2336e8">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE}{path}">{alts}
<meta property="og:type" content="website"><meta property="og:site_name" content="{BRAND}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{SITE}{path}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&family=IBM+Plex+Sans:wght@400;600;700&display=swap" rel="stylesheet">
<style>
{CSS}</style>
<script data-goatcounter="{GOAT}" async src="//gc.zgo.at/count.js"></script>{extra}
</head>
<body>"""


def lang_links(cur, rel_paths, prefix):
    out = []
    for k, L in LANGS.items():
        cur_attr = ' aria-current="page"' if k == cur else ""
        out.append(f'<a href="{prefix}{rel_paths[k]}" hreflang="{L["html_lang"]}"{cur_attr}>{e(L["name"])}</a>')
    return f'<nav class="langs" aria-label="{e(LANGS[cur]["ui"]["langs"])}">' + "".join(out) + "</nav>"


def hero(lang, alt, up, h1, lede, home="./", trust=True):
    x = X[lang]
    mode = '<p class="mode" aria-hidden="true"><s>Hard mode</s><span class="arrow">→</span><span class="easy">Easy mode</span></p>'
    tr = f'<p class="trust">{e(x["trust"])}</p>' if trust else ""
    return f"""<header class="hero"><div class="wrap">
  <div class="toprow"><a class="logo" href="{home}">EasyMode<b>Korea</b></a>{lang_links(lang, alt, up)}</div>
  {mode}<h1>{e(h1)}</h1><p>{e(lede)}</p>{tr}
</div></header>"""


def task_list(lang):
    T = LANGS[lang]["tasks"]
    out = []
    for tid, slug, srcs in TASK_META:
        t = dict(T[tid]); t["id"] = tid; t["slug"] = slug; t["short"] = SHORT[lang]["tasks"][tid]
        t["sources"] = [SOURCES[s] for s in srcs]
        t["phrases"] = [[ko, m[lang]] for ko, m in PHRASES.get(tid, [])]
        t["icon"] = icon(tid)
        out.append(t)
    return out


def resolve(t, profile, device):
    if "all" in t: return t["all"]
    v = t["v"][profile]
    if isinstance(v, str): v = t["v"][v]
    if t.get("dev") and device in v: v = v[device]
    return v


SHOW_HTML = lambda lang: f"""<div class="show" id="show" hidden role="dialog" aria-modal="true" aria-labelledby="show-lbl">
  <div class="lbl" id="show-lbl"></div><div class="ko" lang="ko" id="show-ko"></div>
  <div><p class="mean" id="show-mean"></p><button class="btn" type="button" id="show-close">{e(SHORT[lang]['close'])}</button></div>
</div>"""

COMMON_JS = r"""
function el(tag, attrs = {}, kids = []) { const n = document.createElement(tag); for (const [k, v] of Object.entries(attrs)) { if (k === "text") n.textContent = v; else if (k === "html") n.innerHTML = v; else n.setAttribute(k, v); } for (const c of [].concat(kids)) if (c) n.append(c); return n; }
function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }
function count(path, title) { try { if (window.goatcounter && window.goatcounter.count) window.goatcounter.count({ path, title, event: true }); } catch (e) {} }
/* Full-screen card to hand the phone to staff or a driver. */
let lastFocus = null;
function show(label, ko, big, mean) {
  lastFocus = document.activeElement;
  document.getElementById("show-lbl").textContent = label;
  const k = document.getElementById("show-ko"); k.textContent = ko;
  if (big) k.append(el("small", { text: big }));
  document.getElementById("show-mean").textContent = mean || "";
  document.getElementById("show").hidden = false; document.getElementById("show-close").focus();
  count("show-card", label);
}
function hideShow() { document.getElementById("show").hidden = true; if (lastFocus) lastFocus.focus(); }
document.getElementById("show-close").addEventListener("click", hideShow);
document.addEventListener("keydown", ev => { if (ev.key === "Escape" && !document.getElementById("show").hidden) hideShow(); });
"""


def build_tool(lang):
    L = LANGS[lang]; U = L["ui"]; x = X[lang]; S = SHORT[lang]; d = L["dir"]; up = "../" if d else ""
    path = d
    alt = {k: LANGS[k]["dir"] for k in LANGS}
    topics = "".join(f'<a href="{t["slug"]}.html">{e(t["short"])}</a>' for t in task_list(lang))
    keys = ("staff", "means", "stay_title", "taxi_card", "taxi_ko", "taxi_means", "deliv_card", "deliv_ko", "deliv_means", "station", "checkin", "contact", "note", "map")
    data = {"ui": U, "x": {k: x[k] for k in keys}, "s": S, "tasks": task_list(lang), "check": L["check"], "checked": CHECKED[lang], "lang": lang}
    prof = "".join(f'<label><input type="radio" name="profile" value="{p}"{" checked" if p == "visitor" else ""}><span>{e(S["prof"][p])}</span></label>' for p in ("visitor", "krsim", "arc"))
    dev = "".join(f'<label><input type="radio" name="device" value="{v}"{" checked" if v == "ios" else ""}><span>{e(U[v])}</span></label>' for v in ("ios", "android"))
    steps = "".join(f"<li><b>{e(a)}</b>{e(b)}</li>" for a, b in x["first"])
    body = f"""
{hero(lang, alt, up, x['hook'], x['lede'])}
<div class="setupbar"><div class="wrap">
  <div class="seg" role="radiogroup" aria-label="{e(S['setup_q'])}">{prof}</div>
  <div class="seg" role="radiogroup" aria-label="{e(U['device_q'])}">{dev}</div>
</div></div>
<div class="wrap">
  <section class="stay" id="stay" hidden aria-live="polite"></section>
  <div class="score" id="score" aria-live="polite"></div>
  <p class="hint">{e(S['tap'])}</p>
  <main class="rows" id="rows"></main>
  <details class="panel" open><summary>{e(U['cl_title'])}</summary><div class="in">
    <p class="hint">{e(U['cl_lead'])}</p><ol id="checklist"></ol>
    <div class="actions"><button class="btn" type="button" id="copy-btn">{e(U['copy'])}</button><span class="copied" id="copied" role="status"></span></div>
  </div></details>
  <details class="panel" id="first-24"><summary>{e(x['first_title'])}</summary><div class="in timeline"><p class="hint">{e(x['first_lead'])}</p><ol>{steps}</ol></div></details>
  <nav class="topics">{topics}<a href="changes.html">{e(x['nav_changes'])}</a></nav>
  <footer><div>{e(U['how'])}</div><div>{U['hosts'].format(base=up)}</div><div>{e(U['indep'])}</div></footer>
</div>
{SHOW_HTML(lang)}
<script>
const D = {json.dumps(data, ensure_ascii=False)};
{COMMON_JS}
{TOOL_JS}
</script>
</body>
</html>
"""
    write(path + "index.html", head(lang, f"{BRAND}: {x['hook']}", x["lede"], path, alt) + body)
    return path


TOOL_JS = r"""
const U = D.ui, XS = D.x, S = D.s;
function resolve(t, p, dev) { if (t.all) return t.all; let v = t.v[p]; if (typeof v === "string") v = t.v[v]; if (t.dev && v[dev]) v = v[dev]; return v; }
function render() {
  const p = document.querySelector('input[name="profile"]:checked').value;
  const dev = document.querySelector('input[name="device"]:checked').value;
  const open = new Set([...document.querySelectorAll(".row[open]")].map(r => r.id));
  const rows = document.getElementById("rows"); rows.replaceChildren();
  const n = { ok: 0, warn: 0, mixed: 0, bad: 0 };
  for (const t of D.tasks) {
    const v = resolve(t, p, dev); n[v.s]++;
    const row = el("details", { class: "row " + v.s, id: "task-" + t.id });
    if (open.has(row.id)) row.open = true;
    const sum = el("summary");
    const txt = el("span", { class: "txt" }, [el("span", { class: "top" }, [el("span", { class: "name", text: t.short }), el("span", { class: "pill " + v.s, text: U.labels[v.s] })]), el("span", { class: "sub", text: v.verdict })]);
    sum.append(el("span", { class: "ic", html: t.icon }), txt);
    row.append(sum);
    const body = el("div", { class: "body" });
    body.append(el("p", { class: "verdict", text: v.verdict }));
    body.append(el("ol", { class: "steps" }, v.route.map(r => el("li", { text: r }))));
    const fb = el("p", { class: "fallback" }); fb.append(el("b", { text: U.fails.replace(/[:：]\s*$/, "") }), v.fallback); body.append(fb);
    const act = el("div", { class: "actions" });
    for (const [ko, m] of t.phrases) { const b = el("button", { type: "button", class: "btn alt", text: S.show + ": " + ko }); b.addEventListener("click", () => show(S.show, ko, "", XS.means + ": " + m)); act.append(b); }
    act.append(el("a", { class: "btn ghost", href: t.slug + ".html", text: S.guide + " →" }));
    body.append(act);
    const det = el("details"); det.append(el("summary", { text: S.details })); const ul = el("ul");
    for (const x of (t.notes || [])) ul.append(el("li", { text: x }));
    for (const [nm, url] of t.sources) { const li = el("li"); li.append(el("a", { href: url, rel: "noopener", target: "_blank", text: nm })); ul.append(li); }
    det.append(ul);
    const key = "wik-report-" + t.id + "-" + p, rep = el("div", { class: "report" }), thx = el("span", { role: "status" });
    for (const [val, txt] of [["yes", U.worked], ["no", U.failed]]) {
      const b = el("button", { type: "button", "aria-pressed": String(store(key) === val), text: txt });
      b.addEventListener("click", () => {
        if (store(key) !== val) count(`report/${D.lang}/${t.id}/${p}/${dev}/${val}`, `${t.id} ${p} ${val}`);
        store(key, val); rep.querySelectorAll("button").forEach(x => x.setAttribute("aria-pressed", String(x === b))); thx.textContent = U.thanks;
      });
      rep.append(b);
    }
    rep.append(thx);
    body.append(el("div", { class: "foot" }, [el("span", { text: U.checked + " " + D.checked }), rep, det]));
    row.append(body); rows.append(row);
  }
  const sc = document.getElementById("score"); sc.replaceChildren();
  for (const k of ["ok", "warn", "mixed", "bad"]) if (n[k]) sc.append(el("span", { class: "pill " + k, text: n[k] + " · " + U.labels[k] }));
  const items = (p === "arc" ? D.check.arc : D.check.visitor).slice();
  if (p !== "arc") items.splice(3, 0, dev === "ios" ? D.check.ios_tm : D.check.and_tm);
  document.getElementById("checklist").replaceChildren(...items.map(i => el("li", { text: i })));
  store("wik-setup", p + "|" + dev);
}
function stay() {
  let g = null;
  try { const m = location.hash.match(/[#&]g=([A-Za-z0-9_-]+)/); if (m) { const b = atob(m[1].replace(/-/g, "+").replace(/_/g, "/")); g = JSON.parse(new TextDecoder().decode(Uint8Array.from(b, c => c.charCodeAt(0)))); } } catch (e) { g = null; }
  if (!g || typeof g !== "object") return;
  const s = (k, n) => String(g[k] || "").slice(0, n);
  const box = document.getElementById("stay");
  box.append(el("h2", { text: XS.stay_title + (s("n", 60) ? ": " + s("n", 60) : "") }));
  const a = s("a", 160);
  if (a) {
    box.append(el("div", { class: "addr", lang: "ko", text: a }));
    const act = el("div", { class: "actions" });
    const t1 = el("button", { type: "button", class: "btn alt", text: S.show_driver }); t1.addEventListener("click", () => show(XS.taxi_card, XS.taxi_ko, a, XS.means + ": " + XS.taxi_means));
    const t2 = el("button", { type: "button", class: "btn ghost", text: XS.deliv_card }); t2.addEventListener("click", () => show(XS.deliv_card, a, XS.deliv_ko, XS.means + ": " + XS.deliv_means));
    act.append(t1, t2, el("a", { class: "btn ghost", href: "https://map.naver.com/p/search/" + encodeURIComponent(a), rel: "noopener", target: "_blank", text: XS.map }));
    box.append(act);
  }
  const dl = el("dl", { class: "kv" });
  for (const [k, lbl, n] of [["s", XS.station, 80], ["c", XS.checkin, 40], ["k", XS.contact, 80], ["t", XS.note, 280]]) if (s(k, n)) dl.append(el("dt", { text: lbl }), el("dd", { text: s(k, n) }));
  if (dl.children.length) box.append(dl);
  box.hidden = false;
  if (s("n", 60)) count(`host/${s("n", 60)}`, "host stay page");
}
const saved = store("wik-setup");
if (saved) { const [p, d] = saved.split("|"); const a = document.querySelector(`input[name="profile"][value="${p}"]`); if (a) a.checked = true; const b = document.querySelector(`input[name="device"][value="${d}"]`); if (b) b.checked = true; }
document.querySelectorAll('input[name="profile"], input[name="device"]').forEach(i => i.addEventListener("change", render));
document.getElementById("copy-btn").addEventListener("click", async () => {
  const text = U.cl_head.replace("{d}", D.checked) + "\n" + [...document.querySelectorAll("#checklist li")].map((li, i) => (i + 1) + ". " + li.textContent).join("\n");
  const out = document.getElementById("copied");
  try { await navigator.clipboard.writeText(text); out.textContent = U.copied; count(`copy-checklist/${D.lang}`, "copy checklist"); } catch (e) { out.textContent = U.copy_fail; }
});
render(); stay();
const target = location.hash.match(/^#task-[\w-]+$/); if (target) { const r = document.querySelector(target[0]); if (r) r.open = true; }
"""

TOPIC_JS = r"""
(function () {
  document.querySelectorAll("[data-show]").forEach(b => b.addEventListener("click", () => show(b.dataset.lbl, b.dataset.show, "", b.dataset.mean)));
  const saved = (store("wik-setup") || "visitor|ios").split("|");
  const blocks = [...document.querySelectorAll(".card[data-p]")];
  if (blocks.length < 2) return;
  let shown = 0;
  for (const b of blocks) { const ok = b.dataset.p === saved[0] && (!b.dataset.d || b.dataset.d === saved[1]); b.hidden = !ok; if (ok) shown++; }
  if (!shown) { blocks.forEach(b => b.hidden = false); return; }
  const btn = document.getElementById("show-all"); btn.hidden = false;
  btn.addEventListener("click", () => { blocks.forEach(b => b.hidden = false); btn.hidden = true; });
})();
"""


def build_topic(lang, t):
    L = LANGS[lang]; U = L["ui"]; x = X[lang]; S = SHORT[lang]; d = L["dir"]; up = "../" if d else ""
    path = f"{d}{t['slug']}.html"
    alt = {k: f"{LANGS[k]['dir']}{t['slug']}.html" for k in LANGS}
    fail_lbl = U["fails"].strip().rstrip(":：").strip()
    blocks = []
    profiles = ["visitor", "krsim", "arc"] if "all" not in t else [None]
    for p in profiles:
        devices = ["ios", "android"] if t.get("dev") and p != "arc" else [None]
        for dv in devices:
            v = resolve(t, p or "visitor", dv or "ios")
            heading = U["for_profile"][p] if p else U["labels"][v["s"]]
            if dv: heading += f" · {U[dv]}"
            route = "".join(f"<li>{e(r)}</li>" for r in v["route"])
            attrs = (f' data-p="{p}"' if p else "") + (f' data-d="{dv}"' if dv else "")
            blocks.append(f"""<article class="card {v['s']}"{attrs}><div class="actions" style="justify-content:space-between;align-items:center"><h2>{e(heading)}</h2><span class="pill {v['s']}">{e(U['labels'][v['s']])}</span></div>
<p class="verdict">{e(v['verdict'])}</p><ol class="steps">{route}</ol><p class="fallback"><b>{e(fail_lbl)}</b>{e(v['fallback'])}</p></article>""")
    phrases = "".join(f'<button class="btn alt" type="button" data-show="{e(ko)}" data-lbl="{e(S["show"])}" data-mean="{e(x["means"])}: {e(m)}">{e(S["show"])}: {e(ko)}</button>' for ko, m in t["phrases"])
    notes = "".join(f"<li>{e(n)}</li>" for n in t.get("notes", []))
    srcs = "".join(f'<li><a href="{e(u)}" rel="noopener" target="_blank">{e(n)}</a></li>' for n, u in t["sources"])
    others = "".join(f'<a href="{o["slug"]}.html">{e(o["short"])}</a>' for o in task_list(lang) if o["id"] != t["id"])
    body = f"""
{hero(lang, alt, up, t['seo'], t['intro'], trust=False)}
<div class="wrap">
  <p class="hint" style="margin-top:16px">{e(U['checked'])} {e(CHECKED[lang])} · <a href="changes.html">{e(x['nav_changes'])}</a></p>
  <div class="actions"><a class="btn" href="./#task-{t['id']}">{e(U['open_tool'])}</a>{phrases}</div>
  <main class="cards">{''.join(blocks)}<button class="linkbtn" type="button" id="show-all" hidden>{e(x['others'])}</button></main>
  <details class="panel"><summary>{e(S['details'])}</summary><div class="in notes"><ul>{notes}{srcs}</ul></div></details>
  <nav class="topics">{others}<a href="./#first-24">{e(x['nav_first'])}</a></nav>
  <footer><div>{e(x['trust'])}</div><div>{U['hosts'].format(base=up)}</div><div>{e(U['indep'])}</div></footer>
</div>
{SHOW_HTML(lang)}
<script>{COMMON_JS}{TOPIC_JS}</script>
</body>
</html>
"""
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": t["seo"], "dateModified": CHECKED_ISO, "inLanguage": L["html_lang"], "url": SITE + path, "publisher": {"@type": "Organization", "name": BRAND}}
    ldtag = f'\n<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'
    write(path, head(lang, f"{t['seo']} | {BRAND}", t["intro"], path, alt, ldtag) + body)
    return path


def build_changes(lang):
    L = LANGS[lang]; x = X[lang]; d = L["dir"]; up = "../" if d else ""
    path = f"{d}changes.html"
    alt = {k: f"{LANGS[k]['dir']}changes.html" for k in LANGS}
    rows = "".join(f'<li><b>{e(dt)}</b>{e(tx)}</li>' for dt, tx in x["changes"])
    body = f"""
{hero(lang, alt, up, x['changes_title'], x['changes_lead'], trust=False)}
<div class="wrap">
  <section class="panel" style="margin-top:18px"><div class="in timeline" style="padding-top:16px"><ol>{rows}</ol></div></section>
  <div class="actions"><a class="btn" href="./">{e(L['ui']['open_tool'])}</a></div>
  <footer><div>{e(x['trust'])}</div></footer>
</div>
</body>
</html>
"""
    write(path, head(lang, f"{x['changes_title']} | {BRAND}", x["changes_lead"], path, alt) + body)
    return path


def write(rel, text):
    full = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(full) or ".", exist_ok=True)
    open(full, "w", encoding="utf-8").write(text)


def main():
    paths = []
    for lang in LANGS:
        paths.append(build_tool(lang))
        paths.append(build_changes(lang))
        for t in task_list(lang):
            paths.append(build_topic(lang, t))
    paths.append("hosts.html")
    urls = "".join(f"<url><loc>{SITE}{p}</loc><lastmod>{CHECKED_ISO}</lastmod></url>\n" for p in paths)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
    print(f"built {len(paths)} pages")


if __name__ == "__main__":
    main()
