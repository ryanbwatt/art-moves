#!/usr/bin/env python3
"""Render Art Moves from data and Markdown into static HTML.

Inputs:  src/data/sales.json, src/issues/NNN.md, src/pages/about.md, src/assets/
Outputs: site/ (home, one page per issue, archive, data, method, images, CSV, JSON)

Standard library only. Output is committed, so the host needs no build step.
Links are relative, so the site works at any address.
Run: python3 scripts/build.py
"""
import csv, datetime, html, io, json, pathlib, re, shutil, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import schema as S

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC, OUT = ROOT / "src", ROOT / "site"
NAV = [("Latest", "index.html"), ("Issues", "archive.html"), ("Data", "data.html"), ("Method", "about.html")]
FONTS = ["https://api.fontshare.com/v2/css?f[]=switzer@400,500,600&display=swap",
         "https://api.fontshare.com/v2/css?f[]=gambetta@400,401&display=swap"]
TAGLINE = "Where serious money moves in art and luxury."
esc = html.escape

# ---------- formatting ----------

def money(n, cur):
    sym = S.SYMBOLS.get(cur, cur + " ")
    if n >= 1e9: return f"{sym}{n/1e9:.2f}B"
    if n >= 1e6: return f"{sym}{n/1e6:.2f}".rstrip("0").rstrip(".") + "M"
    if n >= 1e4: return f"{sym}{n/1e3:.0f}k"
    return f"{sym}{n:,.0f}"

def local_price(r):
    return r.get("price_with_premium") if r["price_basis"] == "with_premium" else r.get("price_hammer")

def result(r):
    s = money(local_price(r), r["currency"])
    return s if r["currency"] == "USD" else f"{s} ({money(r['price_usd'], 'USD')})"

def estimate(r, short=False):
    """Estimate range. Tables use short=True so long notes stay on the sale card and in the CSV."""
    if r.get("estimate_low") is None:
        return "No range published" if short else (r.get("estimate_note") or "Not published")
    s = f"{money(r['estimate_low'], r['currency'])} to {money(r['estimate_high'], r['currency'])}"
    return s if short else s + (f" ({r['estimate_note']})" if r.get("estimate_note") else "")

def buyer(r):
    if r["buyer_status"] == "anonymous": return "Anonymous"
    return f"{r['buyer_name']} ({r['buyer_attribution']})"

def evidence(r):
    return "Confirmed by the house" if r["price_source"] == "house" else "Reported by the press"

def day(iso):
    d = datetime.date.fromisoformat(str(iso))
    return f"{d.day} {d:%b %Y}"

def lot_label(r):
    return esc(r["maker"]) + ", <i>" + esc(r["title"]) + "</i>" + (f" ({esc(r['year_made'])})" if r.get("year_made") else "")

# ---------- minimal Markdown ----------

def inline(t):
    t = esc(t, quote=False)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+|[\w./#-]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    return t

def markdown(text, directive=lambda name, arg: ""):
    """Paragraphs, lists, links, bold, and ## headings. Each ## opens a section
    whose heading sits in the left-hand label column."""
    out, para, items, open_sec = [], [], [], False
    def flush():
        if para: out.append("<p>" + inline(" ".join(para)) + "</p>"); para.clear()
        if items: out.append("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in items) + "</ul>"); items.clear()
    for line in text.splitlines():
        s = line.strip()
        m = re.fullmatch(r"\{\{(\w+)(?::([^}]+))?\}\}", s)
        if not s: flush()
        elif m: flush(); out.append(directive(m.group(1), m.group(2)))
        elif s.startswith("## "):
            flush()
            if open_sec: out.append("</div></section>")
            out.append(f'<section class="sec"><h2 class="label">{inline(s[3:])}</h2><div class="sec-body">'); open_sec = True
        elif s.startswith("### "): flush(); out.append(f"<h3>{inline(s[4:])}</h3>")
        elif s.startswith("- "):
            if para: flush()
            items.append(s[2:])
        else:
            if items: flush()
            para.append(s)
    flush()
    if open_sec: out.append("</div></section>")
    return "\n".join(out)

def read_md(path):
    raw = path.read_text()
    meta = {}
    if raw.startswith("---"):
        _, head, raw = raw.split("---", 2)
        for line in head.strip().splitlines():
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, raw

# ---------- components ----------

def sources_for(rows):
    """Number each distinct source URL once, in order of first use."""
    order = {}
    for r in rows:
        for s in r["sources"]:
            order.setdefault(s["url"], (len(order) + 1, s["publisher"]))
    return order

def cites(r, order):
    return " ".join(f'<a class="cite" href="#s{order[s["url"]][0]}">{order[s["url"]][0]}</a>' for s in r["sources"])

def figure(r, cls="plate"):
    img = r.get("image")
    if not img: return ""
    cap = (f'{lot_label(r)}. {esc(img["credit"])}. '
           f'<a href="{esc(img["source_url"])}">{esc(img["license"])}</a>.')
    return (f'<figure class="{cls}"><div class="wall"><img src="img/{esc(img["file"])}" alt="{esc(r["maker"])}, {esc(r["title"])}" loading="lazy"></div>'
            f'<figcaption>{cap}</figcaption></figure>')

def sale_block(r, order):
    facts = [("Price", ("Includes buyer's premium. " if r["price_basis"] == "with_premium" else "Hammer price, before fees. ") + evidence(r)),
             ("Estimate", estimate(r)),
             ("Sale", f"{S.HOUSES[r['house']]} {r['location']}, {day(r['sale_date'])}" + (f", lot {r['lot_number']}" if r.get("lot_number") else "")),
             ("Seller", r.get("seller") or "Not disclosed"),
             ("Buyer", buyer(r)),
             ("Guarantee", r["guarantee"].replace("_", " ").capitalize())]
    for k, label in (("record", "Record"), ("bidding_notes", "Bidding"), ("financing_notes", "Financing")):
        if r.get(k): facts.append((label, r[k]))
    dl = "".join(f"<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>" for k, v in facts)
    return (f'<article class="sale" id="{esc(r["id"])}">{figure(r)}'
            f'<p class="kicker">{esc(S.CATEGORIES[r["category"]])} · {esc(S.HOUSES[r["house"]])} {esc(r["location"])}</p>'
            f'<h3 class="sale-title">{lot_label(r)}</h3><p class="figure-price">{esc(result(r))}</p><dl class="facts">{dl}</dl>'
            f'<p class="why"><strong>Why it matters.</strong> {esc(r["why_it_matters"])} {cites(r, order)}</p></article>')

def sales_table(rows, order=None, sortable=False):
    head = ["Date", "House", "Lot", "Result", "Estimate", "Buyer", "Source"]
    th = "".join(f'<th{" class=num" if h == "Result" else ""}>{h}</th>' for h in head)
    body = []
    for r in sorted(rows, key=lambda r: -r["price_usd"]):
        src = cites(r, order) if order else " ".join(
            f'<a href="{esc(s["url"])}">{esc(s["publisher"])}</a>' for s in r["sources"][:1])
        body.append(
            f'<tr><td data-v="{r["sale_date"]}">{day(r["sale_date"])}</td>'
            f'<td>{esc(S.HOUSES[r["house"]])}<br><span class="dim">{esc(r["location"])}</span></td>'
            f'<td>{lot_label(r)}<br><span class="dim">{esc(S.CATEGORIES[r["category"]])}</span></td>'
            f'<td class="num" data-v="{r["price_usd"]}">{esc(result(r))}<br><span class="dim">{S.PRICE_BASIS[r["price_basis"]]}</span></td>'
            f'<td>{esc(estimate(r, True))}</td><td>{esc(buyer(r))}</td><td>{src}</td></tr>')
    cls = "index sortable" if sortable else "index"
    return f'<div class="scroll"><table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'

def sale_rows(rows, href):
    """Home-page list: image, lot, and result on one line per sale."""
    out = []
    for r in sorted(rows, key=lambda r: -r["price_usd"]):
        img = r.get("image")
        thumb = (f'<img src="img/{esc(img["file"])}" alt="" loading="lazy">' if img
                 else f'<span class="tile">{esc(S.CATEGORIES[r["category"]])}</span>')
        out.append(f'<a class="row" href="{href}#{esc(r["id"])}"><span class="row-thumb">{thumb}</span>'
                   f'<span class="row-main"><span class="row-title">{lot_label(r)}</span>'
                   f'<span class="dim">{esc(S.HOUSES[r["house"]])} {esc(r["location"])} · {day(r["sale_date"])} · Buyer: {esc(buyer(r))}</span></span>'
                   f'<span class="row-price">{esc(result(r))}</span></a>')
    return f'<div class="rows">{"".join(out)}</div>'

def source_list(order):
    if not order: return ""
    li = "".join(f'<li id="s{n}"><a href="{esc(u)}">{esc(p)}</a></li>' for u, (n, p) in order.items())
    return f'<section class="sec"><h2 class="label">Sources</h2><div class="sec-body"><ol class="sources">{li}</ol></div></section>'

SORT_JS = """<script>document.querySelectorAll('.sortable th').forEach(function(th,i){th.tabIndex=0;th.setAttribute('role','button');function go(){var tb=th.closest('table').tBodies[0],d=th.dataset.d==='a'?'d':'a';th.dataset.d=d;[].slice.call(tb.rows).sort(function(a,b){var x=a.cells[i].dataset.v||a.cells[i].textContent,y=b.cells[i].dataset.v||b.cells[i].textContent,n=parseFloat(x)-parseFloat(y);n=isNaN(n)||/-/.test(x)?x.localeCompare(y):n;return d==='a'?n:-n}).forEach(function(r){tb.appendChild(r)})}th.addEventListener('click',go);th.addEventListener('keydown',function(e){if(e.key==='Enter')go()})});</script>"""

def page(title, body, current=None, description="", script=""):
    nav = "".join(f'<a href="{h}"' + (' aria-current="page"' if n == current else "") + f">{n}</a>" for n, h in NAV)
    full = "Art Moves" if title == "Art Moves" else f"{title} · Art Moves"
    return (f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{esc(full)}</title><meta name="description" content="{esc(description or TAGLINE)}">'
            f'<link rel="icon" href="data:,"><link rel="preconnect" href="https://api.fontshare.com">{"".join(f'<link rel="stylesheet" href="{u}">' for u in FONTS)}<link rel="stylesheet" href="site.css"></head>'
            f'<body><a class="skip" href="#main">Skip to content</a><header class="top"><a class="wordmark" href="index.html">Art Moves</a><nav aria-label="Main">{nav}</nav></header>'
            f'<main id="main">\n{body}\n</main>'
            f'<footer class="foot"><span>Art Moves. {TAGLINE} Published Sundays.</span>'
            f'<span>Researched and drafted with Perplexity Computer; edited by a human. <a href="about.html">Method</a></span></footer>{script}</body></html>\n')

# ---------- pages ----------

def main():
    rows = json.loads((SRC / "data" / "sales.json").read_text())
    by_id = {r["id"]: r for r in rows}
    issues = []
    for f in sorted((SRC / "issues").glob("*.md")):
        meta, text = read_md(f)
        meta["number"] = int(meta["number"]); meta["slug"] = f"{meta['number']:03d}"; meta["text"] = text
        meta["rows"] = [r for r in rows if r["issue"] == meta["number"]]
        meta["lead_row"] = by_id.get(meta.get("lead", ""))
        issues.append(meta)
    issues.sort(key=lambda i: -i["number"])
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(SRC / "assets" / "img", OUT / "img")
    shutil.copy(SRC / "assets" / "site.css", OUT / "site.css")

    def issue_meta(it):
        return f'Issue {it["number"]:02d} · {day(it["date"])} · Covers {esc(it["window"])}'
    def banner(it):
        return '<p class="banner">Sample issue for layout review. Not published editorial.</p>' if it.get("status") == "sample" else ""

    for n, it in enumerate(issues):
        order = sources_for(it["rows"])
        def directive(name, arg, it=it, order=order):
            if name == "sale": return sale_block(by_id[arg.strip()], order)
            if name == "table": return sales_table(it["rows"], order)
            raise SystemExit(f"unknown directive {name} in issue {it['slug']}")
        newer = issues[n - 1] if n > 0 else None
        older = issues[n + 1] if n + 1 < len(issues) else None
        pager = "".join(x for x in [
            f'<a href="{older["slug"]}.html">Previous issue</a>' if older else "",
            f'<a href="{newer["slug"]}.html">Next issue</a>' if newer else "",
            '<a href="archive.html">All issues</a>'] if x)
        body = (f'{banner(it)}<header class="issue-head"><p class="label">{issue_meta(it)}</p>'
                f'<h1 class="display">{esc(it["title"])}</h1><p class="standfirst">{esc(it.get("topline", ""))}</p></header>'
                f'\n{markdown(it["text"], directive)}\n{source_list(order)}<nav class="pager" aria-label="Issues">{pager}</nav>')
        (OUT / f"{it['slug']}.html").write_text(page(it["title"], body, description=it.get("topline", "")))

    # home
    if issues:
        top = issues[0]; href = f'{top["slug"]}.html'
        hero = figure(top["lead_row"], "plate hero") if top.get("lead_row") else ""
        home = (f'{banner(top)}{hero}<section class="lead"><p class="label">{issue_meta(top)}</p>'
                f'<div><h1 class="display"><a href="{href}">{esc(top["title"])}</a></h1>'
                f'<p class="standfirst">{esc(top.get("topline", ""))}</p><p><a class="more" href="{href}">Read the issue</a></p></div></section>'
                f'<section class="sec"><h2 class="label">Sales in this issue</h2><div class="sec-body wide">{sale_rows(top["rows"], href)}</div></section>')
        if issues[1:]:
            earlier = "".join(f'<a class="row" href="{i["slug"]}.html"><span class="row-main"><span class="row-title">{esc(i["title"])}</span>'
                              f'<span class="dim">{issue_meta(i)}</span></span></a>' for i in issues[1:6])
            home += f'<section class="sec"><h2 class="label">Earlier issues</h2><div class="sec-body wide"><div class="rows">{earlier}</div></div></section>'
    else:
        home = '<section class="lead"><p class="label">Coming soon</p><div><h1 class="display">The first issue is on its way.</h1></div></section>'
    home += ('<section class="sec"><h2 class="label">About</h2><div class="sec-body"><p class="standfirst">A free weekly brief on who is buying, what they paid, '
             'and what it says about how wealthy families protect and grow capital. Written for readers who know finance and are new to art.</p>'
             '<p><a class="more" href="about.html">How it is made</a></p></div></section>')
    (OUT / "index.html").write_text(page("Art Moves", home, "Latest"))

    # archive
    trs = []
    for i in issues:
        top_row = max(i["rows"], key=lambda r: r["price_usd"], default=None)
        total = sum(r["price_usd"] for r in i["rows"])
        trs.append(f'<tr><td>{i["number"]:02d}</td><td>{day(i["date"])}</td><td><a href="{i["slug"]}.html">{esc(i["title"])}</a></td>'
                   f'<td>{lot_label(top_row) + ", " + esc(result(top_row)) if top_row else ""}</td>'
                   f'<td class="num">{money(total, "USD") if total else ""}</td></tr>')
    arch = ('<header class="issue-head"><p class="label">Archive</p><h1 class="display">Issues</h1></header>'
            '<div class="scroll"><table class="index"><thead><tr><th>No.</th><th>Date</th><th>Issue</th>'
            f'<th>Top sale</th><th class="num">Tracked value</th></tr></thead><tbody>{"".join(trs)}</tbody></table></div>')
    (OUT / "archive.html").write_text(page("Issues", arch, "Issues", "Every issue of Art Moves."))

    # data
    data = (f'<header class="issue-head"><p class="label">{len(rows)} sales tracked</p><h1 class="display">Data</h1>'
            '<p class="standfirst">Every sale Art Moves has covered, one row per sale. Select a column heading to sort. '
            'Download as <a href="sales.csv">CSV</a> or <a href="sales.json">JSON</a>.</p></header>' + sales_table(rows, sortable=True))
    (OUT / "data.html").write_text(page("Data", data, "Data", "The Art Moves sales dataset.", SORT_JS))
    (OUT / "sales.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n")
    cols = [c for c in S.REQUIRED + S.OPTIONAL if c not in ("sources", "image")] + ["source_urls"]
    buf = io.StringIO(); w = csv.DictWriter(buf, cols, extrasaction="ignore"); w.writeheader()
    for r in rows: w.writerow({**r, "source_urls": " | ".join(s["url"] for s in r["sources"])})
    (OUT / "sales.csv").write_text(buf.getvalue())

    # method
    _, about = read_md(SRC / "pages" / "about.md")
    body = '<header class="issue-head"><p class="label">How it is made</p><h1 class="display">Method</h1></header>' + markdown(about)
    (OUT / "about.html").write_text(page("Method", body, "Method", "How Art Moves is sourced and made."))
    print(f"build: {len(issues)} issue(s), {len(rows)} row(s) -> {OUT}")

if __name__ == "__main__":
    main()
