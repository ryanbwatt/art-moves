#!/usr/bin/env python3
"""Fill fx_rate_to_usd and price_usd for rows that lack them.

Rates are ECB reference rates from the Frankfurter API, taken on the sale date
(or the last business day before it). fx_rate_to_usd is USD per one unit of the
sale currency. Run: python3 scripts/fx.py
"""
import json, pathlib, urllib.request

DATA = pathlib.Path(__file__).resolve().parents[1] / "src" / "data" / "sales.json"

def rate(currency, date):
    if currency == "USD":
        return 1.0, date
    url = f"https://api.frankfurter.dev/v1/{date}?base={currency}&symbols=USD"
    req = urllib.request.Request(url, headers={"User-Agent": "art-moves"})
    with urllib.request.urlopen(req, timeout=20) as r:
        d = json.load(r)
    return d["rates"]["USD"], d["date"]

def main():
    rows = json.loads(DATA.read_text())
    changed = 0
    for r in rows:
        if r.get("fx_rate_to_usd") and r.get("price_usd"):
            continue
        fx, fx_date = rate(r["currency"], r["sale_date"])
        local = r.get("price_with_premium") if r["price_basis"] == "with_premium" else r.get("price_hammer")
        r["fx_rate_to_usd"], r["fx_date"], r["fx_source"] = round(fx, 5), fx_date, "ECB reference rate via Frankfurter"
        r["price_usd"] = round(local * fx)
        changed += 1
    DATA.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n")
    print(f"fx: filled {changed} row(s)")

if __name__ == "__main__":
    main()
