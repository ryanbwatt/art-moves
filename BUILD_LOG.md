# Art Moves Build Log

Kept in this repo. Sessions 1 to 3 were written before the repo existed and were moved in at Session 4.

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
- Reading the auction calendar exposed a scheduling point the brief did not anticipate: New York marquee week falls after Issue #1.

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

## Session 5: launch, personal-site link, Phase 2 research (11 Nov 2026)

**Asked:** merge the scaffold, host on free Cloudflare, add a Projects link on ryanbwatt.com, bring contact details onto its About page, start the research.

**Done**

| Step | Result |
|---|---|
| Merged PR #1 (scaffold) and PR #2 (deploy workflow) on `art-moves` | On Ryan's explicit instruction each time. Default stays: he merges. |
| Hosting | Cloudflare Pages project `art-moves`, deployed by a GitHub Actions workflow on merges to `main` that touch `site/`. Live at art-moves.pages.dev. No DNS changed. |
| ryanbwatt.com | PR #3: new Projects page (last in nav) with Art Moves and a one-sentence description; contact details added to About. Contact page left in place. Not merged. |
| Phase 2 research | 34 sale rows, 12 Oct to 11 Nov 2026, in `src/data/sales.json`. Draft PR on branch `issue/001`. |

**Capabilities used:** web search and page fetching, structured extraction from fetched pages run in parallel, GitHub CLI, Python scripts in a cloud sandbox, headless browser screenshots. Connectors: GitHub. Model: Claude (orchestrator); a smaller model for page extraction.

**Research method**

1. About 45 pages fetched: house press releases and results pages first, then trade press (The Art Newspaper, Artnet, Apollo, Observer, Reuters, Hodinkee, Rapaport, WatchPro).
2. Each page reduced to structured lot records (529 lot mentions), then deduplicated by hand into 34 rows.
3. Every figure in a row comes from a fetched page. Where sources disagreed, the row says so in its notes.
4. USD conversion by script, ECB reference rate on the sale date.
5. `validate.py` passes on all 34 rows.

**Decisions**

- Kept only rows above the thresholds. Dropped the two sample rows and the sample issue.
- Popova buyer: two outlets report different things (an advisory firm; a Christie's executive taking the bid). Row is marked anonymous with both reports in the notes.
- One reported buyer only: Shawn Mehta, on a Journe watch, attributed to Hodinkee, including his statement that he bid for a friend.
- Removed a Lalanne design row because the source did not say which Lalanne made the work.
- Issue table now shows the estimate range only; long notes stay on the sale card and in the CSV.

**What worked well**

- Parallel fetch plus extraction turned 45 pages into comparable records in a few minutes.
- Cross-checking press against house releases caught real errors: a hammer price reported as the final price (Journe Régence, CHF 7.1m vs 8.68m), and two different totals for one watch set.
- The validator caught nothing wrong, but it forced every row to carry sources, a price basis and an estimate comparison.

**Limitations, failures, and workarounds**

- Cloudflare: the connector had no Pages actions; the dashboard's Git connection looped (Cloudflare changed its GitHub flow on 10 Nov); the Global API Key was the wrong credential type. Workaround: deploy from GitHub Actions with a Pages-only token stored as a repo secret. First run failed until the secret existed.
- No 1Password connector exists, and the desktop view was not available from a phone, so Ryan had to add the secret himself.
- Sotheby's auction pages do not expose sold prices to a fetch. All 9 Sotheby's rows rely on press, so none is better than medium confidence.
- Christie's and Phillips press releases do not say on the page whether lot prices include premium. Confirmed indirectly (Christie's results pages state totals include premium; hammer prices reported by press are lower by the expected margin).
- Extraction hit a concurrency cap of 16 parallel calls; reran the remainder in a pool of 6.
- Gaps: no fashion or handbag result in the window with a readable price (Christie's Paris handbag sale closes 13 Nov). Design is one low-confidence row. Jewelry is one row; Sotheby's Geneva jewels sold on 11 Nov and had no results yet. No Hong Kong sales fell in the window.
- Images: only the Kandinsky has a verified public-domain image. Others need title-level matching on Wikimedia Commons before use.
- Several sale dates (Phillips watch sessions, Christie's Paris evening sale, Al Thani session) are not confirmed to the day.
- Link checker reports 10 warnings: sites that block scripted requests. The pages were read during research.

**Cost:** credit use not measured per step; check the usage page for this task. Elapsed research time roughly 40 minutes.

## Session 6: buyer rule and Issue 1 draft (11 Nov 2026)

**Asked:** always name the buyer and link, in a new tab, to a profile showing who they are and how they made their money. Merge the personal-site PR.

**Done**

| Step | Result |
|---|---|
| ryanbwatt.com PR #3 | Merged on Ryan's instruction. |
| Buyer rule | New field `buyer_profile_url`. Named buyers link out in a new tab on sale cards, the issue table and the home list. Validator warns when a named buyer has no profile link. Method page updated. |
| Popova row | Changed from anonymous to reported: Beaumont Nathan, credited to Apollo citing the Baer Faxt. |
| Issue 1 | Written in `src/issues/001.md`: top line, seven featured sales, who bought, market signal, outside fine art, how to read the numbers, full table. |

**Decisions**

- "Name the buyer" is applied to every buyer a credible outlet has reported. No further names were found for the other 32 lots after a targeted search, so they stay anonymous with what is on the record about the bidding.
- The two named parties are an adviser and a boutique head, each likely acting for someone else. Their profile links explain their role, not a fortune. The rule fits better once a principal is named.

**What worked well:** re-reading my own draft against the data caught a wrong claim (that the Kandinsky hammered near its low estimate; it hammered above the high) before it shipped.

**Limitations:** every statement in the issue traces to a fetched page, but press sources were read through summaries, not line by line. Ryan should spot-check the seven featured sales before merging.

## Session 7: deploy fix, Project setup, Sunday automation (11 Nov 2026)

Two Computer threads worked this session. The build thread fixed the personal-site deploy. A second thread set up the Project and the automation, and wrote this entry from the build thread's transcript and the repo.

**Asked**

- Build thread: "status? how come projects not showing on ryanbwatt.com?", then "just added ryanbwatt.com", then "merge".
- Second thread: a pasted context pack to turn into a Project; "what do you recommend? when should I use a project?"; "go"; "yes"; then "do all 3 of the suggested", read as the three items the build thread had left open: the Sunday automation, this log entry, and the one-paragraph explanation of Computer.

**Done**

| Step | Result |
|---|---|
| Issue 1 | Art Moves PR #3 merged by Ryan. The deploy workflow ran and Issue 1 is live at art-moves.pages.dev. |
| Personal-site deploy fix | ryanbwatt.com PR #3 was merged but Cloudflare never built it. Ryan restored the Cloudflare GitHub app's access to the repo. PR #4, a one-paragraph README note, gave Cloudflare a new commit to build, and was merged on Ryan's instruction. The Projects page and the About contact details are live. |
| Project | Created as "Ryan HQ", since renamed "Art Moves". Ryan's context pack is the Project instructions. The build thread was moved in, and a snapshot of this log and the architecture proposal sit in Project files. Section 4 of the instructions was rewritten to match the build as it stands. |
| Sunday automation | "Art Moves weekly issue draft". Sundays 9:00 AM ET, first run 15 Nov 2026. Fresh session each run, inside the Project, Standard mode. It opens a pull request and has no merge step. Its saved instructions are copied to `WEEKLY_RUN.md`. |
| Explanation of Computer | One paragraph, at the end of this file. |

**Capabilities used:** GitHub CLI, page fetching, Projects (instructions, files, moving a thread), memory search across threads, reading another thread's transcript, scheduled automation. Second thread's model: Claude Fable 5.2 as orchestrator, no sub-agents.

**Computer on its own vs. Ryan**

| Computer on its own | Ryan |
|---|---|
| Diagnosed the missing build from the absent Cloudflare check on the merge commit, without Cloudflare access | Restored the Cloudflare app's repo access in GitHub; Computer could neither see nor change that setting |
| From a new thread, found the build thread, its documents and its three open items without being given links | Said "merge" for each merge |
| Checked for an existing Project and an existing automation before creating either | Approved moving the build thread into the Project, which Computer could not undo |
| Wrote the automation's instructions from the approved proposal, the repo's scripts and the failures recorded in this log | Approved the rewrite of the Project instructions |

**Decisions**

| Decision | Reason |
|---|---|
| Fresh session per run, all state in the repo | As proposed. A run must not depend on what an earlier chat happened to remember |
| The window starts where the last merged issue ended | Issue 1 ran to 11 Nov, so a fixed Sunday-to-Saturday week would cover 8 to 11 Nov twice. It also survives a skipped week |
| Full instructions saved in the automation, with a copy in the repo | The run works even if the repo copy is missing. The copy keeps a record under version control. The saved automation is what runs |
| No test run tonight | Issue 1 covers through today, so there is nothing new to collect. The 15 Nov run is the test |
| One-off 18 Nov run for marquee week not created | It was a default in the proposal but not one of the three items asked for. Flagged to Ryan |
| This entry arrives as a pull request | The publishing rule: nothing is pushed to `main` |

**What worked well**

- One thread picked up another's open items: memory search found the build thread, its transcript gave the three items.
- Checking state before acting. By the time "do all 3" arrived, the Projects link was already live, so nothing was redone.
- A missing build check on one commit was enough to diagnose the deploy failure from outside Cloudflare.

**Limitations, failures, and workarounds**

| Issue | What happened | Workaround |
|---|---|---|
| Cloudflare did not build the merge | Probably caused by Session 5: while connecting Art Moves in Cloudflare, the Cloudflare GitHub app's repository access was narrowed to `art-moves`. Cause not confirmed, but restoring access fixed it | Ryan restored access |
| Restored access does not rebuild an old commit | Cloudflare only builds on a new commit | A small README pull request |
| Ambiguous instruction | "Do all 3 of the suggested" did not say which three | Read the build thread's last message, which listed exactly three; stated the assumption in the reply |
| Two threads, one log | The second thread cannot write to the build thread's workspace, and the build thread's checkout is now behind `main` | This pull request; the build thread should pull before its next change |
| Project renamed mid-session | The Project's title changed while the second thread was saving files. The file path changed with it and a save failed | Re-synced under the new name and saved again |
| Project instructions out of date | The context pack still described a page on ryanbwatt.com in its planning phase | Flagged, then rewritten on approval |
| Thread move is one-way | Computer can move a thread into another Project but not back to no Project | Asked first |
| Automation untested | No run has happened yet | First run is the test; fix on 15 Nov if needed |
| `status: draft` | The builder ignores `status` unless it is `sample`, so merged Issue 1 still says draft in its source | Cosmetic; left as is |
| Method page ahead of the build | It said a Sunday run existed before one did | True as of this session |

**Would land with an enterprise buyer**

- Approval gates hold when no one is watching: the scheduled run can open a pull request and cannot merge one.
- Standing instructions: a team writes its rules once in a Project and every session there starts with them.
- It asked before the one step it could not undo, and did not ask before the steps it could.
- It said what it could not see (a hosting setting) and handed the person the exact place to fix it.

**Cost:** credit use not measured; check the usage page for both threads.

## Session 8: guiding principles from the editor (13 Nov 2026)

**Asked:** in what reads as a dictated note, after a conversation with his mother, Ryan added principles for the product. Paraphrased prompt: when someone like Ken Griffin buys a $100M Rembrandt, say what it means for Rembrandt and, more to the point, for similar artists, the way AMD moves when Nvidia does; explain why prices move; say whether a peer is now a buy and how to buy it. Add a set of questions on the site (budget, timing, painting or photograph or sculpture) that tailor it for readers who know nothing about art. Through all of it keep answering one question: why do people who are careful with money buy art at all?

**Done**

| Step | Result |
|---|---|
| Read current state first | This log, the open PR #4, `WEEKLY_RUN.md`, the data schema and the Project's notes from the earlier product discussion |
| Checked the premise against research | Five searches: art returns, collector motives, price spillover between artists, current buyer's premium rates, and Rembrandt's circle. Sources are linked in `PRINCIPLES.md` |
| Wrote `PRINCIPLES.md` | The thesis, read-through rules, verdict form, reader questions, guardrails, and a proposed build |
| Did not build | Ryan's rule is architecture first. The read-through data, the questions page and the weekly-run changes wait for his approval |

**Capabilities used:** Project memory, GitHub CLI, web search, file writing. Model: Claude Fable 5.2 as orchestrator, no sub-agents.

**Computer on its own vs. Ryan**

| Computer on its own | Ryan |
|---|---|
| Treated a loose dictated note as a brief and separated it into three ideas: read-through, reader questions, thesis | Supplied the ideas and the analogy |
| Tested the stock analogy against published research instead of accepting it, and wrote down where it breaks | To decide: verdict wording, whether routes include gallery works, whether to prototype before 18 Nov |
| Noticed two conflicts with existing rules and wrote guardrails for them (below) | |
| Left the Sunday automation alone so its first run on 15 Nov tests one thing | |

**Decisions**

| Decision | Reason |
|---|---|
| Principles go in the repo as their own file | The weekly run starts fresh each time and reads the repo. A principle that lives only in a chat is lost |
| Read-through is keyed to the sale, not the buyer | Only 2 of 34 Issue 1 buyers were named, and both were intermediaries. A feature that needs a named billionaire would rarely fire |
| Verdicts proposed as Worth a look, Wait or Pass, with no price targets | The About page says nothing on the site is investment advice. An opinion with its basis shown fits that; a predicted return does not |
| Routes over listings | A route (this artist's etchings sell for this range at these sales) stays true for months. A single lot is gone in a week |
| Reader answers stay in the browser | No account, no tracking and no new service, so nothing needs approval. The cost: no record of what readers choose |
| Corrected the example | Bruegel is not in Rembrandt's circle, as Ryan said himself. The file uses Lievens, Dou, Flinck and Bol so the example is not copied into an issue by mistake |

**Limitations, failures, and workarounds**

| Issue | What happened | Workaround |
|---|---|---|
| The analogy is weaker than it sounds | The one study found on peer prices puts the effect at 2 to 3% for a 10% move in peers, and it is a single working paper on abstract artists | Read-throughs carry a signal label (observed, pattern, none yet) and the issue checks peers' actual results |
| The honest answer to the thesis may be unwelcome | After correcting for which paintings get resold, broad art returns are 6.3% a year with a Sharpe ratio of 0.11, and the buyer pays 28% on top of the hammer price | The thesis is framed as use, identity and access first, with holding value as a constraint. Said plainly in the file |
| Motives conflict with the buyer rule | "Why they bought" invites guessing about private people | Motives are printed only when reported or stated; otherwise the issue reads the structure of the sale |
| Suggesting things to buy raises the stakes on the gallery disclosure | The editor works with a gallery | Any gallery work suggested would be labelled; auction-only is the proposed default |
| Open PR #4 touches this file | A second branch from `main` would conflict | This branch is stacked on `log/session-7`. Merge #4 first, or merge this one and close #4 |
| Dictation | Names came through as "Broegel" and "Maddie" | Read as Bruegel and Matt from context |

**Would land with an enterprise buyer**

- It took a spoken, unstructured idea and returned a structured proposal with sources, without being asked to check the premise.
- It disagreed with part of the brief, showed the evidence and still delivered what was asked.
- It found where a new request collided with rules written in earlier sessions and resolved the conflict in writing.
- It stopped at the approval line the team had set: a proposal and a pull request, no build.

**Cost:** credit use not measured; check the usage page for this thread.

## Session 9: merges and a pressure test (14 Nov 2026)

**Asked:** merge PRs #4 and #5. Then look across this thread and the other thread in the Project, and come back with questions that harden the project against critics now and after. Use Tom Bilyeu's public Instagram captions on validating a business with AI as the model. Stated goal: get young and middle-aged men engaged in art; the payoff is not meant to be money.

**Done**

| Step | Result |
|---|---|
| Merged PR #4, then PR #5 | On Ryan's instruction. Neither touched `site/`, so nothing was redeployed |
| Read the other thread | The build thread, 28 exchanges, including the product discussion of 12 Nov (way-in pyramid, guess-the-price card, picks) |
| Read Bilyeu's posts | One Instagram caption and his profile fetched in full; three more captions read as search excerpts. Quoted and linked in `PRESSURE_TEST.md` |
| Ran his tests on Art Moves | Three searches (competing newsletters, beginner collectors, arts attendance by sex) plus the repo's own data |
| Wrote `PRESSURE_TEST.md` | Audit, the attacks to expect, 14 questions with a lean on each |

**Capabilities used:** GitHub CLI, memory search and reading another thread's transcript, web search, page fetching (a public Instagram caption was readable without a login), file writing. Model: Claude Fable 5.2 as orchestrator, no sub-agents.

**Computer on its own vs. Ryan**

| Computer on its own | Ryan |
|---|---|
| Found and read the other thread without a link | Said "merge" for both PRs |
| Turned a creator's sales-flavoured posts into five tests and adapted "will 1,000 people pay $100" for a project with no revenue goal | Chose the framework |
| Audited its own earlier work and reversed its own recommendation from Session 8 | To answer: the 14 questions |

**Decisions**

| Decision | Reason |
|---|---|
| Call: change it, do not kill it | Six features proposed across two sessions, no confirmed reader, no way to count one |
| Recommend a feature freeze for now | Session 8 recommended prototyping the read-through. Under these tests, a reader's reaction and a first scheduled run are worth more than a seventh feature |
| Questions carry a lean | The same format got a full set of answers on 12 Nov |

**Limitations, failures, and workarounds**

| Issue | What happened | Workaround |
|---|---|---|
| Thread list | Asking for the Project's threads returned every personal thread | Picked the build thread by title and content |
| Dictation | "Arvise" and "Tom Billia" | Read as Art Moves and Tom Bilyeu |
| Premise check | The stated gap in men's interest is 16% against 20% for museum and gallery visits; the larger barrier in the survey is time | Recorded in the audit; question 1 asks what stops Matt |
| Competitor scan | Not exhaustive; four searches | Labelled as such |
| No reader data | The site has no sign-up or visit counts, so nothing about real use could be checked | Questions 5 to 7 |

**Would land with an enterprise buyer**

- It was asked to attack its own work and did, down to withdrawing advice it gave the day before.
- It carried context across two threads without being handed either one.
- It checked the sponsor's premise against public data before building on it.

**Cost:** credit use not measured; check the usage page for this thread.

## Session 10: answers, a sign-up, the Sunday email, and a re-check (14 Nov 2026)

**Asked:** the editor answered the 14 pressure-test questions in one dictated reply and said to merge PR #6. Then: add a sign-up to the site; he will send an email each Sunday, headline first and easy to digest, in the manner of the Wall Street Journal editor's daily note; use the auction houses' own databases more; and be more aggressive with images, since they are public on the internet. He had not done the spot check of Issue 1.

**Done**

| Step | Result |
|---|---|
| Recorded the answers | Added to `PRESSURE_TEST.md` in general terms, then merged PR #6 on the editor's instruction. Docs only, so nothing was redeployed |
| Sign-up section | Built into the home page and each issue page. It is a plain HTML form with no script, pointed at whichever email service is named in `src/config.json`. It renders nothing until that line is filled in, so this change can merge before a service is chosen |
| Sunday email | `scripts/newsletter.py` drafts `email/NNN.html` and `.txt` from the issue's front matter and the data: headline as subject, a "Plus" line, five short numbered sections, a link to the full issue. Issue 1 comes to 527 words, about two minutes. A plain-text copy was placed in the editor's own drafts folder, addressed to himself. Nothing was sent |
| Re-check of Issue 1 | All seven featured prices match their sources. Two statements in the text were wrong and nine rows contradicted their own notes. Corrected, dated and listed on the issue. See `ACCURACY.md` |
| Auction-house data | Read the houses' terms. No public feed; two of three forbid automated collection. Wrote up the route that holds: press offices, one page at a time, and a licensed database if wanted |
| Image question | Answered in the reply, not built. The published rule stands until a replacement is agreed |

**Capabilities used:** GitHub CLI, web search and page fetching (house terms, lot pages, pricing pages for four email services), code execution, a headless browser for checks at desktop and phone widths, the connected email account for one draft, memory. Model: Claude Fable 5.2 as orchestrator, no sub-agents.

**Computer on its own vs. Ryan**

| Computer on its own | Ryan |
|---|---|
| Noticed the repo had been made public since the last session and kept private names and commercial terms out of everything committed | Said "merge" for PR #6 |
| Checked the connected email-marketing account before using it, found it belongs to another organisation the editor works with, and did not use it | To decide: which email service. That is a new service, so it waits for his approval |
| Re-read its own Issue 1 against the sources and published corrections to its own work | Still owes his own read of the seven sales |
| Declined to act on "public images are free to use" and came back with three routes that are | To decide: the image rule |
| Added a validator rule so the guarantee error cannot recur silently | |

**Decisions**

| Decision | Reason |
|---|---|
| Form is switched off by configuration, not by leaving it out | The page work is done and reviewed once; turning it on is a one-line change after a service is approved |
| The email is drafted by script and sent by a person | Same gate as the site: the automation prepares, the editor publishes. The weekly run's rule against emailing anyone stays |
| Email text lives in the issue's front matter | One file per issue for the Sunday run to write and the editor to edit |
| New guarantee value, `guaranteed` | "Unknown" was being used for two different things: nothing reported, and reported without a named backer |
| Corrections printed on the issue, with dates | The method page promises it |
| Named `newsletter.py`, not `email.py` | A file called `email.py` in `scripts/` would shadow Python's own `email` module and break the link checker |
| Proposed changes to the Sunday run are listed, not applied | The saved automation runs from `main` tomorrow morning; changing its instructions before this merges would point it at a script that is not there yet |

**Limitations, failures, and workarounds**

| Issue | What happened | Workaround |
|---|---|---|
| Wrong claim carried over | An earlier session described the repo as private. It was made public from another thread | Checked the repo's visibility before writing; rewrote the answers without names |
| Branch drift | The PR #6 branch had picked up a merge commit from another thread | Reset to the remote branch and re-applied the one commit |
| Email account | The connected marketing account is another organisation's list and sender, and the connector cannot create a new list | Not used. Four services compared for the editor to choose from |
| House sites | Sotheby's lot pages show the estimate but no sold price; Phillips' terms page would not open | Monet price stays press-reported; Phillips' terms are marked unverified |
| Own error | The Popova was written up as if it had no guarantee, while the row's own note said every lot in that sale was guaranteed. The validator passed it | Corrected, and the validator now catches the pattern |
| Context limit | The session ran long enough that earlier steps were summarised. The summary's figures were treated as unverified | Re-opened the lot pages and the press report before printing a correction |
| Email layout | Drafted as HTML and plain text; only the plain text can be placed in the drafts folder through the connector | The HTML version is in `email/` for whichever service is chosen |

**Would land with an enterprise buyer**

- It audited its own published output, found it wrong in two places, and filed the correction with dates and a control to stop a repeat.
- It refused the convenient route twice: another organisation's mailing list, and a data collector that would break two sets of website terms. Both times it gave the compliant alternative and its cost.
- It treated its own summary of earlier work as unverified and went back to the sources before publishing.
- New services stayed behind an approval: the form is built, tested and switched off.

**Cost:** credit use not measured; check the usage page for this thread.

### Session 10, later the same evening: merge, service chosen, and a correction to a correction

| Step | Result |
|---|---|
| Merged PR #8 | On the editor's instruction. The deploy ran in under a minute. Checked on the live address in a fresh browser: corrections showing, lot numbers showing, sign-up form absent as intended, data table still sorting, no sideways scroll at phone width |
| Email service | The editor chose Buttondown. The form is already built for it. Switching it on needs one thing only he can do: create the account. Then one line in `src/config.json` |
| Found an error in the correction | The note published earlier in the session said nine sale cards had shown the guarantee as unknown. One card did; the other eight were data rows with no card. Found while checking the live page, where the new label appeared once, not nine times. Fixed and dated |

**Computer on its own vs. Ryan:** Ryan said "merge" and picked the service. Computer checked the live result against what it had claimed, caught its own overstatement, and opened the fix without being asked.

**Limit:** Computer cannot open an account with a new service on the editor's behalf; that step is his.

**Would land with an enterprise buyer:** the check after release is what found the error. The claim in the pull request and the page on the live address disagreed by a count of eight, and the agent reported it against itself.

### Session 10, last step: sign-up switched on

| Step | Result |
|---|---|
| Merged PR #9 | On the editor's instruction. Checked on the live address: the reworded correction is showing |
| Editor opened the Buttondown account | He sent the username in a two-word message. That was the one step only he could do |
| Form pointed at the service | One line in `src/config.json`. The form's small print and the method page now say that sign-ups go to Buttondown and are confirmed once by email, which the service requires |
| Checked the service's public page before switching on | The newsletter was still titled with the account holder's name, not the publication's. The site's rule is that the editor is unnamed, so the pull request says to rename it before merging |

**Computer on its own vs. Ryan:** Ryan created the account and said "merge". Computer read the service's public page instead of assuming the set-up was complete, and held its own pull request behind a setting it cannot reach.

**Limits:** no test sign-up was sent to the live service, because that would create a real subscriber record and a real email. The form's fields were checked against the service's documentation instead. The first real sign-up is the editor's to make.

**Would land with an enterprise buyer:** a standing rule written days earlier (keep the editor unnamed) was applied to a third-party page nobody asked it to look at.

## Session 11: sign-up live, Sunday run brought up to date (15 Nov 2026)

Just after midnight, nine hours before the first Sunday run.

| Step | Result |
|---|---|
| Merged PR #10 | On the editor's instruction. He had renamed the newsletter in the email service between the warning and the merge; the service's public page showed "Art Moves" when checked afterwards. The form is live on the home page and the issue page |
| Editor tested the sign-up | He signed up with his own address and reported that it worked. Computer did not submit one, since that creates a real subscriber |
| Sunday automation updated | The five changes listed as pending in `WEEKLY_RUN.md` were applied to the saved automation. Before the edit, the saved instructions were compared with the copy in the repo and matched exactly. After it, the saved text was read back and `WEEKLY_RUN.md` was regenerated from it, so the two cannot drift |
| Dry run of a second issue | In a throwaway copy, four rows were moved to a made-up Issue 2. Validation passed, the site built, the sign-up form appeared on the new page, and the email draft was written with fallbacks for the lines a draft might lack. Nothing from the dry run was committed |
| Postal address | The editor asked where it goes. Answered in the conversation: the email service's footer setting. No address has been added to the repo |

**Computer on its own vs. Ryan:** Ryan merged by instruction, tested the form, and gave the go-ahead on the automation in one dictated line. Computer read that line as a yes, said so in its reply, and made the change in a way that is easy to undo: the previous instructions are in this repo's history.

**Failures and limits:**

- The automation has still never run. A matching copy and a passing dry run show the instructions and the scripts agree; they do not show that an unattended run finishes.
- If this pull request is still open when the run starts, both will add to this log and one will need a small manual merge.
- The email service says its own lawyers read the US postal-address rule as applying to advertising, which it does not allow. That is the service's reading, not legal advice, and the address goes in anyway.

**Would land with an enterprise buyer:** the instructions that run unattended are kept as a file under version control, checked against the live automation before and after every change. Anyone can see what the agent is told to do each week and when that changed.

## Session 12: first unattended Sunday run, Issue 2 drafted (15 Nov 2026)

The scheduled automation ran on its own at 9:00 AM ET. Nobody was in the conversation.

| Step | Result |
|---|---|
| Set up | Cloned the repo, read the README, the about page, the schema, Issue 1 and the dataset. No issue pull request was open, so nothing was stacked. Branch `issue/002` |
| Window | 12 to 14 November 2026, the day after Issue 1's window through yesterday |
| Earlier-window pickups | Sotheby's Geneva jewels sales on 11 November were not in Issue 1 because their results came out after it was drafted. Seven lots added, all checked for an existing row first |
| Research | Christie's Shanghai results read from the house's own results pages; Sotheby's results from trade press, since Sotheby's pages do not show sold prices; Heritage from its press release. Each figure checked against a second outlet where one existed, and disagreements written into the row |
| Rows | 13 new: 8 jewelry, 4 fine art, 1 memorabilia. One buyer named (a jewellery firm, reported by National Jeweler citing Sotheby's) |
| Recheck of earlier anonymous rows | Issue 1's anonymous buyers searched again. None newly named. One row (the Bulgari Pink) gained a dated bidding note |
| Images | None added. The only lot photographs found were auction-house or news-agency pictures, which the image rule does not allow |
| Scripts | `fx.py` filled 13 rates, `validate.py` passed 47 rows, `build.py` wrote `site/002.html` with the home page leading on Issue 2, `newsletter.py` wrote `email/002.html` and `email/002.txt`. Nothing sent |
| Pull request | Opened from `issue/002`. Not merged |

**Computer on its own vs. Ryan:** all of it. Ryan's part is the Sunday edit pass and the merge.

**Failures and limits:**

- Sotheby's hides prices, so seven of the thirteen rows rest on press figures, several rounded to the nearest CHF 100,000 by one outlet and exact in another. They are marked medium or low confidence.
- Two figures could not be settled: the estimate on an 8.11-carat pink diamond (two ranges published) and whether Heritage's lightsaber price includes its fee (not stated). Both are flagged in the rows and the pull request.
- The email draft prints the house label "Other" before a city for houses outside the big three ("Other Dallas"). That is a template issue in `scripts/newsletter.py`, left alone because this run edits content, not scripts.
- Several large sales from Issue 1's window that Issue 1 missed (outside this run's rules for pickups) are listed in the pull request for the editor to decide on.

**Would land with an enterprise buyer:** the run held to rules written a week earlier with nobody watching. It left out an image it could have used, kept a weakly sourced claim out of the published text, and flagged its own uncertain numbers in the pull request instead of smoothing them over.

**Elapsed time:** not measured reliably inside the run; the thread timestamps have it. **Cost:** credit use not measured; check the usage page for this thread.

### Session 12, afternoon: Issue 2 published, Sunday run now publishes itself

| Step | Result |
|---|---|
| Merged PR #14 | On the editor's instruction. Deploy finished; the home page leads with Issue 2 and `/002` loads |
| Editor's decision | The Sunday run should merge and publish its own issue. With no readers yet, review before publishing slows iteration more than it protects anyone. He reads after publication instead |
| Automation updated | It now merges its own issue pull request only when validation passes, nothing failed, and nothing rests on one weak source; then it confirms the deploy. Any other pull request still waits for the editor. Email is still sent by hand |
| Selection and voice | The run now picks sales for story as well as price: flops, losses on resale, catalogue caveats, wild multiples, famous owners, odd objects, at any price, and looks in every category before saying a week was empty. Voice leads with who won, who lost and what went wrong, written to be read on a phone |
| Method page | It said a human approves every issue before publication. Reworded to say the editor reads every issue after it goes out, with dated corrections |
| `WEEKLY_RUN.md` | Regenerated from the saved automation after the edit |

**Computer on its own vs. Ryan:** Ryan made the call to drop the review step and gave the editorial direction. Computer chose the conditions under which the run may merge, and found the public method page claim that the change would make untrue.

**Would land with an enterprise buyer:** the human approval step was removed by the owner, but the agent still has explicit conditions under which it stops and waits, and the public page was corrected so it doesn't overstate the oversight.

## Session 13: price history and the three questions (15 Nov 2026)

**Asked for:** a data view a finance reader would recognise (a price chart and key statistics under each work, as on Google Finance), a clearer statement of what the site is for, and a view on reader tailoring and a trade service.

| Change | Detail |
|---|---|
| Price history | New optional `history` field on a sale: earlier changes of hands, oldest first, each with date, event, venue, price, basis and source. A sale with history gets a panel: current price, change since the last documented sale, an inline SVG chart, eight statistics and the full record. Hover or keyboard focus on a point shows that sale |
| Data filled in | De Kooning (2015 auction, 2018 private sale), Richter (2011 auction), Rothko (1992 auction), Kandinsky (1927, 1940, 1972, 2023), Bacon (1994, 2006, both private), and from Issue 2 the Romanov sapphire (1927, 1971, 1992, prices not reported) and Zao Wou-Ki's Mars (2019, a loss, one source). Every entry has a source |
| Rebased | Rebuilt on top of Issue 2 (#14) after it merged. The panel shows the full documented history for each work; no range buttons, at the editor's call |
| Data page | A Price history section above the table; works with a dollar comparison first |
| Home page | "Every issue asks" strip with the three questions |
| Method | The three questions, and a Price history section on what counts as a price and what the figures leave out |
| Checks | `validate.py` checks the history entries: fields, date format and order, event and basis values, sources |

**Decisions made by Computer, for the editor to check:**

- Annualized figures appear only when an earlier sale has a reported dollar price. The Kandinsky's 1940 and 1972 prices are in guilders and are shown without a return.
- HENI lists a 2002 Christie's New York sale of the Richter at $1.05m. The catalogue provenance does not mention it, so it is noted and left out of the chart.
- The Rothko's 1992 price is $264,000 with fees (Artnet), not HENI's $240,000, so both ends of the comparison include fees.
- No P/E or market-cap equivalent. A single work has no earnings and no float; the nearest honest measures are the multiple, the holding period and the annualized change.
- Not built: questionnaire, accounts, and any trade or consignment page. See the pull request for the reasoning.

## Explaining Computer to a customer new to AI agents

Based on this build:

Perplexity Computer is an assistant that does the work instead of describing it. You give it a goal in plain language. It plans the steps, searches and reads sources, writes and runs code on its own cloud machine, uses the accounts you connect (here, GitHub), and comes back with a finished thing: in this build, a live website, a sourced dataset of 34 sales and a first issue, inside a day. Three things make it safe to hand real work to. It shows its sources, so every number can be checked. It stops where you tell it to: nothing reached the live site without a person merging a pull request, and the weekly scheduled run is held to the same rule. And it tells you what it could not do: here it could not read one auction house's prices, guessed the site's framework wrong from the outside, and could not see a hosting setting, and each time it said so and offered a way round. Treat it like a capable new analyst. Give it a clear brief, access to the right systems and a review step, and it will take a multi-step job from research to a recurring process while you keep the final say.
