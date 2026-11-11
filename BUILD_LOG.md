# Art Moves Build Log

Kept in the Computer workspace until a repo is chosen, then moved into the repo.

## Session 1: Wed Nov 11, 2026. Planning

### What Ryan asked for
A build architecture proposal for Art Moves, with no code, repo writes, deployment, or automation until he approves in writing.

### What Computer did
| Step | Capability used | Result |
|---|---|---|
| Read the project brief | File reading | Brief parsed; planning-only constraints noted |
| Site discovery | Code execution (HTTP requests, DNS lookups) | ryanbwatt.com identified as static HTML on Cloudflare Pages, project `ryanbwatt-com` |
| GitHub check | Public GitHub pages only | One public repo (`peaked-redesign`), unrelated to the site |
| Connector check | Connector discovery | GitHub, Vercel, and Cloudflare connectors exist but are not connected; GitHub connection prompt shown |
| Source feasibility test | Page fetching with extraction | Christie's readable; Phillips partly; Sotheby's failed |
| Market research | Web search | Confirmed material for Issue #1 and the New York marquee week dates |
| FX source test | Code execution | ECB reference rates via the Frankfurter API returned rates for a past date |
| Proposal | Document writing | `art-moves-architecture-proposal.md` |

Model: Claude Fable 5.2 as orchestrator. No sub-agents.

### Decisions and reasoning
| Decision | Reason |
|---|---|
| Recommend `/art-moves` over a subdomain | No DNS change, one repo, inherits the site's design |
| JSON file in Git over a database | A few dozen rows a week; Git gives history and portability |
| Research at run time over coded collectors | Two of three house sites were unreliable to automated reading |
| Per-category thresholds | One number does not work across paintings, watches, and handbags |
| Replace "how it was funded" with guarantee tracking | Buyer financing is rarely public; guarantees are published |
| Pull request as the approval gate | Gives a diff, a preview, and a single action to publish |

### What worked well
- Identifying the host without any account access: the `pages.dev` address serves a byte-identical copy of the site.
- Parallel research: ten searches and page reads at once surfaced enough verified material to outline Issue #1.
- Reading the auction calendar exposed a scheduling point the brief did not anticipate: New York marquee week lands on the interview week, after Issue #1.

### Limitations, failures, and workarounds
| Issue | What happened | Workaround |
|---|---|---|
| GitHub not connected | Could not look at private repos, so the site repo is unconfirmed | Connection prompt shown; public profile checked meanwhile |
| GitHub public API rate limit | The unauthenticated API refused the request from the shared sandbox address | Read the public profile page instead |
| DNS tooling | `dig` and `whois` are not installed in the sandbox, and the DNS-over-HTTPS lookups for NS and TXT returned nothing usable | Inferred Cloudflare from A records and headers; nameservers unconfirmed |
| Sotheby's pages | Sale page and press page both failed to load | Search results still surfaced Sotheby's pages; plan relies on press fallback with a source flag |
| Phillips index pages | Past-auctions and press index returned no listings | Individual auction pages do show lot prices; reach them via search |
| Credit estimate | The brief asks for a per-run estimate; Computer cannot predict its own credit use reliably | Measure it from the Phase 4 test run |

### Cost
Time: one planning session. Credits: check the usage page for this session; not estimated here.

## Session 2: Wed Nov 11, 2026. Phase 1 scaffold

### What Ryan asked for
"Go": approval of the architecture proposal with all defaults.

### What Computer did
| Step | Capability used | Result |
|---|---|---|
| Checked GitHub access | Connector discovery | Still not connected; connection prompt shown again |
| Read the live site's stylesheet and page markup | Code execution | Art Moves pages reuse the site's nav markup and `/style.css` unchanged |
| Wrote the data layer | Code execution | `sales.json` schema, `fx.py` (ECB rates), `validate.py` |
| Wrote the page builder | Code execution | `build.py`, standard library only: landing, issue, archive, data, method pages plus CSV and JSON downloads |
| Two sample rows | Earlier research | One Christie's painting, one Phillips watch, both from house pages |
| Visual check | Headless browser (Playwright) | Five pages rendered at 1280px and 375px; no horizontal overflow; column sort works |

### Decisions and reasoning
| Decision | Reason |
|---|---|
| Build locally before the repo is known | The scaffold does not depend on the repo; it keeps the timeline moving while GitHub is unconnected |
| Source in `art-moves-src/`, output in `art-moves/` | Output is committed so the host needs no build step; the two folders drop into any repo |
| No Markdown library | A 30-line renderer covers what issues need and keeps the build dependency-free |
| Did not create a Computer preview link | The brief says publish nothing without approval; screenshots are enough for layout review |
| Sample issue numbered 0 and flagged | It must be removed before Issue #1 and cannot be mistaken for editorial |

### What worked well
- The FX script, validator and builder ran clean on the first full pass.
- Matching an existing hand-written site was simple because its CSS is small and documented in comments.

### Limitations, failures, and workarounds
| Issue | What happened | Workaround |
|---|---|---|
| GitHub still not connected | No repo access, so no branch, PR or Cloudflare preview URL | Work is committed in a local repository in the Computer workspace, ready to push |
| No real preview URL | Without the repo there is no Cloudflare branch preview | Local server plus screenshots |
| First CSS pass | The site's `#content a` rule outranked the Art Moves brand-link colour | Raised selector specificity; caught in the screenshot review |

### Cost
Time: one short session. Credits: see the usage page.

## Session 3: Wed Nov 11, 2026. GitHub connected, repo found

### What Computer did
| Step | Capability used | Result |
|---|---|---|
| Connected GitHub | GitHub connector (second attempt; the first authorization failed) | Read access to private repos |
| Found the site repo | GitHub CLI, read-only | `ryanbwatt/ryanbwatt.com`, private, Astro 7, Cloudflare Pages building from `main` |
| Read the repo's working rules | File reading | `AGENTS.md` and `DECISIONS.md` set strict design rules the Phase 1 scaffold does not follow |
| Found earlier Art Moves work | Git history | Unmerged branch `worktree-art-moves` (Nov 8): Astro routes, RSS, a pilot Issue #1, a different issue format |

### Decisions and reasoning
| Decision | Reason |
|---|---|
| Stopped before opening any pull request | The scaffold overlaps and conflicts with the existing branch; which one wins is Ryan's call |

### What worked well
- Reading the repo's own rule files before writing to it caught the conflict before anything was pushed.

### Limitations, failures, and workarounds
| Issue | What happened | Workaround |
|---|---|---|
| Wrong stack guess in the proposal | From outside, the site looked like plain HTML with a small template script. It is Astro. The host and deploy path were right | Corrected here; the scaffold's static output would still deploy, but it is not how the repo adds pages |
| Scaffold built without repo context | Phase 1 was built while GitHub was unconnected, so it missed the site rules (no page heading, no hairline rules, no JavaScript, 500px column) and the existing branch | Keep the data layer; rework the pages once Ryan picks a path |
| Brief did not mention the earlier build | The Computer brief said "you have no other context" | Surfaced the branch and asked |

## Session 4: Wed Nov 11, 2026. Direction change: standalone site

### What Ryan asked for
A thought partner on where Art Moves should live, then: its own repo and URL (following how Patrick Collison links ventures out to their own domains), his name off the site, public images of the works, and a design inspired by David Zwirner, Gagosian, Hauser & Wirth, 52 Walker, Platform, Uprise Art, Artsy, and the architecture firms OMA, KPF and Herzog & de Meuron.

### What Computer did
| Step | Capability used | Result |
|---|---|---|
| Checked how patrickcollison.com handles projects | Page fetch and code execution | Writing stays on his site; ventures link out to their own domains |
| Looked at the reference sites | Headless browser screenshots | Zwirner, Gagosian, OMA and 52 Walker loaded; Artsy and Herzog & de Meuron returned bot checks |
| Found a usable image | Wikimedia Commons API | Public-domain photograph of the Kandinsky, with credit recorded in the data |
| Redesigned the site | Code execution | Standalone pages: white ground, image on a pale wall, serif headlines, label column, index table |
| Visual check | Headless browser | Five pages at 1440px and 375px, no overflow, no console errors, sort works |
| New repo | GitHub CLI | Private `ryanbwatt/art-moves`, scaffold on a branch with a pull request |

### Decisions and reasoning
| Decision | Reason |
|---|---|
| Separate repo and URL | Matches the Collison pattern, keeps the personal site's rules intact, allows images, and can take a custom domain later |
| Left the old `worktree-art-moves` branch alone | It no longer conflicts, and its pilot issue exists nowhere else |
| Read "public images" as public domain or openly licensed | The brief's copyright rule excludes auction-house photographs |
| Relative links and committed output | The site works at any address and needs no build step on the host |
| Editor unnamed; gallery disclosure kept generic | Ryan wants his name off a standalone site |

### What worked well
- The data layer and builder from Phase 1 carried over; only templates and CSS were rewritten.
- The image field is validated like any other fact: no licence and source, no image.

### Limitations, failures, and workarounds
| Issue | What happened | Workaround |
|---|---|---|
| Phase 1 pages thrown away | They were built to match ryanbwatt.com before the direction changed | Kept scripts and data, rewrote presentation |
| artmoves.com | Registered by someone else since 2003 | Launch on the host's free address; pick an available domain later |
| Two reference sites blocked automated viewing | Artsy and Herzog & de Meuron served bot checks | Worked from the four that loaded and general knowledge of the other two |
| Font request | Asking Fontshare for both families in one URL silently returned only one, so headlines fell back to Times | Split into two requests; caught in the screenshot review |
| Images are scarce | Most contemporary works and all watches, cars and jewelry have no free image | Sales without one show a plain category tile |
| Cloudflare not connected | Computer cannot create the hosting project | Ryan creates it, or connects Cloudflare |
