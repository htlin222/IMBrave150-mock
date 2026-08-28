# slides/ — *Mission by Mission*

The conference deck for this repository: driving an AI coding agent, **live**,
from ten messy hospital exports to a result you can audit.

The talk is built around a live demo, so the slides are signposts, not the
content. Each signpost says what the next demo segment does, prints the prompt
verbatim so the audience can read along, and names the number to watch for.

**Hsieh-Ting Lin, MD (林協霆)** · Department of Medical Oncology (腫瘤內科部),
Koo Foundation Sun Yat-Sen Cancer Center (和信治癌中心醫院).

> ⚠️ Every figure in the deck comes from the synthetic cohort in this repo.
> No real patient is represented, and nothing in it is evidence about
> atezolizumab, bevacizumab or sorafenib.

## Links

**The terminal recording is the deliverable.** The PDFs exist to be presented
around it; the bundle exists so it can be given offline. Everything else is the
machinery that produced it.

| | |
|---|---|
| **<https://imbrave150-talk.pages.dev/talk>** | **The walkthrough — 33 min, 22 at 1.5×.** This is the talk. |
| <https://imbrave150-talk.pages.dev/talk-long> | The long version, 64 min, with the methodological arguments in it |
| <https://imbrave150-talk.pages.dev/> | Landing page |
| <https://imbrave150-talk.pages.dev/deck.pdf> | The 12-slide deck |
| <https://imbrave150-talk.pages.dev/deck-reference.pdf> | 43-slide reference edition |
| <https://imbrave150-talk.pages.dev/deck-backup.pdf> | Deck with recorded frames, for presenting without a browser |
| [Releases](https://github.com/htlin222/IMBrave150-mock/releases) | `imbrave150-slides-*.zip` — everything, offline |

Local equivalents: `cast/walk.html`, `cast/talk-full.html`, `dist/*.pdf`.

Not published, and not in the bundle's public half: `SCRIPT.md` and
`SPEAKER-NOTES.md`. Those are the presenter's lines.

---

## Files

| Path | What it is |
|---|---|
| `deck.md` | **The talk. 12 slides.** Edit this one. |
| `deck-backup.md` | Generated from `deck.md` — the same slides with a still frame from a real recorded agent session after each signpost, for when the live demo will not cooperate. Do not hand-edit; regenerate. |
| `deck-full.md` | Reference edition, 43 slides, for reading after the talk. |
| `cast/walk.html` | **The recording that gets presented.** 32:55, or 22 min at the default 1.5x. Data, cleaning, exploring, analysis, writing — plain prompts, no detours. |
| `SCRIPT.md` | **The rehearsal script.** Every word, in Chinese, with stage directions. Reads to length. |
| `SPEAKER-NOTES.md` | The same talk as notes rather than verbatim, if you would rather not read from a script. |
| `tools/script_timing.py` | Measures how long the script takes, counting the pauses its directions ask for. |
| `cast/talk-full.html` | The hour-long version, with the methodological arguments in it. For questions and for handing out. |
| `cast/talk-markers.tsv` | Every slide, shell command and prompt, with the time it happened. |
| `cast/RUNNING-ORDER.md` | **Read this before you present.** Three routes through the recording, and where to pause. |
| `tools/add_player_controls.py` | Injects the speed buttons and chapter dropdown into the generated player. |
| `walkthrough/` | The presenterm cards shown inside the walkthrough. |
| `talk/` | The cards for the long version. |
| `tools/trim_cast.py` | Cuts dead air off the front of a recording, carrying markers with it. |
| `cast/talk.cast` | The earlier short version: five prompts, no slides, 8 min. |
| `img/` | One still frame per signpost, cut from the per-segment recordings. |
| `recordings/` | The five `.mp4` sessions the frames came from. |
| `tools/record_segments.sh` | Records the five segments as real Claude Code sessions and cuts the frames. |
| `tools/make_backup_deck.py` | Builds `deck-backup.md` from `deck.md` + `img/`. |
| `theme.css` | `mono-academic`: the black-and-white theme, plus the Lucide icons as inline data-URI masks. |
| `.marprc.yml` | Render settings shared by `make` and CI, so the released PDFs match your preview. |
| `tools/check_overflow.py` | Fails the build if any slide is clipped. |
| `dist/` | Build output. Git-ignored. |

## The talk, in 12 slides

```
 1  Title
 2  Disclaimer and conflict of interest
 3  What an agent is, and is not          ← for an audience that has never used one
 4  The difference one sentence makes     ← bad prompt vs good prompt, side by side
 5  ▶ Ten hospitals, three dialects       → live
 6  ▶ The unadjusted answer is lying      → live
 7  ▶ Make the two arms comparable        → live
 8  ▶ Try to break your own result        → live
 9  ▶ Let it review its own manuscript    → live
10  The whole path, on one slide
11  Four habits worth stealing
12  Thank you
```

Every signpost has the same four parts: a plain-English title, **What this step
does**, **What I will type** (the prompt, verbatim), and **What to watch**.

### Before you present

Slide 9 runs `Mission 7.1`, which needs a manuscript to review. Chapter 06
takes longer than the whole talk, so stage it beforehand — with
`live-demo/workspace/manuscript/manuscript.md` already in place, the four
reviewers run standalone in about two minutes.

The prompts on the slides are in English, so type them in English on the day;
otherwise the audience cannot follow along on the screen.

## Build

```bash
make          # all three PDFs into dist/
make talk     # just dist/imbrave150-deck.pdf, while you are editing
make check    # build, rasterise every slide, assert nothing is clipped
make html     # a self-contained HTML deck, for presenting without a viewer
make watch    # live preview while editing
```

`make` shells out to `npx @marp-team/marp-cli@4.0.0`, pinned to the version CI
uses. Set `MARP=marp` to use a locally installed binary instead.

Marp drives a headless Chrome. On macOS the Homebrew `chromium` formula is
frequently a dangling symlink into a `Chromium.app` that was never installed —
the Makefile therefore prefers a real `Google Chrome.app`. Override with
`CHROME_PATH=…` if yours lives elsewhere.

## Design rules

These are enforced by `theme.css` and are not stylistic preferences to be
tidied away later:

- **No decorative header or footer.** The footer band carries an AMA-style
  citation and nothing else, and only on slides that actually cite something.
- **Black and white only.** Emphasis comes from weight, size and whitespace.
  There is no colour anywhere, including links.
- **18px floor.** The citation footer is the smallest text in the deck at
  18px; nothing may go below it.
- **`#` is a section divider, `##` is a slide title.** A slide holding only an
  `h1` is a part opener.
- **At most ten lines of content per slide.**
- Slides are 1280×720, so every `px` in the theme is a real pixel in the PDF.

## Writing a signpost

```markdown
## Make the Two Arms Comparable

- <span class="ic ic-scale"></span> **What this step does**
  - one plain sentence, no jargon

> the prompt, exactly as it will be typed on the day

- <span class="ic ic-eye"></span> **What to watch**
  - the number, and what it means if it is large or small

<!-- _footer: "live-demo · Missions 2.3–3.1　·　<sup>1</sup> Finn RS, et al. <em>N Engl J Med</em>. 2020;382(20):1894-1905. doi:10.1056/NEJMoa1915745" -->
```

The `live-demo · Mission N.N` tag in the footer is deliberately small: the
audience does not need it, and anyone who wants to rerun the step does.

Icons are Lucide (ISC licence), inlined in `theme.css` as `mask-image` data
URIs so the PDF has no network dependency. Available: `ic-database`,
`ic-search`, `ic-merge`, `ic-scale`, `ic-activity`, `ic-shuffle`, `ic-file`,
`ic-users`, `ic-package`, `ic-terminal`, `ic-message`, `ic-check`, `ic-alert`,
`ic-pause`, `ic-git`, `ic-target`, `ic-book`, `ic-flask`, `ic-refresh`,
`ic-eye`.

Slide classes, applied with `<!-- _class: … -->`: `title`, `section`,
`statement`, `dense` (one notch smaller, for a legitimately full slide),
`refs` (bibliography leading), `cols` (two columns).

## The recorded talk

Everything is inside one terminal recording: the slides (presenterm), the raw
data (bat), and the agent working. The agent runs in one tmux window for the
whole hour, so its context never resets; the slides run in a second window and
the recording is a client attached to that session, which is why switching
between them is just terminal output.

Play to the next marker, pause, talk, carry on. The page carries a control bar —
speed (1× to 3×), a chapter dropdown, play/pause, fullscreen — and three things
built for a projector:

- **A chapter side pane** (`☰`, or `c`). Every chapter listed, the current one
  highlighted, click to jump. The page shifts left so it never covers the
  terminal. Fullscreen (`f`) expands the whole page rather than just the
  terminal, so the pane survives it — the player's own fullscreen button does
  not.
- **Click anywhere to pause.** A drag is treated as a selection, not a click,
  so this does not fight the next one.
- **Select text, then "放大文字".** A popover appears above the selection; the
  chosen lines fill the window at the largest size that fits, binary-searched
  against the viewport. `Esc` or `×` returns. This is for the back row.

**It opens at 1.5×, where the recording runs 42:45** — the slot it was built
for, with no cutting. At 1× it is 64:08.

asciinema-player takes `speed` only at construction and exposes no setter — its
handle has just play, pause, seek, getCurrentTime, getDuration and dispose — and
its documented `<`/`>` and `[`/`]` shortcuts do nothing in this build (measured:
the bracket keys seek to times that are not markers). So the bar implements
speed by rebuilding the player at the same position, and `make cast-html` always
runs the injector after the generator; a page regenerated without it looks fine
and silently has no speed control, which the bundle script now checks for.

```bash
make walk        # re-record the walkthrough (~33 min; needs a logged-in claude)
make talk        # re-record the long version (~65 min)
make cast-html   # rebuild the players from the existing recordings
```

Two recordings, from the same repository and the same data.

**`walk.cast` — the one you present.** Five stages in a straight line: data,
cleaning, exploring, analysis, writing. Fourteen turns, twenty-two markers,
32:55 — 22 minutes at the default 1.5×. The prompts are deliberately plain,
the kind anyone would type. There are no methodological arguments in it and no
staged failures: the audience has never seen a terminal, and what is being
taught is the shape of the work.

**`talk-full.cast` — the long version.** The same study with the arguments
kept in: what happens when a prompt is ambiguous, 120 analytic paths, four
reviewers. Eighteen turns, thirty markers, 64 minutes. Hand it out; play from
it if a question needs it. `cast/RUNNING-ORDER.md` has a 20-minute route, a 45-minute route,
and the four moments worth stopping on. The prompts are
deliberately open — *"tell me what you notice"* rather than *"do X"* — so the
slides never print a result and the agent's own reasoning is the content. One
segment is a real failure and its recovery: the matching prompt does not say
which direction to sort, the agent picks one, and the follow-up asks what
happens if you pick the other.

It is a `.cast`, not a video, and that buys three things:

- **Small.** 792 KB for 7 min 39 s of session, or 1.3 MB for the fully offline
  player with the font and the recording embedded. The five per-segment MP4s in
  `recordings/` are 12 MB for the same material.
- **Real text.** asciinema-player draws the glyphs as DOM text, so you can
  select and copy any command or number straight off the projected screen.
  (This holds for the `--player` output only; converting the cast to GIF or MP4
  gives you pixels.)
- **Chapters.** `tools/record_cast.sh` logs the wall-clock time of every prompt
  and `tools/add_markers.py` splices those in as markers, so the player's
  timeline has one jump point per step:

  | | | |
  |---|---|---|
  | 00:07 | 1 | Ten hospitals, three dialects |
  | 02:35 | 2 | The unadjusted answer is lying |
  | 03:34 | 3 | Make the two arms comparable |
  | 04:56 | 4 | Try to break your own result |
  | 06:51 | 5 | Let it review its own manuscript |

The terminal is **105 columns** on purpose. The player scales the grid to its
container, so a narrower terminal means bigger glyphs on a projector; 105 is
about as narrow as Claude Code's tables render cleanly.

One continuous session is also much faster than five separate ones — 7½ minutes
against roughly 45, because the context carries over and the agent does not have
to rediscover the data at every step.

### Two things that will waste your evening

- **Run tmux on a dedicated socket** (`tmux -L`). A long-lived tmux server hands
  the nested session the environment it was started with, which may be months
  old. The symptom is `Login expired · Please run /login` inside the TUI while
  `claude -p` works fine from the same shell. `record_cast.sh` does this.
- **Send the prompt text and Enter as two separate `send-keys`**, about a second
  apart, or the composer reads the burst as a paste and swallows the submit.

## Recording the backup deck

```bash
./tools/record_segments.sh        # all five, ~45 min; or pass 1..5 for one
python3 tools/make_backup_deck.py
make check
```

Each segment runs as a real Claude Code session under VHS, gets the slide's own
prompt typed into it, and does the work for real. Three things this cost an
hour each to learn, all encoded in the script:

- **Record one segment at a time.** Four concurrent runs drove load average past
  70; Claude Code's startup then outran the tape's startup wait and every tape
  died on `Wait+Screen /shift\+tab/` with the command typed and no TUI on
  screen. It is starvation, not a port clash — VHS gives each `ttyd` a random
  port. A longer wait would let you parallelise, but four nested agents on one
  laptop finish later than four in sequence.
- **Use an absolute path to `claude`.** Inside tmux or ttyd, `PATH` may resolve
  to an older build, which gets SIGKILLed in a nested session.
- **Dismiss the first-run dialogs by hand first.** A fresh install shows *"Try
  the new fullscreen renderer?"*, which hides the composer footer VHS waits on.
  The tape then hangs until timeout, showing nothing useful.

## Numbers

Every figure quoted on a slide came from a recorded run of the `live-demo/`
pipeline in this repository, not from the course notes. If you rerun the
pipeline and a number moves, the slide is wrong, not the run.

### Which numbers actually reproduce

Recording the demo with independent agent sessions showed that not every figure
is stable, and the slides now quote only the ones that are:

| Figure | Reproduces? |
|---|---|
| Cohort counts, albumin/bilirubin medians | Yes, exactly |
| Unadjusted HR 0.505 and its CI | Yes, exactly |
| Baseline SMDs | Yes, exactly |
| Caliper 0.114, 706 pairs, 256 unmatched | Yes — **but only if the prompt says `ascending`** |
| Multiverse median ≈ 0.58, and nothing crossing 1.0 | Yes |
| Multiverse *range* and *% inside 0.55–0.61* | **No** — moves with implementation choices |

The matching one is the sharpest lesson. An earlier version of the slide said
only *"sort treated by the score before matching"*. A recorded session read that
as descending and returned **765 pairs, 20.5% unmatched** instead of 706 and
26.6% — the same number the statistical reviewer had predicted from the same
ambiguity. Greedy matching is order-dependent; the direction has to be stated,
and the slide now states it.

## Citations

Every reference in the deck was checked against the Crossref REST API —
journal, volume, pages and year — before it was typeset. If you add one, do
the same:

```bash
curl -s -A "your-name (mailto:you@example.org)" \
  https://api.crossref.org/works/10.1056/NEJMoa1915745 | jq .message.title
```

Reference numbers appear in three places and must agree: the superscript in
the body (`<span class="ref">n</span>`), the `<sup>n</sup>` in that slide's
`_footer`, and the numbered list on the References slides. The continued
References slide starts at 6, which `theme.css` maps with an
`ol[start="6"]` counter rule — renumber both if you insert a reference.

## Online, as a fallback

<https://imbrave150-talk.pages.dev> — the walkthrough, the long version and the
three PDFs, served from Cloudflare Pages. If the laptop or the browser fails on
the day, this is the URL to open.

```bash
./slides/tools/deploy_site.sh   # build the site and push it, from .env
```

Pushing anything under `slides/` to `main` redeploys it
(`.github/workflows/deploy-talk.yml`), which builds the PDFs on the runner —
the recordings are committed, the PDFs are not.

The speaker script and notes are deliberately **not** published. They are the
presenter's own lines, not part of the demo.

## The presenter bundle

```bash
./scripts/make-slides-bundle.sh v2.2.0
```

One zip — 4.6 MB — with the running order, the recording as a self-contained
offline player, and all three PDFs. That is everything needed to give the talk
on a machine with no clone, no network and no toolchain. The script asserts the
PDFs and the player exist before packing, then unpacks the finished zip and
checks the files are really in it, because a bundle that turns out to be empty
is discovered at the worst possible moment.

## CI/CD

`.github/workflows/slides.yml`:

- **push to `main`** → rebuild all three PDFs, verify no slide overflows, upload
  them as a workflow artifact.
- **push a tag `slides-v*`** → the same, then publish a GitHub Release with the
  presenter bundle and all three PDFs attached.

```bash
git tag slides-v1.0.0 && git push origin slides-v1.0.0
```
