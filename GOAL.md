# History by Post

Paid monthly mail-club: one true historical story a month, delivered as a small physical
package (booklet, fold-out map, archival photo sheet, postcard, collectible stamp). This repo
is the webapp — first job is to make the *concept* real on screen so Dhruv can see it, react,
and iterate before any physical production happens. Not a history-education product — a
"tiny historical artefact" people collect. The retention hook is the collection itself
(subscribers keep a box of issues), not the individual month's topic.

## Brand rules (don't drift from these)

- Tone: curious, intimate, cinematic, slightly mysterious. Never academic/listy, never
  sensationalized. Opens in medias res ("Bombay, 1944. At 7:15 on a Tuesday morning...").
- Every issue opens with the same ritual: Issue No. / Place / Year / Subject header, then
  "Dear reader... This really happened." before the story starts.
- **"If we don't know, we don't make it up."** — sources and images must be real/sourced or
  clearly marked as placeholder. Never fabricate an archival citation, image, or quote.
- Every issue = same 5 pillars: The Story, The Place, The Evidence (archival material), The
  World Around Them (era context), The Postcard (collectible takeaway).

## Issue 001: Nellie Bly (1889–90, 72-day trip around the world)

Chosen as the inaugural/demo issue because it has everything: a vivid real person, travel,
rivalry (Elizabeth Bisland racing her the other direction), newspaper-culture spectacle, real
primary sources, photographs, a map-able journey, and a life that continues past the "big
moment" (she later became an industrialist — patented a steel oil drum design).

Full section-by-section spec for the physical package is in the chat history that started
this project (2026-09-17) — not duplicated here since it's long; HANDOFF.md tracks which
sections have been built into the web reader and in what fidelity (placeholder vs sourced
imagery). Physical-only pieces (the actual printed stamp/postcard/belly band) aren't a web
concern — the web reader's job is to evoke the same experience on screen, not replicate paper
constraints.

## Stack

Matches Dhruv's other personal apps (`../workout`, `../expenses`): Flask + Jinja templates +
vanilla JS + SQLite, deployed as a systemd service via `make install`/`make restart`. No
payments/auth yet — this phase is concept + landing + waitlist capture only.
