# stage/ — what to put in place before the talk

Slide 9 of the talk runs `Mission 7.1`: four review subagents, in parallel, on a
manuscript. They need a manuscript to review, and producing one is Chapter 06 of
`live-demo/`, which on its own takes longer than the entire talk.

`live-demo/workspace/` is deliberately git-ignored — it is the sandbox the demo
writes into, and it starts empty on every clone. So the manuscript produced by
the recorded run is kept here instead, tracked, and copied into place before you
present.

```bash
./slides/stage/stage.sh
```

That puts `manuscript.md` into `live-demo/workspace/manuscript/` so the four
reviewers run standalone in about two minutes.

`manuscript.md` is the output of the recorded run: every number in it came from
`live-demo/workspace/` and matches the figures printed on the slides.
`review_log.csv` is the triage of the four reviews from that run — useful if
someone asks what the reviewers actually found. Three of their findings were
real defects and were fixed.
