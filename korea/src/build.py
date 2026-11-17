"""Builds Works in Korea: one checker page and one page per topic, in each language.
Run from the repo root:  python korea/src/build.py
Content lives in data.py, styles in style.css. Output goes to korea/ (committed, served by GitHub Pages).
"""
import html, json, os, sys

sys.path.insert(0, os.path.dirname(__file__))
from data import CHECKED, CHECKED_ISO, LANGS, SOURCES, TASK_META  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
SITE = "https://eddpositive.github.io/korea/"
GOAT = "https://eddpositive.goatcounter.com/count"
CSS = open(os.path.join(os.path.dirname(__file__), "style.css"), encoding="utf-8").read()
EXTRA_CSS = """
.host { background: var(--accent-soft); border-radius: 12px; padding: 12px 14px; margin: 16px 0 0; font-weight: 500; }
.langs { display: flex; gap: 12px; flex-wrap: wrap; font-size: 14px; margin-top: 8px; }
.langs a[aria-current="page"] { font-weight: 600; color: var(--ink); text-decoration: none; }
.topics { display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 22px; }
.topics a { padding: 6px 12px; border: 1px solid var(--line); border-radius: 999px; background: var(--surface); text-decoration: none; font-size: 14px; }
.profile h2 { font: 700 18px/1.3 var(--display); margin: 0; }
.cta-tool { display: inline-block; margin: 6px 0 18px; }
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
<meta property="og:type" content="website"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{SITE}{path}">
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
        out.append(t)
    return out


def resolve(t, profile, device):
    if "all" in t: return t["all"]
    v = t["v"][profile]
    if isinstance(v, str): v = t["v"][v]
    if t.get("dev") and device in v: v = v[device]
    return v


def build_tool(lang):
    L = LANGS[lang]; U = L["ui"]; d = L["dir"]; up = "../" if d else ""
    path = d
    alt = {k: LANGS[k]["dir"] for k in LANGS}
    topics = "".join(f'<a href="{t["slug"]}.html">{e(t["title"])}</a>' for t in task_list(lang))
    data = {"ui": U, "tasks": task_list(lang), "check": L["check"], "checked": CHECKED[lang], "lang": lang}
    body = f"""
  <header class="top">
    <div class="brand"><h1>{e(U['title'])}</h1><span class="kr">{e(U['kr'])}</span></div>
    {lang_links(lang, alt, up)}
    <p class="host" id="host" hidden></p>
    <p class="lede">{e(U['lede'])}</p>
  </header>
  <section class="setup" aria-labelledby="setup-title">
    <h2 id="setup-title">{e(U['setup'])}</h2>
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
  <div class="summary" id="summary" aria-live="polite"></div>
  <main class="tasks" id="tasks"></main>
  <section class="checklist" aria-labelledby="cl-title">
    <h2 id="cl-title">{e(U['cl_title'])}</h2>
    <p>{e(U['cl_lead'])}</p>
    <ol id="checklist"></ol>
    <button class="btn" type="button" id="copy-btn">{e(U['copy'])}</button><span class="copied" id="copied" role="status"></span>
  </section>
  <h2>{e(U['guides'])}</h2>
  <nav class="topics">{topics}</nav>
  <footer>
    <div>{e(U['how'])}</div>
    <div>{U['hosts'].format(base=up)}</div>
    <div>{e(U['indep'])}</div>
  </footer>
</div>
<script>
const D = {json.dumps(data, ensure_ascii=False)};
{TOOL_JS}
</script>
</body>
</html>
"""
    write(path + "index.html", head(lang, f"{U['title']} · {U['kr']}", U["meta_desc"], path, alt) + body)
    return path


TOOL_JS = r"""
const U = D.ui;
function resolve(t, p, dev) { if (t.all) return t.all; let v = t.v[p]; if (typeof v === "string") v = t.v[v]; if (t.dev && v[dev]) v = v[dev]; return v; }
function el(tag, attrs = {}, kids = []) { const n = document.createElement(tag); for (const [k, v] of Object.entries(attrs)) { if (k === "text") n.textContent = v; else n.setAttribute(k, v); } for (const c of [].concat(kids)) if (c) n.append(c); return n; }
function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }
function count(path, title) { try { if (window.goatcounter && window.goatcounter.count) window.goatcounter.count({ path, title, event: true }); } catch (e) {} }
function render() {
  const p = document.querySelector('input[name="profile"]:checked').value;
  const dev = document.querySelector('input[name="device"]:checked').value;
  const box = document.getElementById("tasks"); box.replaceChildren();
  const n = { ok: 0, warn: 0, mixed: 0, bad: 0 };
  for (const t of D.tasks) {
    const v = resolve(t, p, dev); n[v.s]++;
    const c = el("article", { class: "task " + v.s, id: "task-" + t.id });
    const h = el("h3"); h.append(el("a", { href: t.slug + ".html", text: t.title, style: "color:inherit;text-decoration:none" }));
    c.append(el("div", { class: "task-head" }, [h, el("span", { class: "chip " + v.s, text: U.labels[v.s] })]));
    c.append(el("p", { class: "verdict", text: v.verdict }));
    c.append(el("ol", { class: "route" }, v.route.map(r => el("li", { text: r }))));
    const fb = el("p", { class: "fallback" }); fb.append(el("strong", { text: U.fails }), v.fallback); c.append(fb);
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
  const sum = document.getElementById("summary"); sum.replaceChildren(el("b", { text: U.for_setup }));
  for (const k of ["ok", "warn", "mixed", "bad"]) if (n[k]) sum.append(el("span", { class: "chip " + k, text: n[k] + " · " + U.labels[k] }));
  const items = (p === "arc" ? D.check.arc : D.check.visitor).slice();
  if (p !== "arc") items.splice(3, 0, dev === "ios" ? D.check.ios_tm : D.check.and_tm);
  document.getElementById("checklist").replaceChildren(...items.map(i => el("li", { text: i })));
  store("wik-setup", p + "|" + dev);
}
const saved = store("wik-setup");
if (saved) { const [p, d] = saved.split("|"); const a = document.querySelector(`input[name="profile"][value="${p}"]`); if (a) a.checked = true; const b = document.querySelector(`input[name="device"][value="${d}"]`); if (b) b.checked = true; }
document.querySelectorAll('input[name="profile"], input[name="device"]').forEach(i => i.addEventListener("change", render));
document.getElementById("copy-btn").addEventListener("click", async () => {
  const text = U.cl_head.replace("{d}", D.checked) + "\n" + [...document.querySelectorAll("#checklist li")].map((li, i) => (i + 1) + ". " + li.textContent).join("\n");
  const out = document.getElementById("copied");
  try { await navigator.clipboard.writeText(text); out.textContent = U.copied; count(`copy-checklist/${D.lang}`, "copy checklist"); } catch (e) { out.textContent = U.copy_fail; }
});
render();
try { const h = new URLSearchParams(location.search).get("host"); if (h) { const b = document.getElementById("host"); b.textContent = U.host_banner.replace("{h}", h.slice(0, 60)); b.hidden = false; count(`host/${h.slice(0, 60)}`, "host link"); } } catch (e) {}
"""


def build_topic(lang, t):
    L = LANGS[lang]; U = L["ui"]; d = L["dir"]; up = "../" if d else ""
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
            blocks.append(f"""<article class="task {v['s']} profile"><div class="task-head"><h2>{e(heading)}</h2><span class="chip {v['s']}">{e(U['labels'][v['s']])}</span></div>
<p class="verdict">{e(v['verdict'])}</p><ol class="route">{route}</ol><p class="fallback"><strong>{e(U['fails'])}</strong>{e(v['fallback'])}</p></article>""")
    notes = "".join(f"<li>{e(n)}</li>" for n in t.get("notes", []))
    srcs = "".join(f'<li><a href="{e(u)}" rel="noopener" target="_blank">{e(n)}</a></li>' for n, u in t["sources"])
    others = "".join(f'<a href="{o["slug"]}.html">{e(o["title"])}</a>' for o in task_list(lang) if o["id"] != t["id"])
    body = f"""
  <header class="top">
    <p class="meta"><a href="./">← {e(U['title'])}</a></p>
    <div class="brand"><h1>{e(t['seo'])}</h1></div>
    {lang_links(lang, alt, up)}
    <p class="lede">{e(t['intro'])}</p>
    <p class="meta">{e(U['checked'])} {e(CHECKED[lang])}</p>
  </header>
  <a class="btn cta-tool" href="./">{e(U['open_tool'])}</a>
  <main class="tasks">{''.join(blocks)}</main>
  <section class="checklist"><h2>{e(U['sources'])}</h2><ul>{notes}{srcs}</ul></section>
  <h2>{e(U['guides'])}</h2><nav class="topics">{others}</nav>
  <footer><div>{e(U['how'])}</div><div>{U['hosts'].format(base=up)}</div><div>{e(U['indep'])}</div></footer>
</div>
</body>
</html>
"""
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": t["seo"], "dateModified": CHECKED_ISO, "inLanguage": L["html_lang"], "url": SITE + path}
    page = head(lang, t["seo"], t["intro"], path, alt).replace("</head>", f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n</head>', 1) + body
    write(path, page)
    return path


def write(rel, text):
    full = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(full) or ".", exist_ok=True)
    open(full, "w", encoding="utf-8").write(text)


def main():
    paths = []
    for lang in LANGS:
        paths.append(build_tool(lang))
        for t in task_list(lang):
            paths.append(build_topic(lang, t))
    paths.append("hosts.html")
    urls = "".join(f"<url><loc>{SITE}{p}</loc><lastmod>{CHECKED_ISO}</lastmod></url>\n" for p in paths)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
    print(f"built {len(paths)} pages")


if __name__ == "__main__":
    main()
