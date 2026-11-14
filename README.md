# Art Moves

A free weekly brief on where serious money moves in the art and luxury markets.

| Path | What it is |
|---|---|
| `src/data/sales.json` | One object per sale. The source of truth |
| `src/issues/NNN.md` | Issue text. `{{sale:ID}}` renders a sale, `{{table}}` renders the issue's table |
| `src/pages/about.md` | Method page |
| `src/assets/` | Stylesheet and images. Images must be public domain or openly licensed, with credit recorded on the sale |
| `scripts/fx.py` | Fills USD conversions from ECB reference rates |
| `scripts/validate.py` | Checks every row; must pass before a pull request |
| `scripts/build.py` | Renders everything into `site/` |
| `site/` | The published site. Generated; do not edit by hand |
| `PRINCIPLES.md` | Guiding principles: the question each issue answers, read-through to peer artists, verdicts, reader questions. Includes a proposed build that is not started |
| `BUILD_LOG.md` | Running record of the build |
| `WEEKLY_RUN.md` | Copy of the instructions the Sunday automation follows |

Run, in order: `python3 scripts/fx.py`, `python3 scripts/validate.py`, `python3 scripts/build.py`. Python 3, no packages.

## Hosting

Cloudflare Pages, project `art-moves`. `.github/workflows/deploy.yml` uploads `site/` on every merge to `main` that changes it. It needs one repository secret, `CLOUDFLARE_API_TOKEN`: a Cloudflare API token with the single permission Account > Cloudflare Pages > Edit.

## Weekly run

A Perplexity Computer automation runs on Sundays at 9:00 AM Eastern. It researches the week, adds rows, drafts the next issue and opens a pull request from a branch named `issue/NNN`. It has no merge step. See `WEEKLY_RUN.md`.

## Publishing rule

Changes go on a branch and a pull request. The editor merges. Nothing is pushed to `main` directly.
