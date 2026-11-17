"""Builds EasyModeKorea: checker page, topic pages and a changelog page, in each language.
Run from the repo root:  python korea/src/build.py
Content: data.py (answers) and data_extra.py (hook, phrases, first 24 hours, changelog, host-stay strings).
Host stay pages need no server: the host's details travel in the link's #g= hash, so they are
never sent to any server (not even analytics) and are rendered with textContent only.
"""
import html, json, os, sys

sys.path.insert(0, os.path.dirname(__file__))
from data import CHECKED, CHECKED_ISO, LANGS, SOURCES, TASK_META  # noqa: E402
from data_extra import BRAND, PHRASES, X  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
SITE = "https://eddpositive.github.io/korea/"
GOAT = "https://eddpositive.goatcounter.com/count"
CSS = open(os.path.join(os.path.dirname(__file__), "style.css"), encoding="utf-8").read()
EXTRA_CSS = """
.hook { font: 800 clamp(26px, 6vw, 40px)/1.12 var(--display); letter-spacing: -0.02em; margin: 6px 0 0; text-wrap: balance; }
.brandline { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; font: 700 15px var(--body); color: var(--accent); }
.trust { font-size: 13px; color: var(--muted); margin: 8px 0 0; }
.langs { display: flex; gap: 12px; flex-wrap: wrap; font-size: 14px; margin-top: 8px; }
.langs a[aria-current="page"] { font-weight: 600; color: var(--ink); text-decoration: none; }
.topics { display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 22px; }
.topics a { padding: 6px 12px; border: 1px solid var(--line); border-radius: 999px; background: var(--surface); text-decoration: none; font-size: 14px; }
.glance { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 8px; margin: 4px 0 16px; }
.glance a { display: flex; align-items: center; gap: 8px; padding: 10px 12px; border-radius: 10px; background: var(--surface); border: 1px solid var(--line); text-decoration: none; color: var(--ink); font-size: 14px; font-weight: 500; }
.glance a::before { content: ""; flex: none; width: 10px; height: 10px; border-radius: 50%; background: var(--muted); }
.glance a.ok::before { background: var(--ok); } .glance a.warn::before { background: var(--warn); } .glance a.mixed::before { background: var(--mixed); } .glance a.bad::before { background: var(--bad); }
.staff { border: 2px dashed var(--line); border-radius: 12px; padding: 12px 14px; display: grid; gap: 4px; }
.staff .lbl { font-size: 12px; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); font-weight: 600; }
.staff .ko { font: 700 22px/1.35 "Apple SD Gothic Neo", "Noto Sans KR", "Malgun Gothic", var(--body); }
.staff .mean { font-size: 14px; color: var(--muted); }
.stay { background: var(--surface); border: 2px solid var(--accent); border-radius: 14px; padding: 16px; margin: 18px 0; display: grid; gap: 12px; }
.stay h2 { font: 700 22px var(--display); margin: 0; }
.stay .from { color: var(--muted); font-size: 14px; margin: 0; }
.stay .big { font: 800 26px/1.35 "Apple SD Gothic Neo", "Noto Sans KR", "Malgun Gothic", var(--body); word-break: keep-all; }
.stay dl { margin: 0; display: grid; gap: 6px; } .stay dt { font-size: 12px; color: var(--muted); } .stay dd { margin: 0 0 6px; font-weight: 500; }
.first ol { padding-left: 22px; display: grid; gap: 8px; margin: 0; } .first b { display: block; }
.profile[hidden] { display: none; }
.cta-tool { display: inline-block; margin: 6px 0 18px; }
.linkbtn { background: none; border: 0; color: var(--accent); font: 500 14px var(--body); cursor: pointer; padding: 0; text-decoration: underline; }
"""
e = lambda s: html.escape(str(s), quote=True)


def head(lang, title, desc, path, alt_paths):
    alts = "".join(f'<link rel="alternate" hreflang="{LANGS[k]["html_lang"]}" href="{SITE}{p}">' for k, p in alt_paths.items())
    alts += f'<link rel="alternate" hreflang="x-default" href="{SITE}{alt_paths["en"]}">'
    return f"""<!DOCTYPE html>
<html lang="{LANGS[lang]['html_lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE}{path}">{alts}
<meta property="og:type" content="website"><meta property="og:site_name" content="{BRAND}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{SITE}{path}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
{CSS}{EXTRA_CSS}</style>
<script data-goatcounter="{GOAT}" async src="//gc.zgo.at/count.js"></script>
</head>
<body>
<div class="wrap">"""


def lang_links(cur, rel_paths, prefix):
    out = []
    for k, L in LANGS.items():
        cur_attr = ' aria-current="page"' if k == cur else ""
        out.append(f'<a href="{prefix}{rel_paths[k]}" hreflang="{L["html_lang"]}"{cur_attr}>{e(L["name"])}</a>')
    return f'<nav class="langs" aria-label="{e(LANGS[cur]["ui"]["langs"])}">' + "".join(out) + "</nav>"


def task_list(lang):
    T = LANGS[lang]["tasks"]
    out = []
    for tid, slug, srcs in TASK_META:
        t = dict(T[tid]); t["id"] = tid; t["slug"] = slug
        t["sources"] = [SOURCES[s] for s in srcs]
        t["phrases"] = [[ko, m[lang]] for ko, m in PHRASES.get(tid, [])]
        out.append(t)
    return out


def resolve(t, profile, device):
    if "all" in t: return t["all"]
    v = t["v"][profile]
    if isinstance(v, str): v = t["v"][v]
    if t.get("dev") and device in v: v = v[device]
    return v


def staff_html(lang, t):
    x = X[lang]
    return "".join(f'<div class="staff"><span class="lbl">{e(x["staff"])}</span><span class="ko" lang="ko">{e(ko)}</span><span class="mean">{e(x["means"])}: {e(m)}</span></div>' for ko, m in t["phrases"])


def first24_html(lang):
    x = X[lang]
    steps = "".join(f"<li><b>{e(a)}</b>{e(b)}</li>" for a, b in x["first"])
    return f'<section class="checklist first" id="first-24"><h2>{e(x["first_title"])}</h2><p>{e(x["first_lead"])}</p><ol>{steps}</ol></section>'


FOOT = lambda lang, up: f"""<footer><div>{e(X[lang]['trust'])}</div><div>{e(LANGS[lang]['ui']['how'])}</div><div>{LANGS[lang]['ui']['hosts'].format(base=up)}</div><div>{e(LANGS[lang]['ui']['indep'])}</div></footer>"""


def build_tool(lang):
    L = LANGS[lang]; U = L["ui"]; x = X[lang]; d = L["dir"]; up = "../" if d else ""
    path = d
    alt = {k: LANGS[k]["dir"] for k in LANGS}
    topics = "".join(f'<a href="{t["slug"]}.html">{e(t["title"])}</a>' for t in task_list(lang))
    data = {"ui": U, "x": {k: x[k] for k in ("staff", "means", "stay_title", "stay_from", "taxi_card", "taxi_ko", "taxi_means", "deliv_card", "deliv_ko", "deliv_means", "station", "checkin", "contact", "note", "map")},
            "tasks": task_list(lang), "check": L["check"], "checked": CHECKED[lang], "lang": lang}
    body = f"""
  <header class="top">
    <div class="brandline">{BRAND}</div>
    <h1 class="hook">{e(x['hook'])}</h1>
    {lang_links(lang, alt, up)}
    <p class="lede">{e(x['lede'])}</p>
    <p class="trust">{e(x['trust'])}</p>
  </header>
  <section class="stay" id="stay" hidden aria-live="polite"></section>
  <section class="setup" aria-labelledby="setup-title">
    <h2 id="setup-title">{e(x['your_mode'])}</h2>
    <fieldset><legend>{e(U['phone_q'])}</legend><div class="opts">
      <label class="opt"><input type="radio" name="profile" id="p-visitor" value="visitor" checked><span>{e(U['p_visitor'][0])}<small>{e(U['p_visitor'][1])}</small></span></label>
      <label class="opt"><input type="radio" name="profile" id="p-krsim" value="krsim"><span>{e(U['p_krsim'][0])}<small>{e(U['p_krsim'][1])}</small></span></label>
      <label class="opt"><input type="radio" name="profile" id="p-arc" value="arc"><span>{e(U['p_arc'][0])}<small>{e(U['p_arc'][1])}</small></span></label>
    </div></fieldset>
    <fieldset><legend>{e(U['device_q'])}</legend><div class="opts">
      <label class="opt"><input type="radio" name="device" id="d-ios" value="ios" checked><span>{e(U['ios'])}</span></label>
      <label class="opt"><input type="radio" name="device" id="d-android" value="android"><span>{e(U['android'])}</span></label>
    </div></fieldset>
  </section>
  <h2>{e(x['glance'])}</h2>
  <nav class="glance" id="glance" aria-label="{e(x['glance'])}"></nav>
  <main class="tasks" id="tasks"></main>
  <section class="checklist" aria-labelledby="cl-title">
    <h2 id="cl-title">{e(U['cl_title'])}</h2>
    <p>{e(U['cl_lead'])}</p>
    <ol id="checklist"></ol>
    <button class="btn" type="button" id="copy-btn">{e(U['copy'])}</button><span class="copied" id="copied" role="status"></span>
  </section>
  {first24_html(lang)}
  <h2>{e(U['guides'])}</h2>
  <nav class="topics">{topics}<a href="changes.html">{e(x['nav_changes'])}</a></nav>
  {FOOT(lang, up)}
</div>
<script>
const D = {json.dumps(data, ensure_ascii=False)};
{TOOL_JS}
</script>
</body>
</html>
"""
    write(path + "index.html", head(lang, f"{BRAND}: {x['hook']}", x["lede"], path, alt) + body)
    return path


COMMON_JS = r"""
function el(tag, attrs = {}, kids = []) { const n = document.createElement(tag); for (const [k, v] of Object.entries(attrs)) { if (k === "text") n.textContent = v; else n.setAttribute(k, v); } for (const c of [].concat(kids)) if (c) n.append(c); return n; }
function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }
function count(path, title) { try { if (window.goatcounter && window.goatcounter.count) window.goatcounter.count({ path, title, event: true }); } catch (e) {} }
"""

TOOL_JS = COMMON_JS + r"""
const U = D.ui, XS = D.x;
function resolve(t, p, dev) { if (t.all) return t.all; let v = t.v[p]; if (typeof v === "string") v = t.v[v]; if (t.dev && v[dev]) v = v[dev]; return v; }
function staff(t) { return t.phrases.map(([ko, m]) => el("div", { class: "staff" }, [el("span", { class: "lbl", text: XS.staff }), el("span", { class: "ko", lang: "ko", text: ko }), el("span", { class: "mean", text: XS.means + ": " + m })])); }
function render() {
  const p = document.querySelector('input[name="profile"]:checked').value;
  const dev = document.querySelector('input[name="device"]:checked').value;
  const box = document.getElementById("tasks"), glance = document.getElementById("glance");
  box.replaceChildren(); glance.replaceChildren();
  for (const t of D.tasks) {
    const v = resolve(t, p, dev);
    glance.append(el("a", { href: "#task-" + t.id, class: v.s, text: t.title, title: U.labels[v.s] }));
    const c = el("article", { class: "task " + v.s, id: "task-" + t.id });
    const h = el("h3"); h.append(el("a", { href: t.slug + ".html", text: t.title, style: "color:inherit;text-decoration:none" }));
    c.append(el("div", { class: "task-head" }, [h, el("span", { class: "chip " + v.s, text: U.labels[v.s] })]));
    c.append(el("p", { class: "verdict", text: v.verdict }));
    c.append(el("ol", { class: "route" }, v.route.map(r => el("li", { text: r }))));
    const fb = el("p", { class: "fallback" }); fb.append(el("strong", { text: U.fails }), v.fallback); c.append(fb);
    for (const s of staff(t)) c.append(s);
    const det = el("details"); det.append(el("summary", { text: U.sources })); const ul = el("ul");
    for (const x of (t.notes || [])) ul.append(el("li", { text: x }));
    for (const [nm, url] of t.sources) { const li = el("li"); li.append(el("a", { href: url, rel: "noopener", target: "_blank", text: nm })); ul.append(li); }
    det.append(ul); c.append(det);
    const key = "wik-report-" + t.id + "-" + p, rep = el("div", { class: "report" }), thx = el("span", { class: "thanks", role: "status" });
    for (const [val, txt] of [["yes", U.worked], ["no", U.failed]]) {
      const b = el("button", { type: "button", "aria-pressed": String(store(key) === val), text: txt });
      b.addEventListener("click", () => {
        if (store(key) !== val) count(`report/${D.lang}/${t.id}/${p}/${dev}/${val}`, `${t.id} ${p} ${val}`);
        store(key, val); rep.querySelectorAll("button").forEach(x => x.setAttribute("aria-pressed", String(x === b))); thx.textContent = U.thanks;
      });
      rep.append(b);
    }
    rep.append(thx);
    c.append(el("div", { class: "meta" }, [el("span", { text: U.checked + " " + D.checked }), rep]));
    box.append(c);
  }
  const items = (p === "arc" ? D.check.arc : D.check.visitor).slice();
  if (p !== "arc") items.splice(3, 0, dev === "ios" ? D.check.ios_tm : D.check.and_tm);
  document.getElementById("checklist").replaceChildren(...items.map(i => el("li", { text: i })));
  store("wik-setup", p + "|" + dev);
}
/* Host stay card: details come from #g=<base64url JSON> and are only ever set as text. */
function stay() {
  let g = null;
  try { const m = location.hash.match(/[#&]g=([A-Za-z0-9_-]+)/); if (m) { const b = atob(m[1].replace(/-/g, "+").replace(/_/g, "/")); g = JSON.parse(new TextDecoder().decode(Uint8Array.from(b, c => c.charCodeAt(0)))); } } catch (e) { g = null; }
  if (!g || typeof g !== "object") return;
  const s = (k, n) => String(g[k] || "").slice(0, n);
  const box = document.getElementById("stay");
  box.append(el("h2", { text: XS.stay_title + (s("n", 60) ? ": " + s("n", 60) : "") }));
  if (s("a", 160)) {
    box.append(el("div", { class: "staff" }, [el("span", { class: "lbl", text: XS.taxi_card }), el("span", { class: "ko", lang: "ko", text: XS.taxi_ko }), el("span", { class: "big", lang: "ko", text: s("a", 160) }), el("span", { class: "mean", text: XS.means + ": " + XS.taxi_means })]));
    box.append(el("div", { class: "staff" }, [el("span", { class: "lbl", text: XS.deliv_card }), el("span", { class: "big", lang: "ko", text: s("a", 160) }), el("span", { class: "ko", lang: "ko", text: XS.deliv_ko }), el("span", { class: "mean", text: XS.means + ": " + XS.deliv_means })]));
    box.append(el("a", { class: "btn", href: "https://map.naver.com/p/search/" + encodeURIComponent(s("a", 160)), rel: "noopener", target: "_blank", text: XS.map }));
  }
  const dl = el("dl");
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
"""

TOPIC_JS = COMMON_JS + r"""
/* Show only the reader's own setup first; the rest stay one tap away. */
(function () {
  const saved = (store("wik-setup") || "visitor|ios").split("|");
  const blocks = [...document.querySelectorAll(".profile[data-p]")];
  if (blocks.length < 2) return;
  let shown = 0;
  for (const b of blocks) { const ok = b.dataset.p === saved[0] && (!b.dataset.d || b.dataset.d === saved[1]); b.hidden = !ok; if (ok) shown++; }
  if (!shown) { blocks.forEach(b => b.hidden = false); return; }
  const btn = document.getElementById("show-all"); btn.hidden = false;
  btn.addEventListener("click", () => { blocks.forEach(b => b.hidden = false); btn.hidden = true; });
})();
"""


def build_topic(lang, t):
    L = LANGS[lang]; U = L["ui"]; x = X[lang]; d = L["dir"]; up = "../" if d else ""
    path = f"{d}{t['slug']}.html"
    alt = {k: f"{LANGS[k]['dir']}{t['slug']}.html" for k in LANGS}
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
            blocks.append(f"""<article class="task {v['s']} profile"{attrs}><div class="task-head"><h2>{e(heading)}</h2><span class="chip {v['s']}">{e(U['labels'][v['s']])}</span></div>
<p class="verdict">{e(v['verdict'])}</p><ol class="route">{route}</ol><p class="fallback"><strong>{e(U['fails'])}</strong>{e(v['fallback'])}</p></article>""")
    notes = "".join(f"<li>{e(n)}</li>" for n in t.get("notes", []))
    srcs = "".join(f'<li><a href="{e(u)}" rel="noopener" target="_blank">{e(n)}</a></li>' for n, u in t["sources"])
    others = "".join(f'<a href="{o["slug"]}.html">{e(o["title"])}</a>' for o in task_list(lang) if o["id"] != t["id"])
    body = f"""
  <header class="top">
    <p class="brandline"><a href="./">{BRAND}</a></p>
    <h1 class="hook">{e(t['seo'])}</h1>
    {lang_links(lang, alt, up)}
    <p class="lede">{e(t['intro'])}</p>
    <p class="meta">{e(U['checked'])} {e(CHECKED[lang])} · <a href="changes.html">{e(x['nav_changes'])}</a></p>
  </header>
  <a class="btn cta-tool" href="./">{e(U['open_tool'])}</a>
  <main class="tasks">{''.join(blocks)}<button class="linkbtn" type="button" id="show-all" hidden>{e(x['others'])}</button>{staff_html(lang, t)}</main>
  <section class="checklist"><h2>{e(U['sources'])}</h2><ul>{notes}{srcs}</ul></section>
  <h2>{e(U['guides'])}</h2><nav class="topics">{others}<a href="./#first-24">{e(x['nav_first'])}</a></nav>
  {FOOT(lang, up)}
</div>
<script>{TOPIC_JS}</script>
</body>
</html>
"""
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": t["seo"], "dateModified": CHECKED_ISO, "inLanguage": L["html_lang"], "url": SITE + path, "publisher": {"@type": "Organization", "name": BRAND}}
    page = head(lang, f"{t['seo']} | {BRAND}", t["intro"], path, alt).replace("</head>", f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n</head>', 1) + body
    write(path, page)
    return path


def build_changes(lang):
    L = LANGS[lang]; x = X[lang]; d = L["dir"]; up = "../" if d else ""
    path = f"{d}changes.html"
    alt = {k: f"{LANGS[k]['dir']}changes.html" for k in LANGS}
    rows = "".join(f'<li><b>{e(dt)}</b> {e(tx)}</li>' for dt, tx in x["changes"])
    body = f"""
  <header class="top"><p class="brandline"><a href="./">{BRAND}</a></p><h1 class="hook">{e(x['changes_title'])}</h1>{lang_links(lang, alt, up)}<p class="lede">{e(x['changes_lead'])}</p></header>
  <section class="checklist first"><ol>{rows}</ol></section>
  <a class="btn cta-tool" href="./">{e(L['ui']['open_tool'])}</a>
  {FOOT(lang, up)}
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
