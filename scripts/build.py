#!/usr/bin/env python3
"""Render Art Moves from data and Markdown into static HTML.

Inputs:  src/data/sales.json, src/issues/NNN.md, src/pages/about.md, src/assets/, src/config.json
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

def buyer_html(r, short=False):
    """Buyer name, linked in a new tab to a profile that explains who they are and where the money comes from."""
    if r["buyer_status"] == "anonymous": return "Anonymous"
    name = esc(r["buyer_name"])
    if r.get("buyer_profile_url"):
        name = f'<a href="{esc(r["buyer_profile_url"])}" target="_blank" rel="noopener">{name}</a>'
    return name if short else f'{name} ({esc(r["buyer_attribution"])})'

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

# ---------- price history ----------

RETURNS_PAPER = "https://academic.oup.com/rfs/article-abstract/29/4/1007/1896045"

def year_of(d):
    """'2015-05-12', '1927-11' or '1972' as a fractional year."""
    p = [int(x) for x in str(d).split("-")]
    return p[0] + ((p[1] - 1) / 12 if len(p) > 1 else 0.5) + ((p[2] - 1) / 365 if len(p) > 2 else 0)

def when(d):
    p = str(d).split("-")
    if len(p) == 3: return day(d)
    if len(p) == 2: return f"{datetime.date(int(p[0]), int(p[1]), 1):%b %Y}"
    return p[0]

def history_events(r):
    """Every documented change of hands, oldest first, ending with this sale."""
    now = {"date": r["sale_date"], "event": "auction", "venue": f"{S.HOUSES[r['house']]} {r['location']}" + (f", lot {r['lot_number']}" if r.get("lot_number") else ""),
           "currency": r["currency"], "price": local_price(r), "price_usd": r["price_usd"], "basis": r["price_basis"], "current": True}
    return list(r.get("history") or []) + [now]

def returns(r):
    """Change since the last earlier sale with a dollar price: (event, multiple, years, annualized)."""
    priced = [h for h in r.get("history") or [] if h.get("price_usd") and h["event"] in ("auction", "private_sale")]
    if not priced: return None
    last = priced[-1]
    yrs = year_of(r["sale_date"]) - year_of(last["date"])
    mult = r["price_usd"] / last["price_usd"]
    return last, mult, yrs, (mult ** (1 / yrs) - 1 if yrs >= 1 else None)

def pct(x, sign=True):
    return (f"{x:+.1%}" if sign else f"{x:.1%}").replace("-", "−")

def chart(r):
    """Inline SVG: documented prices as points on a time axis. Dashed lines join them because
    nothing traded in between. Undisclosed changes of hands are ticks on the axis."""
    ev = history_events(r)
    pts = [h for h in ev if h.get("price_usd")]
    if len(pts) < 2: return ""
    W, H, L, R_, T, B = 640, 220, 64, 16, 16, 30
    x0 = min(year_of(h["date"]) for h in ev); x1 = year_of(r["sale_date"])
    x0 = min(x0, x1 - 5); span = x1 - x0
    top = max(h["price_usd"] for h in pts)
    mag = 10 ** (len(str(int(top))) - 1)
    step_v = next(s * mag for s in (0.25, 0.5, 1, 2, 2.5, 5) if top / (s * mag) <= 4)
    ymax = (int(top // step_v) + 1) * step_v
    X = lambda y: L + (year_of(y) - x0) / span * (W - L - R_)
    Y = lambda v: T + (1 - v / ymax) * (H - T - B)
    out = [f'<svg class="ticker-chart" viewBox="0 0 {W} {H}" role="img" aria-label="Documented sale prices for {esc(r["title"])}, in US dollars">']
    for i in range(int(round(ymax / step_v)) + 1):
        v = i * step_v
        out.append(f'<line class="grid" x1="{L}" x2="{W-R_}" y1="{Y(v):.1f}" y2="{Y(v):.1f}"/><text class="axis" x="{L-8}" y="{Y(v)+4:.1f}" text-anchor="end">{money(v, "USD") if v else "$0"}</text>')
    step = 10 if span > 25 else 5 if span > 10 else 2
    for yr in range(int(x0) // step * step + step, int(x1) + 1, step):
        out.append(f'<text class="axis" x="{X(str(yr)) - (W-L-R_)/span*0.5:.1f}" y="{H-8}" text-anchor="middle">{yr}</text>')
    line = " ".join(f'{X(h["date"]):.1f},{Y(h["price_usd"]):.1f}' for h in pts)
    out.append(f'<polyline class="link" points="{line}"/>')
    for h in ev:
        if not h.get("price_usd"):
            out.append(f'<line class="tick" x1="{X(h["date"]):.1f}" x2="{X(h["date"]):.1f}" y1="{Y(0)-7:.1f}" y2="{Y(0)+7:.1f}"><title>{esc(when(h["date"]))}: {esc(S.HISTORY_EVENTS[h["event"]].lower())}, price not disclosed</title></line>')
    for h in pts:
        local = money(h["price"], h["currency"]) + ("" if h["currency"] == "USD" else f' ({money(h["price_usd"], "USD")})')
        out.append(f'<circle class="pt{" now" if h.get("current") else ""}" cx="{X(h["date"]):.1f}" cy="{Y(h["price_usd"]):.1f}" r="6" tabindex="0" '
                   f'data-price="{esc(money(h["price_usd"], "USD"))}" data-when="{esc(when(h["date"]))}" data-where="{esc(h["venue"])}" '
                   f'aria-label="{esc(when(h["date"]))}, {esc(h["venue"])}: {esc(local)}"><title>{esc(when(h["date"]))}, {esc(h["venue"])}: {esc(local)}</title></circle>')
    out.append("</svg>")
    return "".join(out)

def ticker(r, heading=False):
    """Google Finance-style panel for one object: the price, what it did since the last
    documented sale, a chart, key statistics and the full record of changes of hands."""
    ret = returns(r)
    first_public = not any(h["event"] == "auction" for h in r.get("history") or [])
    if ret:
        last, mult, yrs, ann = ret
        change = (f'<span class="chg">{"+" if mult >= 1 else "−"}{money(abs(r["price_usd"] - last["price_usd"]), "USD")} ({pct(mult - 1)})</span> '
                  f'<span class="dim">since {esc(when(last["date"]))}</span>')
    else:
        change = '<span class="dim">' + ("First time at public auction. No earlier public price in dollars." if first_public else "No earlier price in comparable dollars.") + '</span>'
    stats = [("Price", money(r["price_usd"], "USD") + f' <span class="dim">{S.PRICE_BASIS[r["price_basis"]]}</span>'),
             ("Last documented sale", f'{money(ret[0]["price_usd"], "USD")} <span class="dim">{esc(when(ret[0]["date"]))}</span>' if ret
              else next((f'{money(h["price"], h["currency"])} <span class="dim">{esc(when(h["date"]))}</span>' for h in reversed(r.get("history") or [])
                         if h.get("price") and h["event"] in ("auction", "private_sale")), "None public")),
             ("Held", f"{ret[2]:.1f} years" if ret else "—"),
             ("Multiple", f"{ret[1]:.2f}×" if ret else "—"),
             ("Annualized", pct(ret[3]) if ret and ret[3] is not None else "—"),
             ("Versus estimate", {"below": "Below", "within": "Within", "above": "Above", "no_estimate": "No range"}[r["vs_estimate"]]),
             ("Guarantee", esc(S.GUARANTEE[r["guarantee"]])),
             ("Changes of hands on record", str(len(history_events(r))))]
    dl = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in stats)
    li = []
    for h in reversed(history_events(r)):
        price = (money(h["price"], h["currency"]) + ("" if h["currency"] == "USD" or not h.get("price_usd") else f' ({money(h["price_usd"], "USD")})')
                 + f' <span class="dim">{S.HISTORY_BASIS.get(h["basis"], S.PRICE_BASIS.get(h["basis"], ""))}</span>') if h.get("price") else '<span class="dim">Price not disclosed</span>'
        src = "" if h.get("current") else f' · <a class="dim" href="{esc(h["source_url"])}" target="_blank" rel="noopener">{esc(h["publisher"])}</a>'
        note = f'<br><span class="dim">{esc(h["note"])}</span>' if h.get("note") else ""
        li.append(f'<li><span class="tl-when">{esc(when(h["date"]))}</span><span class="tl-what">{esc(S.HISTORY_EVENTS[h["event"]])}{" (this sale)" if h.get("current") else ""} · {esc(h["venue"])}<br>{price}{src}{note}</span></li>')
    head = f'<h3 class="sale-title">{lot_label(r)}</h3>' if heading else ""
    return (f'<section class="ticker" aria-label="Price history">{head}<p class="label">Price history</p>'
            f'<p class="quote"><span class="q-price" data-default="{esc(money(r["price_usd"], "USD"))}">{esc(money(r["price_usd"], "USD"))}</span> '
            f'<span class="q-note" data-default="{esc(change)}">{change}</span></p>'
            f'{chart(r)}<dl class="stats">{dl}</dl><ol class="timeline">{"".join(li)}</ol>'
            f'<p class="dim small">Nominal US dollars as reported at the time, before the seller\'s commission, insurance, storage and tax. '
            f'Only works that come back to market get a second price, which flatters returns '
            f'(<a href="{RETURNS_PAPER}" target="_blank" rel="noopener">Korteweg, Kräussl and Verwijmeren, 2016</a>). Not investment advice.</p></section>')

TICKER_JS = """<script>document.querySelectorAll('.ticker').forEach(function(t){var p=t.querySelector('.q-price'),n=t.querySelector('.q-note');function show(c){p.textContent=c.dataset.price;n.innerHTML='';var s=document.createElement('span');s.className='dim';s.textContent=c.dataset.when+' · '+c.dataset.where;n.appendChild(s)}function reset(){p.textContent=p.dataset.default;n.innerHTML=n.dataset.default}t.querySelectorAll('.pt').forEach(function(c){c.addEventListener('mouseenter',function(){show(c)});c.addEventListener('focus',function(){show(c)});c.addEventListener('mouseleave',reset);c.addEventListener('blur',reset)})});</script>"""

def sale_block(r, order):
    facts = [("Price", ("Includes buyer's premium. " if r["price_basis"] == "with_premium" else "Hammer price, before fees. ") + evidence(r)),
             ("Estimate", estimate(r)),
             ("Sale", f"{S.HOUSES[r['house']]} {r['location']}, {day(r['sale_date'])}" + (f", lot {r['lot_number']}" if r.get("lot_number") else "")),
             ("Seller", r.get("seller") or "Not disclosed"),
             ("Buyer", buyer(r)),
             ("Guarantee", S.GUARANTEE[r["guarantee"]])]
    for k, label in (("record", "Record"), ("bidding_notes", "Bidding"), ("financing_notes", "Financing"), ("update_note", "Updated")):
        if r.get(k): facts.append((label, r[k]))
    dl = "".join(f"<div><dt>{esc(k)}</dt><dd>{buyer_html(r) if k == 'Buyer' else esc(v)}</dd></div>" for k, v in facts)
    return (f'<article class="sale" id="{esc(r["id"])}">{figure(r)}'
            f'<p class="kicker">{esc(S.CATEGORIES[r["category"]])} · {esc(S.HOUSES[r["house"]])} {esc(r["location"])}</p>'
            f'<h3 class="sale-title">{lot_label(r)}</h3><p class="figure-price">{esc(result(r))}</p><dl class="facts">{dl}</dl>'
            f'<p class="why"><strong>Why it matters.</strong> {esc(r["why_it_matters"])} {cites(r, order)}</p>'
            f'{ticker(r) if r.get("history") else ""}</article>')

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
            f'<td>{esc(estimate(r, True))}</td><td>{buyer_html(r, True)}</td><td>{src}</td></tr>')
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
                   f'<span class="dim">{esc(S.HOUSES[r["house"]])} {esc(r["location"])} · {day(r["sale_date"])} · Buyer: {buyer_html(r, True)}</span></span>'
                   f'<span class="row-price">{esc(result(r))}</span></a>')
    return f'<div class="rows">{"".join(out)}</div>'

def source_list(order):
    if not order: return ""
    li = "".join(f'<li id="s{n}"><a href="{esc(u)}">{esc(p)}</a></li>' for u, (n, p) in order.items())
    return f'<section class="sec"><h2 class="label">Sources</h2><div class="sec-body"><ol class="sources">{li}</ol></div></section>'

def subscribe(cfg, place):
    """Sign-up form for the Sunday email. A plain HTML form that posts to whichever
    email service is named in src/config.json. Renders nothing until an action is set."""
    sub = cfg.get("subscribe") or {}
    if not sub.get("action"): return ""
    hidden = "".join(f'<input type="hidden" name="{esc(k)}" value="{esc(str(v))}">' for k, v in (sub.get("hidden") or {}).items())
    return (f'<section class="sec" id="subscribe-{place}"><h2 class="label">Sunday email</h2><div class="sec-body">'
            '<p class="standfirst">The week\'s biggest sales in art, watches and cars, in three minutes. One email, every Sunday. Free.</p>'
            f'<form class="signup" action="{esc(sub["action"])}" method="{esc(sub.get("method", "post"))}" target="_blank" rel="noopener">{hidden}'
            f'<label for="email-{place}">Email address</label>'
            f'<div class="signup-row"><input id="email-{place}" type="email" name="{esc(sub.get("email_field", "email"))}" autocomplete="email" placeholder="you@example.com" required>'
            '<button type="submit">Subscribe</button></div>'
            '<p class="dim small">You will get one email asking you to confirm. Your address is used for this email and nothing else. Unsubscribe any time.</p></form></div></section>')

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

QUESTIONS = ('<section class="sec"><h2 class="label">Every issue asks</h2><div class="sec-body wide"><ol class="questions">'
             '<li><strong>Who paid what?</strong><span>The price with and without fees, the estimate, any guarantee, and the buyer when it is on the record.</span></li>'
             '<li><strong>What did it fetch last time?</strong><span>Earlier documented sales of the same object, and what the change works out to a year. <a href="data.html">Price history</a></span></li>'
             '<li><strong>Why would a careful person buy art?</strong><span>What a sale says to a reader who knows finance and is weighing a first purchase.</span></li>'
             '</ol></div></section>')

# ---------- pages ----------

def main():
    rows = json.loads((SRC / "data" / "sales.json").read_text())
    by_id = {r["id"]: r for r in rows}
    cfg = json.loads((SRC / "config.json").read_text())
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
    # Tells Cloudflare Pages which requests skip the visit-logging function.
    shutil.copy(SRC / "assets" / "_routes.json", OUT / "_routes.json")

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
                f'\n{markdown(it["text"], directive)}\n{subscribe(cfg, "issue")}{source_list(order)}<nav class="pager" aria-label="Issues">{pager}</nav>')
        js = TICKER_JS if 'class="ticker"' in body else ""
        (OUT / f"{it['slug']}.html").write_text(page(it["title"], body, description=it.get("topline", ""), script=js))

    # home
    if issues:
        top = issues[0]; href = f'{top["slug"]}.html'
        hero = figure(top["lead_row"], "plate hero") if top.get("lead_row") else ""
        home = (f'{banner(top)}{hero}<section class="lead"><p class="label">{issue_meta(top)}</p>'
                f'<div><h1 class="display"><a href="{href}">{esc(top["title"])}</a></h1>'
                f'<p class="standfirst">{esc(top.get("topline", ""))}</p><p><a class="more" href="{href}">Read the issue</a></p></div></section>{QUESTIONS}{subscribe(cfg, "home")}'
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
            'Download as <a href="sales.csv">CSV</a> or <a href="sales.json">JSON</a>.</p></header>')
    hist = sorted((r for r in rows if r.get("history")), key=lambda r: (returns(r) is None, -r["price_usd"]))
    if hist:
        data += ('<section class="sec"><h2 class="label">Price history</h2><div class="sec-body wide">'
                 '<p class="standfirst">What the same object fetched the last time it changed hands, where that is on the record. '
                 'Hover or tab to a point for the sale behind it.</p>'
                 + "".join(ticker(r, heading=True) for r in hist) + '</div></section>')
    data += '<section class="sec"><h2 class="label">Every sale</h2><div class="sec-body wide">' + sales_table(rows, sortable=True) + '</div></section>'
    (OUT / "data.html").write_text(page("Data", data, "Data", "The Art Moves sales dataset.", SORT_JS + TICKER_JS))
    (OUT / "sales.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n")
    cols = [c for c in S.REQUIRED + S.OPTIONAL if c not in ("sources", "image", "history")] + ["source_urls"]
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
