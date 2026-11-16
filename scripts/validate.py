#!/usr/bin/env python3
"""Check sales.json before anything is built or published.

Run: python3 scripts/validate.py [--check-links]
Exits 1 if any row fails. The weekly automation must not open a normal PR on failure.
"""
import datetime, json, pathlib, re, sys, urllib.request
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import schema as S

DATA = pathlib.Path(__file__).resolve().parents[1] / "src" / "data" / "sales.json"

def is_date(v):
    try:
        datetime.date.fromisoformat(v); return True
    except Exception:
        return False

def local_price(r):
    return r.get("price_with_premium") if r.get("price_basis") == "with_premium" else r.get("price_hammer")

def expected_vs(r):
    lo, hi = r.get("estimate_low"), r.get("estimate_high")
    if lo is None or hi is None:
        return "no_estimate"
    p = r.get("price_hammer") or local_price(r)
    return "below" if p < lo else "above" if p > hi else "within"

def check_row(r, seen):
    e = []
    for k in S.REQUIRED:
        if r.get(k) in (None, "", []):
            e.append(f"missing {k}")
    for k in r:
        if k not in S.REQUIRED and k not in S.OPTIONAL:
            e.append(f"unknown field {k}")
    if e:
        return e
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}-[a-z0-9-]+", r["id"]): e.append("id format")
    if r["id"] in seen: e.append("duplicate id")
    seen.add(r["id"])
    for k in ("sale_date", "fx_date"):
        if not is_date(r[k]): e.append(f"{k} is not a date")
    for k, allowed in (("house", S.HOUSES), ("category", S.CATEGORIES), ("price_basis", S.PRICE_BASIS),
                       ("vs_estimate", S.VS_ESTIMATE), ("guarantee", S.GUARANTEE),
                       ("buyer_status", S.BUYER_STATUS), ("price_source", S.PRICE_SOURCE),
                       ("confidence", S.CONFIDENCE)):
        if r[k] not in allowed: e.append(f"{k}={r[k]!r} not allowed")
    p = local_price(r)
    if not isinstance(p, (int, float)) or p <= 0:
        e.append("no price for the stated price_basis")
    else:
        usd = p * r["fx_rate_to_usd"]
        if abs(usd - r["price_usd"]) / usd > 0.005: e.append(f"price_usd off: expected about {round(usd)}")
        if r["vs_estimate"] != expected_vs(r): e.append(f"vs_estimate should be {expected_vs(r)}")
    if r["guarantee"] == "unknown" and "guarantee" in (r.get("financing_notes") or "").lower():
        e.append("financing_notes mentions a guarantee but guarantee is unknown; use guaranteed, house, third_party or none")
    if r["buyer_status"] == "anonymous" and r.get("buyer_name"): e.append("anonymous row has buyer_name")
    if r["buyer_status"] != "anonymous" and not (r.get("buyer_name") and r.get("buyer_attribution")):
        e.append("named/reported buyer needs buyer_name and buyer_attribution")
    if r.get("buyer_profile_url") and not str(r["buyer_profile_url"]).startswith("https://"): e.append("buyer_profile_url must be https")
    if r["buyer_status"] != "anonymous" and not r.get("buyer_profile_url"):
        print(f"WARN {r['id']}: named buyer has no buyer_profile_url")
    if len(r["why_it_matters"].split()) > 60: e.append("why_it_matters over 60 words")
    for s in r["sources"]:
        if not str(s.get("url", "")).startswith("https://"): e.append("source url must be https")
        if not s.get("publisher"): e.append("source missing publisher")
        if s.get("type") not in S.SOURCE_TYPE: e.append("source type")
    img = r.get("image")
    if img:
        for k in ("file", "credit", "license", "source_url"):
            if not img.get(k): e.append(f"image missing {k}")
        if img.get("file") and not (DATA.parents[1] / "assets" / "img" / img["file"]).exists(): e.append("image file not found")
        if img.get("kind", "photo") not in ("photo", "illustration"): e.append("image kind must be photo or illustration")
        if img.get("kind") == "illustration" and "AI-generated" not in img.get("credit", ""): e.append("illustration credit must say AI-generated")
        if "sothebys.com" in str(img.get("source_url", "")): e.append("image source must not be sothebys.com")
    prev = ""
    for h in r.get("history") or []:
        for k in h:
            if k not in S.HISTORY_FIELDS: e.append(f"history: unknown field {k}")
        d = str(h.get("date", ""))
        if not re.fullmatch(r"\d{4}(-\d{2}(-\d{2})?)?", d): e.append(f"history: bad date {d!r}")
        if d < prev: e.append("history: not in date order")
        if d >= r["sale_date"]: e.append("history: entry on or after the sale date")
        prev = d
        if h.get("event") not in S.HISTORY_EVENTS: e.append(f"history: event {h.get('event')!r}")
        if h.get("basis") not in S.HISTORY_BASIS: e.append(f"history: basis {h.get('basis')!r}")
        if h.get("price") is not None and not h.get("currency"): e.append("history: price without currency")
        if h.get("price_usd") is not None and h.get("price") is None: e.append("history: price_usd without price")
        if not str(h.get("source_url", "")).startswith("https://") or not h.get("publisher"): e.append("history: needs https source_url and publisher")
    if r["price_source"] == "house" and not any(s.get("type") == "primary" for s in r["sources"]):
        e.append("price_source=house but no primary source")
    return e

def link_ok(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (art-moves link check)"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status < 400
    except Exception:
        return False

def main():
    rows = json.loads(DATA.read_text())
    seen, bad = set(), 0
    for r in rows:
        errs = check_row(r, seen)
        if "--check-links" in sys.argv:
            # Some house sites refuse scripts; a failed fetch is a warning, not an error.
            for s in r.get("sources", []):
                if not link_ok(s["url"]): print(f"WARN {r.get('id')}: could not fetch {s['url']}")
        if errs:
            bad += 1
            print(f"FAIL {r.get('id', '?')}: " + "; ".join(errs))
    print(f"validate: {len(rows)} row(s), {bad} failing")
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
