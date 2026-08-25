# slides/ — *Mission by Mission*

The conference deck for this repository: driving an AI coding agent
end-to-end, from ten messy hospital exports to a typeset, machine-audited
manuscript.

**Hsieh-Ting Lin, MD (林協霆)** · Department of Medical Oncology (腫瘤內科部),
Koo Foundation Sun Yat-Sen Cancer Center (和信治癌中心醫院).

> ⚠️ Every figure in the deck comes from the synthetic cohort in this repo.
> No real patient is represented, and nothing in it is evidence about
> atezolizumab, bevacizumab or sorafenib.

## Files

| Path | What it is |
|---|---|
| `deck.md` | The deck. Marp markdown — **this is the only file you edit for content.** |
| `theme.css` | `mono-academic`: the black-and-white theme, plus the Lucide icons as inline data-URI masks. |
| `.marprc.yml` | Render settings shared by `make` and CI, so the released PDF matches your preview. |
| `tools/check_overflow.py` | Fails the build if any slide is clipped. |
| `dist/` | Build output. Git-ignored. |

## Build

```bash
make          # → dist/imbrave150-mission-by-mission.pdf
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
- **At most ten lines of content per slide.** Two top-level bullets —
  *Current step* and *Good prompt* — with their nested detail beneath.
- Slides are 1280×720, so every `px` in the theme is a real pixel in the PDF.

## Writing a slide

The recurring shape, which the whole deck is built from:

```markdown
## Mission 2.3 — Propensity-Score Matching

- <span class="ic ic-scale"></span> **Current step**
  - what the agent is being asked to do, right now
- <span class="ic ic-message"></span> **Good prompt**
  - why that wording, and what a bad one would cost

> the prompt itself, verbatim

<!-- _footer: "<sup>2</sup> Austin PC. … <em>Multivariate Behav Res</em>. 2011;46(3):399-424. doi:10.1080/00273171.2011.568786" -->
```

Icons are Lucide (ISC licence), inlined in `theme.css` as `mask-image` data
URIs so the PDF has no network dependency. Available: `ic-database`,
`ic-search`, `ic-merge`, `ic-scale`, `ic-activity`, `ic-shuffle`, `ic-file`,
`ic-users`, `ic-package`, `ic-terminal`, `ic-message`, `ic-check`, `ic-alert`,
`ic-pause`, `ic-git`, `ic-target`, `ic-book`, `ic-flask`, `ic-refresh`,
`ic-eye`.

Slide classes, applied with `<!-- _class: … -->`: `title`, `section`,
`statement`, `dense` (one notch smaller, for a legitimately full slide),
`refs` (bibliography leading), `cols` (two columns).

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

- **push to `main`** → rebuild the PDF, verify no slide overflows, upload it as
  a workflow artifact.
- **push a tag `slides-v*`** → the same, then publish a GitHub Release with the
  PDF attached.

```bash
git tag slides-v1.0.0 && git push origin slides-v1.0.0
```
