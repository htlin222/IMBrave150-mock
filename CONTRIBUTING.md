# Contributing

This is a teaching repository. Its value is that the numbers in it are true of
the data in it, and that anyone can check that — so the bar for a change is
whether it keeps that property.

## Before anything else

```bash
make setup                                            # uv venv + pinned deps
cd live-demo && ../.venv/bin/python verify/preflight.py --full
```

`preflight.py` deliberately triggers the known breakages up front. Green means
the environment matches the one everything here was measured on.

## The three rules that are not negotiable

**1 · No number that was not produced by a run.**
Every figure in the missions, the acceptance scripts, the slides and the
manuscript came out of an actual execution. If you change something that moves
a number, re-run it and update every place it appears — the acceptance scripts
are the record of what the correct answer is, so they change first.

**2 · No citation from memory.**
Every reference must be found by search and then verified against Crossref:
DOI plus six bibliographic fields. A DOI that looks plausible is not a DOI.
This is enforced in Mission 6.8 and it applies to the prose too.

**3 · Never commit `.env`.**
It holds a live Cloudflare API token. It is git-ignored by this repository's
own `.gitignore` (a global one does not travel with a clone), and worth
checking before every push:

```bash
git diff --cached --name-only | grep -qx '.env' && echo "STOP" || echo ok
```

Use `.env.example` for anything anyone else needs to know.

## Do not hand-edit the generated files

| File | Regenerate with |
|---|---|
| `docs/PROMPTS.md` | `python3 scripts/extract_prompts.py` |
| `docs/FILE-TREE.md` | `python3 scripts/gen_file_tree.py` |
| `live-demo/reference-run/` | `python3 scripts/make_reference_run.py` |

CI fails if the first two are stale. To change a prompt, edit
`slides/tools/record_*.sh` — that is the file that actually ran, so it is the
only honest source. To annotate a new file, add it to `NOTES` in
`gen_file_tree.py`.

## Changing the pinned dependencies

Don't, without reading the comment at the top of `requirements.txt` first. The
combination `lifelines==0.30.0` + `numpy==2.5.1` makes
`lifelines.plotting.add_at_risk_counts()` raise `TypeError`, and Mission 3.2 is
written around that: the mission teaches the manual at-risk table. Relaxing the
pin makes the function work again and quietly deletes the lesson.

## Changing a mission

Each mission is a contract: it names its output files and columns, and
`live-demo/verify/chNN.py` looks for exactly those names. If you rename an
output, the acceptance script changes in the same commit or the mission is
broken for everyone.

Keep the `⛔ 硬性約束` blocks. Every entry in them is something that has
actually failed on stage, and the cost of rediscovering one live is high.

## Changing the slides

```bash
make -C slides pdf
```

That builds all three decks, rasterises them, and fails if any slide
overflowed — Marp clips a too-full slide silently, so this check is the only
thing standing between a late edit and a truncated sentence on a projector.

## Changing the recordings

`slides/tools/record_walkthrough.sh` drives a real nested agent session and
takes as long as the recording. The header comment lists the things that cost
a take to learn (dedicated tmux sockets, absolute path to the agent binary,
prompt text and Enter as separate sends). Read it before editing.

If you change the prompt list, regenerate `docs/PROMPTS.md`.

## Language

Code, commit messages and the slides are in English. `live-demo/`, the
runbook and the rehearsal script are in Chinese, because that is the room
they were written for. Keep each file in the language it is already in.

## Reporting a run that did not reproduce

That is the most useful issue you can file. Include:

- which route (guided / walkthrough / reference scripts) and which mission;
- the acceptance script output, verbatim;
- your `pip freeze` and OS;
- the numbers you got, next to the ones in
  [`live-demo/reference-run/`](live-demo/reference-run/).

An agent-driven run legitimately varies — see that folder for how much. What
should never vary is the *direction*: unadjusted lower than matched, matched
near 0.58, no specification crossing 1.0.
