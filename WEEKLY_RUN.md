# Weekly run

A copy of the instructions saved in the Perplexity Computer automation "Art Moves weekly issue draft", as of 11 Nov 2026. The automation runs on Sundays at 9:00 AM Eastern, in a fresh session, and opens a pull request. It cannot merge.

The saved automation is what runs. Editing this file does not change the run; change the automation, then update this copy.

---

Draft the next weekly issue of Art Moves and open it as a pull request for the editor to review. Do not publish anything.

Art Moves is a free weekly brief on notable auction sales in art and luxury: who bought, what they paid, and what the sale says about how wealthy families protect and grow capital. The reader knows finance and is new to the art market. Repo: `ryanbwatt/art-moves` (private). Live site: https://art-moves.pages.dev/. Merging a pull request to `main` publishes the site, and only the editor merges.

## Hard rules

- Never push to `main`. Never merge a pull request. Work on a branch and open one pull request.
- Do not change the deploy workflow, hosting, DNS, repo settings, or any other repo. Do not email or message anyone.
- Every figure must come from a page you fetched in this run. If you cannot source a number, leave the sale out and list it under gaps.
- Keep the editor's name off the site and out of the issue.
- If cloning, pushing, or opening the pull request fails, stop and report what failed. Do not work around it through another route.

## 1. Set up

1. Clone the repo with `gh repo clone ryanbwatt/art-moves` and work from `main`.
2. Read `README.md`, `src/pages/about.md` (the published method), `scripts/schema.py`, the most recent file in `src/issues/`, and `src/data/sales.json`. Existing rows and the latest issue are the pattern to follow.
3. The new issue number N is the highest issue number on `main` plus one. Use branch `issue/NNN` (three digits).
4. If an earlier issue pull request is still open, do not stack on it. Build from `main`, cover everything since the last merged issue, name the branch `issue/NNN-YYYYMMDD`, and say in the pull request that it replaces the open one.

## 2. Window

The window runs from the day after the last merged issue's window ended (see `window` in that issue's front matter) through yesterday. Also pick up sales from the earlier window whose results were not out when that issue was drafted. Never add a sale that already has a row.

## 3. Collect

Cover Sotheby's, Christie's and Phillips in all categories, plus other houses (`house: other`) for cars or anything else with a notable result. Include a sale when its price with premium, in USD, meets the floor:

| Category | Include from | Usually featured from |
|---|---|---|
| Fine art | $1M | $10M, or a strong story |
| Watches | $500k | $1M |
| Jewelry | $1M | $5M |
| Cars | $1M | $5M |
| Design and furniture | $250k | $1M |
| Fashion, handbags, memorabilia | $100k | $500k |
| Story override | Any price | Named buyer, record, restitution, unusual guarantee |

Cap the week at about 40 rows, highest value first. Aim for at least one row outside fine art when one qualifies.

Sources, in order: the auction house's results page or press release, then established trade press (The Art Newspaper, Artnet, Apollo, ARTnews, Reuters, Hodinkee, Rapaport, WatchPro and similar). Known limits from earlier runs:

- Sotheby's pages do not show sold prices to a fetch. Use press, set `price_source: press`, and keep confidence at medium or lower.
- Phillips index pages return nothing; reach individual auction pages through search.
- Press sometimes reports a hammer price as the final price. Check every figure's basis against a second source before recording it.
- Where sources disagree, record the figure you can best support and state the disagreement in the row's notes.

## 4. Enrich each sale

Add one object per sale to `src/data/sales.json`, using the fields in `scripts/schema.py`.

- `id`: `YYYY-MM-DD-house-short-slug`. `issue`: N.
- Prices: record `price_hammer` and `price_with_premium` where known and set `price_basis` to the one the row reports. Keep the original currency. Leave the FX fields for the script.
- Estimate: low and high without fees, and `vs_estimate` comparing the hammer price to the range.
- `guarantee`: none, house, third_party, irrevocable_bid, or unknown. Buyer financing is rarely public, so track guarantees and irrevocable bids; use `financing_notes` only for something a source states.
- Buyer: set `buyer_status: reported` with `buyer_name`, `buyer_attribution` (the outlet) and `buyer_profile_url` only when a credible outlet names the buyer. The profile link must be an https page that explains who they are and how they made their money, and you must open it to confirm. Otherwise set `anonymous` and put what is on the record about the bidding in `bidding_notes`. A claim with one weak source stays out of the data and goes in the pull request notes. Never print a guess about a private person.
- `why_it_matters`: 60 words or fewer, plain English, for a finance reader.
- `sources`: every page used, with `url` (https), `publisher`, `type` (primary or press) and `accessed`.
- `image`: only a public-domain or openly licensed image, with `file`, `credit`, `license` and `source_url`. No auction-house photographs. No image is fine.

Then recheck the anonymous rows from the previous three issues for newly reported buyers. If one is now named, update the row and set `updated_at` and `update_note`.

## 5. Check and build

Run, in order: `python3 scripts/fx.py`, `python3 scripts/validate.py`, `python3 scripts/build.py`. Validation must pass. Confirm `site/NNN.html` exists and that `site/index.html` leads with the new issue.

## 6. Write the issue

Create `src/issues/NNN.md` with this front matter: `number`, `title`, `date` (today), `window` (for example `12 to 14 November 2026`), `status: draft`, `lead` (the id of the lead sale) and `topline` (two or three sentences).

Sections, as in the latest issue:

1. `## Top line`: what happened this week, in three short paragraphs at most.
2. `## Featured sales`: three to seven sales, each on its own line as `{{sale:ID}}`.
3. `## Who bought`: named buyers with attribution, then what is on the record about the unnamed ones.
4. `## Market signal`: one takeaway and one clearly marked opinion. Define any market term in a sentence.
5. `## Outside fine art`: watches, jewelry, cars, design, fashion, as available.
6. `## How to read these numbers`: a short primer for a newcomer. Do not repeat last week's terms.
7. `## All sales in this issue`: a single line, `{{table}}`.

Voice: opinionated, plain, short sentences. Link each factual claim inline to its source, as the latest issue does. Summarize in your own words; do not reproduce article text. No emojis. Do not use: delve, explore, seamless, game-changer, robust, leverage, testament, cutting-edge.

The page builder only understands paragraphs, `- ` lists, `**bold**`, links, `##` and `###` headings, and directives on their own line. Do not use tables, italics or nested lists in the issue file.

If fewer than three sales qualify, write a short quiet-week issue: one sale, one signal, and what is coming up next week.

Before committing, re-read the draft against the data. Every number in the prose must match a row or a linked source. Then rebuild.

## 7. Log the run

Append a dated entry to `BUILD_LOG.md` in the same pull request, in the format of the most recent entry: what ran, capabilities used, decisions, what worked, failures and workarounds, and elapsed time. Credit use cannot be measured from inside a run, so say to check the usage page.

## 8. Open the pull request

- Check the git author and committer identity before committing. End the commit message with the trailer `Co-authored-by: Perplexity <noreply@perplexity.ai>`.
- Commit `src/`, `site/` and `BUILD_LOG.md` on the branch, push it, and open a pull request titled `Issue N: <title>`.
- If validation fails and you cannot fix it, open the pull request as a draft titled `Needs attention: Issue N` and list the failing rows.
- Pull request body: a five-line summary; the window; row counts by category; named buyers and their sources; everything unverified or low confidence; gaps (sales with no readable result); and the three things most worth spot-checking. End with the line `<sub>Created with [Perplexity](<this run's thread URL>)</sub>`.

## 9. Report

Finish with a short message: the pull request link, the five-line summary, and the unverified list. If the run failed, say what failed and that nothing was published.
