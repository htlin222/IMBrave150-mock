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

## Files

| Path | What it is |
|---|---|
| `deck.md` | **The talk. 12 slides.** Edit this one. |
| `deck-backup.md` | Generated from `deck.md` — the same slides with a still frame from a real recorded agent session after each signpost, for when the live demo will not cooperate. Do not hand-edit; regenerate. |
| `deck-full.md` | Reference edition, 43 slides, for reading after the talk. |
| `img/` | One still frame per signpost, cut from the recordings. |
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

## Recording the backup deck

```bash
./tools/record_segments.sh        # all five, ~45 min; or pass 1..5 for one
python3 tools/make_backup_deck.py
make check
```

Each segment runs as a real Claude Code session under VHS, gets the slide's own
prompt typed into it, and does the work for real. Three things this cost an
hour each to learn, all encoded in the script:

- **VHS cannot run in parallel.** Its `ttyd` binds a fixed port (7681), so a
  second concurrent instance silently gets no terminal and the tape dies on the
  startup wait with an unhelpful error.
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

## CI/CD

`.github/workflows/slides.yml`:

- **push to `main`** → rebuild all three PDFs, verify no slide overflows, upload
  them as a workflow artifact.
- **push a tag `slides-v*`** → the same, then publish a GitHub Release with all
  three PDFs attached.

```bash
git tag slides-v1.0.0 && git push origin slides-v1.0.0
```
