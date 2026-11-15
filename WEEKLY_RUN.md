# Weekly run

A copy of the instructions saved in the Perplexity Computer automation "Art Moves weekly issue", as of 15 Nov 2026. The automation runs on Sundays at 9:00 AM Eastern, in a fresh session. It opens a pull request for the new issue and merges it itself when the checks in step 9 pass, which publishes the issue. It does not send the email.

The saved automation is what runs. Editing this file does not change the run; change the automation, then update this copy.

---

Draft the next weekly issue of Art Moves, open it as a pull request, and merge it to publish the issue when every check in step 9 passes. Do not send the email.

Art Moves is a free weekly brief on notable auction sales in art and luxury: who bought, what they paid, and what the sale says about how wealthy families protect and grow capital. The reader knows finance and is new to the art market. Repo: `ryanbwatt/art-moves` (public). Live site: https://art-moves.pages.dev/. Merging a pull request to `main` publishes the site. The editor has authorized this run to merge its own issue pull request each Sunday, under the conditions in step 9. The editor reads the published issue afterwards and asks for corrections.

## Hard rules

- Never push to `main`. Work on a branch and open one pull request. The only pull request you may merge is this run's own issue pull request, and only under step 9. Never merge any other pull request.
- Do not change the deploy workflow, hosting, DNS, repo settings, or any other repo. Do not email or message anyone.
- Every figure must come from a page you fetched in this run. If you cannot source a number, leave the sale out and list it under gaps.
- Keep the editor's name off the site and out of the issue.
- The repo is public. Keep the names of private people and any commercial terms out of everything committed, including the build log and the pull request.
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

Price is not the only test. Pick sales a young, finance-literate reader with a short attention span would want to read about. Treat these as reasons to include a sale at any price (the story override), and favor them when choosing what to feature:

- Something went wrong: sold below the low estimate, failed to sell, withdrawn, sold at a loss against an earlier sale, a catalogue caveat (untested, restored, doubtful attribution or provenance), a guarantor left holding the lot.
- A wild multiple: far above estimate, or a record.
- A known person: a named buyer, a famous seller or past owner, a celebrity object.
- A strange or funny object, or a fight: family disputes, restitution, a royal objecting to the sale.

Every week, look for at least one notable sale in each of watches, jewelry, cars, design and fashion or memorabilia, and include it through the story override when it is interesting even if it is under the floor. Do not write "nothing qualified" for a category without having looked; if nothing notable happened, say what is coming up instead. A lot that failed to sell has no price, so it cannot be a row; cover it in the prose with its source. Cap the week at about 40 rows. When over the cap, keep the story overrides and drop the least interesting low-value rows.

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
- `guarantee`: none, house, third_party, irrevocable_bid, guaranteed, or unknown. Use `guaranteed` when a source says the lot was guaranteed but not by whom. Use `unknown` only when nothing was reported; the validator fails a row that says unknown while its financing note mentions a guarantee. Buyer financing is rarely public, so track guarantees and irrevocable bids; use `financing_notes` only for something a source states.
- Buyer: set `buyer_status: reported` with `buyer_name`, `buyer_attribution` (the outlet) and `buyer_profile_url` only when a credible outlet names the buyer. The profile link must be an https page that explains who they are and how they made their money, and you must open it to confirm. Otherwise set `anonymous` and put what is on the record about the bidding in `bidding_notes`. A claim with one weak source stays out of the data and goes in the pull request notes. Never print a guess about a private person.
- `why_it_matters`: 60 words or fewer, plain English, for a finance reader.
- `sources`: every page used, with `url` (https), `publisher`, `type` (primary or press) and `accessed`.
- `image`: optional. Find one image of the exact lot through web search. Prefer a public-domain or openly licensed file (Wikimedia Commons, a museum open-access page); otherwise use an image from press coverage or the house's press release. Do not take images from sothebys.com, whose terms forbid reuse on another site. Open the source page and confirm it shows this work (maker and title match) before using it. Save it to `src/assets/img/` as a JPEG no wider than 1,200 px. Record `file`, `credit` (who made or published the image), `license` (the licence name when public domain or openly licensed, otherwise `Source page`) and `source_url` (the https page it came from). If you cannot confirm the image shows this lot, run the sale without one. List every image added, with its source, in the pull request body.

Then recheck the anonymous rows from the previous three issues for newly reported buyers. If one is now named, update the row and set `updated_at` and `update_note`.

## 5. Check and build

Run, in order: `python3 scripts/fx.py`, `python3 scripts/validate.py`, `python3 scripts/build.py`. Validation must pass. Confirm `site/NNN.html` exists and that `site/index.html` leads with the new issue.

After the issue file is written (step 6), run `python3 scripts/newsletter.py` and confirm `email/NNN.html` and `email/NNN.txt` exist. This drafts the Sunday email. It does not send it; the hard rule against emailing anyone stands.

## 6. Write the issue

Create `src/issues/NNN.md` with this front matter: `number`, `title`, `date` (today), `window` (for example `12 to 14 November 2026`), `status: draft`, `lead` (the id of the lead sale) and `topline` (two or three sentences). Also add the email lines, each on one line: `email_plus`, `email_desk`, `email_number`, `email_number_line`, `email_sales`, `email_term` and `email_term_line`. `scripts/newsletter.py` documents them and the latest issue shows the pattern.

Sections, as in the latest issue:

1. `## Top line`: what happened this week, in three short paragraphs at most.
2. `## Featured sales`: three to seven sales, each on its own line as `{{sale:ID}}`.
3. `## Who bought`: named buyers with attribution, then what is on the record about the unnamed ones.
4. `## Market signal`: one takeaway and one clearly marked opinion. Define any market term in a sentence.
5. `## Outside fine art`: watches, jewelry, cars, design, fashion, as available.
6. `## How to read these numbers`: a short primer for a newcomer. Do not repeat last week's terms.
7. `## All sales in this issue`: a single line, `{{table}}`.

Voice: opinionated, plain, short sentences, written to be read on a phone in two minutes. Lead with tension: who won, who lost, what went wrong, who paid too much. Readers come for the flop, the loss, the bidding war and the strange caveat as much as the record, so put those first and say plainly what they cost someone. Write the title and the first sentence of each section as a hook, the way a good headline is written, while staying accurate and fair: no mockery of named private people, and every claim sourced. Prefer one striking number to three averages. Cut throat-clearing and anything that reads like a catalogue. Link each factual claim inline to its source, as the latest issue does. Summarize in your own words; do not reproduce article text. No emojis. Do not use: delve, explore, seamless, game-changer, robust, leverage, testament, cutting-edge.

The page builder only understands paragraphs, `- ` lists, `**bold**`, links, `##` and `###` headings, and directives on their own line. Do not use tables, italics or nested lists in the issue file.

If fewer than three sales qualify, write a short quiet-week issue: one sale, one signal, and what is coming up next week.

Corrections: when a fact in a published issue turns out to be wrong, add a dated line under `## Corrections` at the end of that issue and set `updated_at` and `update_note` on the row. The new issue starts without a Corrections section.

Before committing, re-read the draft against the data. Every number in the prose must match a row or a linked source. Then rebuild and rerun `python3 scripts/newsletter.py`.

## 7. Log the run

Append a dated entry to `BUILD_LOG.md` in the same pull request, in the format of the most recent entry: what ran, capabilities used, decisions, what worked, failures and workarounds, and elapsed time. Credit use cannot be measured from inside a run, so say to check the usage page.

## 8. Open the pull request

- Check the git author and committer identity before committing. End the commit message with the trailer `Co-authored-by: Perplexity <noreply@perplexity.ai>`.
- Commit `src/`, `site/`, `email/` and `BUILD_LOG.md` on the branch, push it, and open a pull request titled `Issue N: <title>`.
- If validation fails and you cannot fix it, open the pull request as a draft titled `Needs attention: Issue N` and list the failing rows.
- Pull request body: a five-line summary; the window; row counts by category; named buyers and their sources; everything unverified or low confidence; gaps (sales with no readable result); and the three things most worth spot-checking. End with the line `<sub>Created with [Perplexity](<this run's thread URL>)</sub>`.

## 9. Merge and publish

Merge the issue pull request yourself only when all of these are true:

- `python3 scripts/validate.py` passed and the pull request is not a draft or a "Needs attention" pull request.
- No step failed, and the issue has at least one sale with a price confirmed by two sources or by the house.
- Every featured sale has at least one source, and nothing in the issue rests only on a single weak source.
- Any required checks on the pull request have passed (wait for them if they are running).

If all are true, merge with `gh pr merge <number> --merge`. Then wait for the "Publish site to Cloudflare Pages" GitHub Actions run on `main` to finish, and confirm that https://art-moves.pages.dev/ links to the new issue and that https://art-moves.pages.dev/NNN.html loads. If any condition fails, do not merge: leave the pull request open and say why at the top of its body. If the merge or the deploy fails, stop and report it; do not work around it.

## 10. Report

Finish with a short message: the published issue link (or the open pull request link if it was not merged, and why), the five-line summary, and the unverified list. If the run failed, say what failed and whether anything was published.
