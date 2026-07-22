# How I do real-world data analysis with Claude Code — presentation deck

**Presenter:** 林協霆 (Hsieh-Ting Lin) · 和信治癌中心腫瘤內科部 (Department of Oncology, Koo Foundation Sun Yat-Sen Cancer Center)

A fullscreen, self-contained HTML slide deck (~60 min) that walks an audience
through a complete real-world analysis of the synthetic **IMbrave150** cohort:
data aggregation → propensity-score matching → survival → subgroups →
robustness → IMRaD manuscript. Each analysis chapter replays as an **animated
Claude Code session** (the prompt types in, the window zooms, real tool calls
and console output appear, then the real figure is revealed).

> Every number and console block in the deck is **verbatim** from a real run of
> this repo's scripts, and every figure is the real SVG that run produced. The
> pipeline was executed end-to-end first (a subagent), then curated into this
> demo — *fidelity first, polish second*.

## Run it

```bash
open -a "Google Chrome" claude-demo/index.html
```

No server, no build, no network. Then press **F** for fullscreen and **→** to go.

## Controls

On a **session** scene the first **→** types the prompt into the composer (the
window zooms), then it *sends*: the prompt rises into a user bubble, the agent
**thinks** (shimmer → "Thought for Ns"), and the response **auto-plays** — each
tool row appears as **Running…** and resolves to **Ran** with its output, a
"Working…" line ticks at the bottom and finishes as "Done". You can just let it
run, or press **→** to push the next beat immediately.

| Key | Action |
|-----|--------|
| **→ / Space** | Type/send the prompt · push the next beat · then next scene |
| **←** | Restart the current scene / previous scene |
| **↑ / ↓** | Jump a whole scene |
| **S** | **Presenter mode** — dark notes pane with speaker cues, a running clock, per-beat prompts, and "up next" |
| **O** | Overview grid (click a thumbnail to jump) |
| **F** | Fullscreen · **C** chapter dots · **Home/End** first/last · **?** shortcuts |

Present on two screens: mirror to the projector, press **S** on your laptop to
keep the notes + clock on your side.

### URL helpers (rehearsal)

- `index.html#8` — deep-link straight to scene 8.
- `index.html?reveal#6` — open a scene with **all** beats already revealed (preview/print).
- `index.html?speaker` — open with presenter mode on.

## Structure (17 scenes, 6 acts)

1. Title · 2. The question + pipeline map
3. Act I — the three EHR dialects · 4. **Session:** harmonise & pool (N=1800)
5. Act II — why the naive HR lies (0.505) · 6. **Session:** PSM → 706 pairs, matched HR 0.578
7. Act III — why Kaplan–Meier · 8. **Session:** KM/Cox → OS HR 0.58 (= the real trial)
9. **Session:** subgroup forest · 10. **Session:** 120-spec multiverse + TMLE
11. Act VI writing workflow · 12–14. **Sessions:** Methods ← scripts, Results ← logs, Discussion ← evidence
15. The assembled IMRaD manuscript · 16. What made it trustworthy · 17. Reproduce / thanks

## Files

```
claude-demo/
  index.html            the deck shell (loads the two assets below)
  assets/
    studio.css          Claude Code UI design tokens (from claude-demo-studio)
    deck.css            slide framework + clay presentation theme
    deck.js             step-through engine, presenter mode, overview
    storyboard.js       ALL content — every scene, prompt, console block, note
  figures/              real SVG/PNG figures from the pipeline run
```

To edit content, open `assets/storyboard.js` — each scene is one `scenes.push({…})`
with `html` (the slide) and `notes` (speaker cues). To re-skin, edit the `:root`
tokens in `deck.css` / `studio.css`.

## Honesty note

The data are **100% synthetic**, modelled on Finn RS et al., *NEJM*
2020;382:1894. Nothing here is evidence about atezolizumab–bevacizumab or
sorafenib; it is a teaching demonstration of analysis *method* and *workflow*.
