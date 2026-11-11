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
| `BUILD_LOG.md` | Running record of the build |

Run, in order: `python3 scripts/fx.py`, `python3 scripts/validate.py`, `python3 scripts/build.py`. Python 3, no packages.

## Hosting

Any static host. For Cloudflare Pages: no framework preset, no build command, output directory `site`.

## Publishing rule

Changes go on a branch and a pull request. The editor merges. Nothing is pushed to `main` directly.
