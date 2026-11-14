# Accuracy note

14 November 2026. Two parts: a re-check of the seven featured sales in Issue 1, and what the auction houses' own sites allow as a source.

## Part 1. Re-check of Issue 1

**Result:** all seven prices match their sources. Two statements in the issue text were wrong and nine rows had a field that contradicted their own notes. All are corrected in this change and listed on the issue under Corrections.

This was a machine re-read of the sources by Perplexity Computer. It does not replace the editor's own check, which is still owed.

### The seven sales

| Sale | Printed | Checked against | Result |
|---|---|---|---|
| Monet, Iris | €50M with fees; estimate €22M to €30M; six bidders, about 45 minutes; Asia, by phone; no guarantee | [Reuters](https://www.reuters.com/lifestyle/claude-monets-iris-becomes-most-expensive-artwork-sold-auction-france-sothebys-2026-10-23/), [The Art Newspaper](https://www.theartnewspaper.com/2026/10/23/monets-monumental-iris-makes-56m-in-paris), [MutualArt](https://www.mutualart.com/Article/Schlumberger-Collection-Monet-Nets--50-M/1F33CD3C04A4A806), [Sotheby's lot page](https://www.sothebys.com/en/buy/auction/2026/la-collection-schlumberger-le-temps-retrouve/iris?locale=en) | Matches. The estimate is now confirmed by the house. The price is still press-only: the lot page shows no sold price to a reader without an account. Lot number (4) and date of the work added |
| Kandinsky, Das bunte Leben | £27M hammer, £31.56M with fees; third-party guarantee | [Christie's release](https://press.christies.com/christies-london-2021-evening-sales-totals-ps219-million/), [The Art Newspaper](https://www.theartnewspaper.com/2026/10/15/christies-achieves-%C2%A3219m-in-steady-solid-london-sales), [Christie's lot page](https://www.christies.com/en/lot/lot-6609206) | Matches. Lot number (115) added. See the soft spot below on the estimate |
| Popova, Painterly Architectonic | £6.2M hammer, £7.64M with fees; artist record; bought by Beaumont Nathan | Christie's release, The Art Newspaper, [Apollo](https://apollo-magazine.com/auction-report-october-2026-london-peter-simon-modern-british/), [Artnet](https://news.artnet.com/market/christies-hauls-in-289-9m-at-london-sales-led-by-41-8m-kandinsky-2824027) | Price and buyer match. **The guarantee was wrong**, see finding 1 |
| F.P. Journe, Résonance Régence | CHF 8,680,500 with fees | [Phillips](https://www.phillips.com/auction/CH080426), [Hodinkee](https://www.hodinkee.com/articles/three-takeaways-from-the-geneva-fall-auction-season) | Matches |
| F.P. Journe, Résonance 022/99R | CHF 4,936,000 with fees; won by Shawn Mehta, who says he bid for a friend | Phillips, Hodinkee | Matches |
| Bulgari Pink | CHF 12,086,000 with fees; estimate CHF 10M to CHF 15M | [Rapaport](https://rapaport.com/news/bulgari-pink-diamond-rakes-in-nearly-15m-at-christies/) | Matches. Hammer price not reported |
| Ferrari 499P Modificata | CHF 8,217,500 with fees; stays at the factory until December 2028 | [Christie's release](https://press.christies.com/gooding-christies-sells-first-ferrari-499p-modificata-at-auction-achieves-over-chf-21-million-at-inaugural-geneva-sale), [Classic Driver](https://www.classicdriver.com/en/article/auctions/why-did-someone-pay-10-million-dollars-a-le-mans-ferrari-cant-race) | Matches |

### Findings

| # | Finding | Fix |
|---|---|---|
| 1 | The Market signal section listed the Popova beside "the unguaranteed Monet" as a real contest, which read as if it had no guarantee. The Art Newspaper: "All 41 lots were guaranteed, with 11 of them guaranteed by the house and the rest by third-party." | Sentence rewritten: the Popova is a guaranteed lot that sold at more than three times its low estimate |
| 2 | The top line said "the biggest prices came with the least pre-arranged support". True of the Monet only. The second and third prices, the Kandinsky and the large Mondrian, had third-party guarantees | Now "the biggest price came with no pre-arranged support" |
| 3 | Nine rows (six Simon lots, the de Kooning, the Rothko, the Modigliani) had `guarantee: unknown` while their own financing note said a source reported a guarantee. Sale cards printed "Guarantee: Unknown" | New value `guaranteed` (shown as "Guaranteed, backer not stated"). `unknown` now prints "Not reported". The validator fails any row whose financing note mentions a guarantee while the field says unknown |
| 4 | Lot numbers missing on the Monet and the Kandinsky | Added from the houses' lot pages |

### Soft spots left as they are

| Item | Why it is soft |
|---|---|
| Kandinsky estimate | Christie's published "estimate on request" in its [pre-sale release](https://press.christies.com/wp-content/uploads/2026/10/0034992b210062227f5b3d8e8178ecd8.pdf). The £18M to £25M range is from the press. Apollo gives £18M to £35M, which would make the £27M hammer inside the estimate, not above it. The row says so |
| Monet price | Press-reported, not house-confirmed. Three outlets agree |
| Monet, Bulgari Pink, Riley | Compared with the estimate using the price with fees, because no hammer price was reported. Flattering to the result; the rows say so |
| The other 27 rows | Not re-checked in this pass |

## Part 2. Using the auction houses' own data

**Short answer:** there is no public feed to tap. None of the three houses offers one, and two of them forbid automated collection in their terms. The sustainable route is their press offices, plus a licensed price database if the budget allows.

| House | What its terms say | What that means here |
|---|---|---|
| Christie's | Users may not use "any robot, spider, scripts" to "data mine or scrape any of the content", or "otherwise access or collect any of the Content, data, or information from the Web Site using automated means". Material may not be reused on another site without written permission ([terms](https://www.christies.com/about/terms-and-conditions/terms-and-conditions-for-website-use)) | No bulk collection. The weekly run reads individual christies.com pages one at a time, which sits uneasily with the clause on automated means. Prefer the press site (its terms were not checked) |
| Sotheby's | No "data mining, spidering, 'screen scraping'" or "any other automatic means of obtaining information". "You agree not to download or use images hosted on the Digital Platforms on another website, for any purpose" ([terms](https://www.sothebys.com/en/terms-conditions)) | No bulk collection, no images. Lot pages show estimates but not sold prices without an account, so press stays the price source |
| Phillips | Website terms could not be opened. Unverified | Its auction pages list sold prices lot by lot. Treat as the other two until the terms are read |

Facts are not owned: a hammer price is a fact and can be reported with attribution. The limits are on how the pages are read and on reusing the houses' text and images.

### Recommended route

| Step | What it gives | Cost |
|---|---|---|
| Ask the three press offices to add Art Moves to their results lists | Results releases by email on sale night, and press images cleared for editorial use with a credit line | Free. Needs a contact name and address, which the site does not show today |
| Keep reading press releases and trade press one page at a time | What the dataset is built on now | Free |
| Licensed price database, if wanted | Auction results with history, cleared for lookup. [Artnet Price Database](https://www.artnet.com/price-database/) from $42.50 for 30 days; [Artprice](https://www.artprice.com/subscription) from €305 a year | Paid. A new service; needs the editor's approval. Check the licence before republishing rows |
| Do not build a collector that walks the houses' sites | | Breaks two sets of terms and would be the first thing a critic checks |
