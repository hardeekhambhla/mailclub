# Handoff

**Cloudflare deploy (2026-09-25)**: site is deployable to Cloudflare Pages; Flask stays for local dev only.
- `build.py` renders `templates/` to `public/` (`/`, `/issues/001` as `issues/001.html`, `/static/*`). `public/` is gitignored.
- `functions/waitlist.js` = Pages Function for `POST /waitlist`; stores `email:<lowercased>` -> ISO timestamp in KV binding `WAITLIST` (dedupes).
- Pages settings: build cmd `pip install -r requirements.txt && python3 build.py`, output dir `public`, prod branch `main`. KV binding `WAITLIST` is set in the dashboard (Settings > Bindings) - deliberately no `wrangler.toml`, since one would override dashboard bindings.
- Local test: `make cf-dev` (wrangler pages dev, local KV). Read signups: `npx wrangler kv key list --namespace-id <id>`.
- Adding a page: add the route to `ROUTES`/`PAGES` in `build.py` as well as `app.py`.

**Second overflow/navigation/polish pass (fixed 2026-09-17, same day, later session)** —
this time actually verified with a real browser (see "Browser testing" below), not by hand
calculation, after two rounds of blind guessing failed:
- **`flipPrev()`/`flipNext()` totally dead (real bug)**: `disableFlipByClick: true` (added
  earlier to protect the fun-facts page's clicks) turns out to guard the *same* internal
  `flip()` method the nav buttons call — confirmed by reading page-flip.js's source directly.
  Removed it; fixed the click-forwarding concern properly instead by adding
  `e.stopPropagation()` in that page's own click handler.
- **Persistent overflow on pages 6-9 (real bug)**: the map page's `.route-line` (11 stops)
  was never scoped down for book-page width at all — full desktop spacing alone ran ~500px,
  more than an entire page's budget. Also found several inline `style="margin-top:30px"` /
  `style="font-size:16px"` etc. on specific elements that were silently overriding the
  book-page CSS tightening (inline always wins) — e.g. Chapter Two's stat-strip. Fixed both;
  also switched pages 8/9's evidence photos to an image-left/text-right layout instead of a
  narrow centered thumbnail (uses full page width, per user request, and incidentally solved
  their overflow too).
- **"Empty space on almost every page" (real bug, not a content problem)**: page-flip.js
  sets `display: block` as an **inline style** on every `.book-page` (needed for its own
  absolute-position layout) — that permanently beats any `display: flex` in a stylesheet, so
  `justify-content: center` on `.book-page` itself was NEVER actually taking effect this
  whole build, on any page. Real fix: every page's content is now wrapped in an inner
  `<div class="page-inner">` (added via a small Python script using a div-depth counter,
  since pages contain their own nested divs so a naive regex can't find the matching close
  tag) that the library never touches, and centering moved onto that. Also gave the cover
  page a real illustrated route/ship graphic (was a tiny flourish) and let the Dear Reader
  portrait be genuinely bigger, both to use freed-up space rather than just leaving it blank.
- **Device-specific testing**: user is on a Samsung Galaxy S24 (confirmed CSS viewport
  360×780) — that became the primary test target once known, alongside a deliberately harsh
  780×437 (short/wide) stress case.
- **Browser testing note for future sessions**: this environment has no browser by default
  (Playwright MCP returns ECONNREFUSED on :9222), but `google-chrome` is installed — launching
  it manually with `--headless=new --remote-debugging-port=9222 --remote-debugging-address=0.0.0.0
  --no-sandbox --user-data-dir=/tmp/chrome-profile about:blank &` makes the Playwright MCP
  tools connect successfully (they were trying to reach exactly that port). Do this BEFORE
  attempting any further visual/interaction work — hand-calculating pixel fit without this,
  like the first two attempts at this book did, does not work reliably.
- **Playwright gotcha**: navigating to a `#hash` variant of the *same* URL already open in
  the tab does not trigger a real reload (same-document navigation), so DOM/script state
  carries over stale. Navigate to an unrelated URL first (e.g. a 404) to force a real
  navigation before testing a fresh load.

**Scroll-vs-flip bug (fixed 2026-09-17)**: trying to scroll a page's content was triggering
a page-flip instead — the library captures touch/drag for its own flip gesture, which fights
`overflow-y:auto`. Real fix was what the user asked for: make every page fit with zero
internal scrolling needed, same as real print pagination would. Did three things: (1) grew
the book to 340×580 with tighter page padding/font sizes (`.book-page` block in style.css,
13px body text now, down from 14.5), (2) shrank the two evidence photos further (160px/150px
max-width) and split the two content-heaviest pages — Chapter One and the closing page — each
into two, so no single page is too dense (17 pages total now, was 15), (3) set
`mobileScrollSupport: false` and `disableFlipByClick: true` on the PageFlip config as a second
line of defense (the latter also fixes a real interactivity risk: the library only forwards
clicks to `<a>`/`<button>` children and otherwise treats a page click as "flip," which could
have been swallowing clicks on the div-based flip-card). All per-page height math above was
done by hand (word counts → estimated wrapped lines → estimated px) since there's still no
working browser in this environment to verify actual text wrapping — flagged as the one thing
really worth checking first.

**Ops (2026-09-20)**: app died once because it was only a plain background process. Keeping
it up = install as systemd service (`make install`, needs user's sudo password); then
`~/watchdog` (5-min timer) auto-restarts any enabled-but-down unit in /etc/systemd/system.
Before `make install`, kill any manual process on :5757 or the service can't bind.

**Status (2026-09-17)**: first-pass prototype, running live at http://localhost:5757. Nothing committed to git yet (no git repo initialized in this
dir at all).

**What exists**:
- `app.py` / `db.py` / `config.py` — Flask + SQLite, same shape as `../workout` and
  `../expenses`. Two pages (`/` landing, `/issues/001` sample issue reader) + a working
  `/waitlist` POST endpoint (email regex validated, stored in `mailclub.db`).
- `templates/landing.html` — hero, the 5-pillar "what arrives in the post" grid, the
  philosophy copy (lifted near-verbatim from the brand brief, since it was explicitly written
  for this purpose), waitlist form, envelope teaser linking to the sample issue.
- `templates/issue_001.html` — the Nellie Bly issue as a **real page-flip book** (rebuilt
  2026-09-17, second time — user said the first hand-rolled slide-transition pager "looks
  shit" and asked for actual double-sided pages you flip like a real leaflet). Uses
  **page-flip.js / StPageFlip** (`St.PageFlip`, pinned CDN version 2.0.7 —
  `cdn.jsdelivr.net/npm/page-flip@2.0.7/dist/js/page-flip.browser.js`), a real open-source
  flip-book library (canvas-rendered page curl, works from live HTML elements via
  `loadFromHTML`, not just static images) — not something hand-rolled, since a convincing
  3D page-turn is a genuinely hard rendering problem this library already solves well.
  Sequence: (1) tap-to-open envelope → (2) "unpacking" screen: 4 small line-icon chips
  (Postcard/Place/World/Tea) fade in staggered, next to a closed leaflet cover → (3) tap the
  closed leaflet → it hides and the real StPageFlip book takes over, opening as a spread with
  hard front/back covers (`data-density="hard"`) and 13 soft double-sided pages between them.
  Pages are white (`var(--card)`, the same white used everywhere else), sized ~320×460
  ("stretch" mode with min/max thresholds so it degrades to single-page mode on narrow
  phones automatically — that's the library's own built-in behavior, not something I built).
  Prev/next buttons and arrow keys call `flipPrev()`/`flipNext()`; the page counter listens
  to the library's `flip` event. Deep-linkable via `#pN` (skips straight past the envelope
  and calls `turnToPage()` on init).
  **Caveat: I have no working browser in this environment (Playwright MCP returns
  ECONNREFUSED) so none of this — the animation, the fit of content on each page, whether
  "stretch" sizing behaves — has been visually verified. The logic and API usage were
  checked carefully against the library's README, and the page renders/serves correctly, but
  you are the first real pair of eyes on how it actually looks and flips.**
  Content per page (unchanged from before): cover, dear-reader/portrait, the ritual (tea),
  Ch.1 departure, Ch.2 Bisland reveal, map, world-around-her, newspaper-fever/board-game,
  evidence/photos, last-24-hours, rest-of-her-life, if-you-were-there (flip card), postcard,
  close/paper-trail, back cover (new — echoes the wordmark, links back to the landing page).
- `static/style.css` — first-pass brand: cream paper background, ink-brown text, oxblood
  accent, Fraunces (display) + Source Serif 4 (body) + Special Elite (typewriter/stamp
  labels), from Google Fonts. **This is a draft to react to, not a locked decision** — user
  said we'd walk through branding properly; this is just enough to see the concept live.

**Real images** (added 2026-09-17): loc.gov itself blocks scripted fetches with a Cloudflare
bot challenge (403, `cf-mitigated: challenge`) — didn't try to work around that. Sourced the
same Library-of-Congress-origin public-domain images via Wikimedia Commons instead, which
mirrors them with clean rights tags and no such block:
- Dear-reader page: full-length publicity photo (`Nellie_Bly_in_traveling_cloak.jpg`, PD,
  pre-1931 publication).
- Evidence page: head-and-shoulders portrait, LOC digital ID cph.3c36891, "no known
  restrictions," photographer H.J. Myers c.1890 (`Nellie_Bly_portrait.jpg`).
- Newspaper-fever page: the actual 1890 board game, LOC digital ID ppmsca.02918, "no known
  restrictions," published in the New York World Jan 26 1890
  (`Round_the_world_with_Nellie_Bly_1890.jpg`, served at Wikimedia's 500px thumbnail size —
  the only cached thumb width that worked for this particular file; the original is an 11MB
  scan, way too big to embed directly).
All three hotlink directly to upload.wikimedia.org (standard, expected practice — Commons is
built as a CDN for reuse) with credit lines under each image. A file I found but deliberately
did NOT use: `Nellie_Bly_1889.jpg` — Commons calls it PD in the US, but its own page credits
"© Bettmann/CORBIS," a contested-rights source; skipped rather than risk it.

**Deliberately NOT built yet / stubbed honestly** (per the brief's own rule, "if we don't
know, we don't make it up" — didn't fabricate sources/images/quotes):
- "From Her Own Hand" (primary-source excerpt) is a placeholder note, not an invented quote.
- "The Bag" section (itemized inventory) is skipped entirely — brief explicitly says this
  needs real research from Bly's own account, so nothing was invented for it.
- Bibliography has real source *names* the user gave (NY World 1889-90, Library of Congress)
  but no fabricated catalog numbers/URLs beyond the two digital IDs above.
- No payments/subscription — waitlist email capture only, and it doesn't send a real
  confirmation email yet (see below).
- No collectible "stamp"/passport concept implemented yet (mentioned in brief, not built).

**Original illustrations** (added 2026-09-17, no image-gen tool available in this
environment — hand-authored inline SVG line art instead, which fits the restrained editorial
brand better than a mismatched AI-image style would anyway):
- `static/favicon.svg` + rasterized `favicon.ico` (16/32px, hand-packed via a small Python
  ICO writer — no PIL/cairosvg in this venv, but `rsvg-convert` was available) +
  `icons/icon-{32,180,192,512}.png`, all wired into `base.html` (`rel="icon"` ico+svg+png,
  `rel="apple-touch-icon"`). The SVG-only version wasn't showing for the user — likely a
  browser SVG-favicon quirk or aggressive favicon caching — so this is now the same
  multi-format pattern `../workout` and `../expenses` both already use, which is known to work.
- 4 small line-icon chips for the envelope-unpacking screen (Postcard/Place/World/Tea).
- `.wordmark` in the header (CSS-styled text, not an image) — "History *by* Post," ink-brown
  with the "by" in oxblood italic. This is deliberately just typography per the user's own
  spec ("just history by post written... brown on white"), not a pictorial logo.
- Cover page: a small dotted-route + sailboat flourish between the duration line and the
  page edge.
- The Ritual (tea) page: a line-art teacup with steam and a tag-string teabag.
- Postcard page: a full ink-line illustration (ship's rail, horizon, distant steamer, gulls,
  wave lines) replacing the old placeholder — this is the one spot in the brief that was
  always meant to be original club artwork, not sourced archival material, so there's no
  "real photo" to source here regardless.

**The Tea** (added 2026-09-17): 6th pillar on the landing page + its own leaflet page (data-page
3, "Something to sip on") — one teabag per issue, framed as the founder's personal pick
("from my own shelf of favourites"), no brewing instructions beyond "just brew it."

**Format/cadence copy** (added 2026-09-17): landing page now has a "How it arrives" section —
mailed by real post on the 1st of each month, arrives by the 15th. Deliberate snail-mail,
not email — matches the "By Post" brand promise.

**Waitlist behavior today**: `/waitlist` validates the email format, inserts it into
`mailclub.db`'s `waitlist` table (`ON CONFLICT DO NOTHING`, so duplicates are silently
ignored, not errored), and returns `{ok: true}` — the page then swaps in a static "you're on
the list" message. **No email is actually sent** — there's no SMTP/transactional-email
integration wired up, so subscribers get no confirmation email of their own right now. That's
the natural next piece if/when the user wants it (needs real credentials for something like
Postmark/SES/Resend — not something to wire up with guessed values).

**How to apply next**: don't re-derive the brand brief from scratch if context is lost — see
`GOAL.md` and the original chat (2026-09-17) for the full spec. Next steps are whatever the
user directs after seeing this draft — likely either branding iteration (colors/type/name
treatment) or filling in the stubbed sections once real sourcing is done.
