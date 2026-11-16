#!/usr/bin/env python3
"""Draft the Sunday email for one issue.

Inputs:  src/issues/NNN.md (front matter), src/data/sales.json, src/config.json
Outputs: email/NNN.html and email/NNN.txt. Not part of site/, so nothing here is published.

The format follows a daily editor's note: the headline is the subject line, a "Plus"
line names two more things inside, and the body is five short numbered sections.
The script only drafts. The editor reads, edits and sends.

Optional front matter on the issue, each on one line:
  email_plus         two more things in the email, after the word "Plus,"
  email_desk         the editor's note; the first sentence is set in bold
  email_number       the figure of the week
  email_number_line  what the figure means
  email_sales        three sale ids, comma separated (default: the first three featured in the issue)
  email_term         one term
  email_term_line    its plain-English meaning
Anything missing falls back to the issue's top line and the data.

Standard library only.
Run: python3 scripts/newsletter.py [issue number]
"""
import html, json, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import schema as S
from build import SRC, ROOT, TAGLINE, day, local_price, money, read_md, result

OUT = ROOT / "email"
esc = html.escape
WPM = 230  # reading speed used for the read-time line

def sentences(text):
    """Split on sentence ends, leaving initials such as F.P. alone."""
    return [s for s in re.split(r"(?<![A-Z]\.)(?<=[.!?])\s+(?=[A-Z0-9\"'])", text.strip()) if s]

def load(number=None):
    rows = json.loads((SRC / "data" / "sales.json").read_text())
    cfg = json.loads((SRC / "config.json").read_text())
    files = sorted((SRC / "issues").glob("*.md"))
    f = SRC / "issues" / f"{int(number):03d}.md" if number else files[-1]
    meta, text = read_md(f)
    meta["number"] = int(meta["number"]); meta["slug"] = f"{meta['number']:03d}"
    mine = [r for r in rows if r["issue"] == meta["number"]]
    by_id = {r["id"]: r for r in mine}
    featured = [i for i in re.findall(r"\{\{sale:([^}]+)\}\}", text) if i.strip() in by_id]
    ids = [i.strip() for i in meta.get("email_sales", "").split(",") if i.strip()] or featured[:3]
    missing = [i for i in ids if i not in by_id]
    if missing: raise SystemExit(f"email_sales: no such sale in issue {meta['slug']}: {', '.join(missing)}")
    return meta, mine, [by_id[i] for i in ids], cfg

def content(meta, rows, picks, cfg):
    """One structure, rendered twice (HTML and plain text) so the two never drift."""
    url = f"{cfg['site_url'].rstrip('/')}/{meta['slug']}.html"
    top = max(rows, key=lambda r: r["price_usd"])
    desk = sentences(meta.get("email_desk") or meta.get("topline", ""))
    named = [r for r in rows if r["buyer_status"] != "anonymous"]
    sections = [("From the editor's desk", [("lead", desk[0] if desk else "", " ".join(desk[1:]))])]
    sections.append(("The number", [("lead", (meta.get("email_number") or result(top)).rstrip(".") + ".",
                     meta.get("email_number_line") or f"The top price in this issue: {top['maker']}, {top['title']}, at {S.HOUSES[top['house']]} {top['location']}.")]))
    sections.append((f"{['No', 'One', 'Two', 'Three', 'Four', 'Five'][min(len(picks), 5)]} sale{'s' if len(picks) != 1 else ''}",
                     [("sale", f"{r['maker']}, {r['title']}", result(r), f"{S.HOUSES[r['house']]} {r['location']}, {day(r['sale_date'])}",
                       sentences(r["why_it_matters"])[0], f"{url}#{r['id']}") for r in picks]))
    words = ["None", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
    count = words[len(named)] if len(named) < 10 else str(len(named))
    who = [("text", f"{count} of {len(rows)} buyers {'is' if len(named) == 1 else 'are'} on the record." if named else f"None of the {len(rows)} buyers has been named by a credible outlet.")]
    for r in named:
        note = r["buyer_attribution"].strip().rstrip(".")
        who.append(("buyer", r["buyer_name"], r.get("buyer_profile_url"), f"{r['maker']}, {r['title']}, {result(r)}", note[0].upper() + note[1:] + "."))
    if named and len(named) < len(rows):
        who.append(("text", f"The other {len(rows) - len(named)} are anonymous. Art Moves does not print guesses about private people."))
    sections.append(("Who bought", who))
    if meta.get("email_term"):
        sections.append(("One term", [("lead", meta["email_term"] + ".", meta.get("email_term_line", ""))]))
    return {"subject": meta["title"], "plus": meta.get("email_plus", ""), "sections": sections, "url": url,
            "meta": f"Issue {meta['number']:02d} · {day(meta['date'])} · Covers {meta['window']}",
            "about": [f"Art Moves. {TAGLINE} Every Sunday.",
                      "Reply to this email and tell me what was useful and what was not. I read every reply.",
                      "The editor works part-time with a commercial art gallery. Art Moves has no advertisers or sponsors, and nothing here is investment advice.",
                      cfg["email"].get("unsubscribe", ""), cfg["email"].get("postal_address", "")]}

# ---------- plain text ----------

def as_text(c):
    out = [c["subject"], ""]
    if c["plus"]: out += [f"Plus, {c['plus']}.", ""]
    out += [c["meta"], ""]
    for n, (title, items) in enumerate(c["sections"], 1):
        out += [f"{n}. {title.upper()}", ""]
        for it in items:
            if it[0] == "lead": out += [" ".join(x for x in it[1:] if x), ""]
            elif it[0] == "text": out += [it[1], ""]
            elif it[0] == "sale": out += [f"- {it[1]}. {it[2]}. {it[3]}.", f"  {it[4]}", f"  {it[5]}", ""]
            elif it[0] == "buyer": out += [f"- {it[1]}: {it[3]}. {it[4]}", ""]
    out += ["READ THE FULL ISSUE", "", "Every sale, every source, and what the numbers mean:", c["url"], "", "ABOUT ART MOVES", ""]
    out += [a + "\n" for a in c["about"] if a]
    return "\n".join(out).rstrip() + "\n"

# ---------- HTML ----------

SANS = "font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Helvetica,Arial,sans-serif"
SERIF = "font-family:Georgia,'Iowan Old Style','Times New Roman',serif"
P = f"margin:0 0 14px;{SANS};font-size:16px;line-height:1.55;color:#111111"
LABEL = f"margin:0 0 12px;{SANS};font-size:12px;line-height:1.4;font-weight:bold;letter-spacing:1px;text-transform:uppercase;color:#111111"
DIM = f"{SANS};font-size:13px;line-height:1.5;color:#6a6a6a"
LINK = "color:#111111;text-decoration:underline"

def as_html(c):
    b = []
    for n, (title, items) in enumerate(c["sections"], 1):
        b.append(f'<tr><td style="padding:22px 0 10px;border-top:1px solid #111111"><p style="{LABEL}">{n}. {esc(title)}</p>')
        for it in items:
            if it[0] == "lead":
                b.append(f'<p style="{P}"><strong>{esc(it[1])}</strong> {esc(it[2])}</p>')
            elif it[0] == "text":
                b.append(f'<p style="{P}">{esc(it[1])}</p>')
            elif it[0] == "sale":
                b.append(f'<p style="{P}"><a href="{esc(it[5])}" style="{LINK};font-weight:bold">{esc(it[1])}</a><br>'
                         f'<strong>{esc(it[2])}</strong> <span style="color:#6a6a6a">· {esc(it[3])}</span><br>{esc(it[4])}</p>')
            elif it[0] == "buyer":
                name = f'<a href="{esc(it[2])}" style="{LINK}">{esc(it[1])}</a>' if it[2] else esc(it[1])
                b.append(f'<p style="{P}"><strong>{name}</strong>: {esc(it[3])}. {esc(it[4])}</p>')
        b.append("</td></tr>")
    plus = f'<p style="margin:0 0 18px;{SANS};font-size:18px;line-height:1.45;color:#111111">Plus, {esc(c["plus"])}.</p>' if c["plus"] else ""
    about = "".join(f'<p style="margin:0 0 10px;{DIM}">{esc(a)}</p>' for a in c["about"] if a)
    return (f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{esc(c["subject"])}</title></head><body style="margin:0;padding:0;background:#ffffff">'
            f'<div style="display:none;max-height:0;overflow:hidden;opacity:0">{esc("Plus, " + c["plus"] + "." if c["plus"] else c["meta"])}</div>'
            '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#ffffff"><tr><td align="center" style="padding:0 20px">'
            '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;text-align:left">'
            f'<tr><td style="padding:28px 0 20px"><p style="margin:0;{SANS};font-size:22px;font-weight:500;color:#111111">Art Moves</p></td></tr>'
            f'<tr><td style="padding:22px 0 14px;border-top:1px solid #111111"><p style="margin:0 0 16px;{DIM};font-size:12px;letter-spacing:1px;text-transform:uppercase">{esc(c["meta"])}</p>'
            f'<h1 style="margin:0 0 14px;{SERIF};font-size:34px;line-height:1.1;font-weight:normal;color:#111111">{esc(c["subject"])}</h1>{plus}</td></tr>'
            + "".join(b) +
            f'<tr><td style="padding:22px 0 28px;border-top:1px solid #111111"><p style="{LABEL}">Read the full issue</p>'
            f'<p style="{P}">Every sale, every source, and what the numbers mean.</p>'
            f'<p style="margin:0"><a href="{esc(c["url"])}" style="display:inline-block;background:#111111;color:#ffffff;{SANS};font-size:16px;font-weight:500;text-decoration:none;padding:13px 22px">Open issue {esc(c["url"].rsplit("/", 1)[1].split(".")[0])}</a></p></td></tr>'
            f'<tr><td style="padding:18px 0 36px;border-top:1px solid #111111"><p style="{LABEL};color:#6a6a6a">About Art Moves</p>{about}</td></tr>'
            '</table></td></tr></table></body></html>\n')

def main():
    meta, rows, picks, cfg = load(sys.argv[1] if len(sys.argv) > 1 else None)
    c = content(meta, rows, picks, cfg)
    OUT.mkdir(exist_ok=True)
    text = as_text(c)
    (OUT / f"{meta['slug']}.txt").write_text(text)
    (OUT / f"{meta['slug']}.html").write_text(as_html(c))
    words = len(text.split())
    print(f"newsletter: issue {meta['slug']} -> {OUT}")
    print(f"subject: {c['subject']}")
    print(f"length: {words} words, about {max(1, round(words / WPM))} minute(s) to read")
    for k in ("email_plus", "email_desk", "email_number", "email_term"):
        if not meta.get(k): print(f"WARN no {k} in the issue front matter; using the fallback")
    if not cfg["email"].get("postal_address"): print("NOTE no postal address in src/config.json; one is required before sending to a list")
    if words > 3 * WPM: print("WARN over a three-minute read; cut something")

if __name__ == "__main__":
    main()
