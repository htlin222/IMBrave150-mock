#!/usr/bin/env python3
"""Add a presenter control bar to a generated asciinema-player page.

asciinema-player 3 takes `speed` as an init option and exposes no way to change
it afterwards — the handle it returns has only play, pause, seek,
getCurrentTime, getDuration and dispose. Its documented `<`/`>` speed keys and
`[`/`]` marker keys do not work in this build either (measured: the bracket keys
seek to times that are not markers, and shift-period does nothing).

So this injects a real control bar and implements speed by disposing the player
and recreating it at the same position with a new speed. Chapters come from the
markers in the .cast and become a dropdown, because clicking a three-pixel dot
on a projector during a talk is not a plan.

    python3 tools/add_player_controls.py cast/talk-full.html cast/talk-full.cast
"""
import json
import pathlib
import re
import sys

SPEEDS = [1, 1.25, 1.5, 2, 3]

CSS = """
<style>
  /* The generated page centres its single child with `html,body{display:flex}`.
     Turning that into a column, and letting the bar stretch across it, keeps
     the player centred while the controls span the full width at the top —
     otherwise the bar becomes a flex item sitting beside the terminal. */
  html, body {
    flex-direction: column !important;
    align-items: center !important;
    justify-content: flex-start !important;
  }
  #talkbar {
    align-self: stretch;
    box-sizing: border-box;
    display: flex; align-items: center; gap: 18px; flex-wrap: wrap;
    padding: 10px 16px; background: #1e1e2e; color: #cdd6f4;
    font: 500 15px/1.4 ui-sans-serif, -apple-system, "Segoe UI", sans-serif;
    border-bottom: 1px solid #313244;
  }
  #talkbar .grp { display: flex; align-items: center; gap: 8px; }
  #talkbar .lbl { color: #7f849c; font-size: 13px; letter-spacing: .06em;
                  text-transform: uppercase; }
  #talkbar button {
    background: #313244; color: #cdd6f4; border: 1px solid #45475a;
    border-radius: 5px; padding: 5px 12px; font: inherit; font-size: 15px;
    cursor: pointer; min-width: 52px;
  }
  #talkbar button:hover { background: #45475a; }
  #talkbar button[aria-pressed="true"] {
    background: #cdd6f4; color: #1e1e2e; border-color: #cdd6f4; font-weight: 600;
  }
  #talkbar select {
    background: #313244; color: #cdd6f4; border: 1px solid #45475a;
    border-radius: 5px; padding: 5px 10px; font: inherit; font-size: 15px;
    max-width: 46vw;
  }
  #talkbar .now { color: #a6adc8; font-variant-numeric: tabular-nums; }
</style>
"""

BAR = """
<div id="talkbar">
  <div class="grp"><span class="lbl">Speed</span><span id="tb-speed"></span></div>
  <div class="grp"><span class="lbl">Chapter</span>
    <select id="tb-chapters"></select>
    <button id="tb-prev" title="previous chapter">&larr;</button>
    <button id="tb-next" title="next chapter">&rarr;</button>
  </div>
  <div class="grp"><button id="tb-play">Pause</button><span class="now" id="tb-now">0:00</span></div>
</div>
"""

JS = """
<script>
(function () {
  var MARKERS = __MARKERS__;
  var SPEEDS = __SPEEDS__;
  var state = { speed: 1, playing: true };
  var el = document.getElementById('player');
  var mk = window.__talkMount;   // (opts) -> player handle
  var player = window.__talkPlayer;

  function fmt(t) {
    t = Math.max(0, Math.floor(t));
    return Math.floor(t / 60) + ':' + String(t % 60).padStart(2, '0');
  }

  // asciinema-player takes speed only at construction, so changing it means
  // rebuilding the player where it stood. Its `startAt` option is ignored on a
  // rebuild (measured: getCurrentTime() comes back 0), so seek explicitly once
  // the new instance is alive, retrying because the first seek can land before
  // the player is ready.
  function remount(speed, at, play) {
    try { player.dispose(); } catch (e) {}
    el.innerHTML = '';
    state.speed = speed;
    player = mk({ speed: speed, autoPlay: false });
    window.__talkPlayer = player;

    var tries = 0;
    (function settle() {
      tries++;
      try { player.seek(at); } catch (e) {}
      var got = 0;
      try { got = player.getCurrentTime() || 0; } catch (e) {}
      if (Math.abs(got - at) > 1.5 && tries < 25) { setTimeout(settle, 80); return; }
      if (play) { try { player.play(); } catch (e) {} }
      paint();
    })();
    paint();
  }

  function currentTime() {
    try { var v = player.getCurrentTime(); return (typeof v === 'number') ? v : 0; }
    catch (e) { return 0; }
  }

  function setSpeed(s) {
    if (s === state.speed) return;
    remount(s, currentTime(), state.playing);
  }

  function jump(t) {
    try { player.seek(t); } catch (e) {}
    if (!state.playing) { try { player.play(); state.playing = true; paint(); } catch (e) {} }
  }

  function chapterIndex(t) {
    var i = 0;
    for (var k = 0; k < MARKERS.length; k++) { if (MARKERS[k].t <= t + 0.4) i = k; }
    return i;
  }

  // --- build the controls -------------------------------------------------
  var sp = document.getElementById('tb-speed');
  SPEEDS.forEach(function (s) {
    var b = document.createElement('button');
    b.textContent = (s % 1 === 0 ? s : s) + '\\u00d7';
    b.dataset.speed = s;
    b.onclick = function () { setSpeed(s); };
    sp.appendChild(b);
  });

  var sel = document.getElementById('tb-chapters');
  MARKERS.forEach(function (m, i) {
    var o = document.createElement('option');
    o.value = i;
    o.textContent = fmt(m.t) + '  ' + m.label;
    sel.appendChild(o);
  });
  sel.onchange = function () { jump(MARKERS[+sel.value].t); };
  document.getElementById('tb-prev').onclick = function () {
    var i = chapterIndex(currentTime() - 2);
    jump(MARKERS[Math.max(0, i - (currentTime() - MARKERS[i].t < 2 ? 1 : 0))].t);
  };
  document.getElementById('tb-next').onclick = function () {
    var i = chapterIndex(currentTime());
    jump(MARKERS[Math.min(MARKERS.length - 1, i + 1)].t);
  };

  var pb = document.getElementById('tb-play');
  pb.onclick = function () {
    try {
      if (state.playing) { player.pause(); state.playing = false; }
      else { player.play(); state.playing = true; }
    } catch (e) {}
    paint();
  };

  function paint() {
    Array.prototype.forEach.call(sp.children, function (b) {
      b.setAttribute('aria-pressed', String(+b.dataset.speed === state.speed));
    });
    pb.textContent = state.playing ? 'Pause' : 'Play';
    var t = currentTime();
    document.getElementById('tb-now').textContent = fmt(t);
    var i = chapterIndex(t);
    if (+sel.value !== i) sel.value = i;
  }

  function bindTime() { }
  setInterval(paint, 500);
  paint();

  // Keys that the player itself does not already use.
  document.addEventListener('keydown', function (e) {
    if (e.target.tagName === 'SELECT') return;
    var i = SPEEDS.indexOf(state.speed);
    if (e.key === '+' || e.key === '=') { setSpeed(SPEEDS[Math.min(SPEEDS.length - 1, i + 1)]); e.preventDefault(); }
    else if (e.key === '-' || e.key === '_') { setSpeed(SPEEDS[Math.max(0, i - 1)]); e.preventDefault(); }
    else if (e.key === 'n') { document.getElementById('tb-next').click(); e.preventDefault(); }
    else if (e.key === 'p') { document.getElementById('tb-prev').click(); e.preventDefault(); }
  });
})();
</script>
"""


def markers_from_cast(cast_path):
    out = []
    for line in cast_path.read_text().splitlines()[1:]:
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if len(ev) >= 3 and ev[1] == "m":
            out.append({"t": round(ev[0], 2), "label": ev[2]})
    return out


def main():
    html = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "cast/talk-full.html")
    cast = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "cast/talk-full.cast")
    if not html.exists():
        sys.exit(f"no page at {html}")
    if not cast.exists():
        sys.exit(f"no recording at {cast}")

    s = html.read_text()
    if "id=\"talkbar\"" in s:
        sys.exit(f"{html.name} already has the control bar; regenerate it first")

    markers = markers_from_cast(cast)
    if not markers:
        sys.exit("the recording has no markers; run tools/add_markers.py first")

    # Wrap the single create() call so the page keeps a handle and can rebuild
    # the player with a different speed.
    pat = re.compile(
        r"AsciinemaPlayer\.create\(\s*(\{data: data\}|\{[^{}]*\}),\s*"
        r"(document\.getElementById\('player'\)),\s*(\{[^{}]*\})\s*\);")
    m = pat.search(s)
    if not m:
        sys.exit("could not find the AsciinemaPlayer.create call to wrap")
    src_arg, el_arg, opts_arg = m.groups()
    boot = (
        f"window.__talkMount = function (extra) {{\n"
        f"    var o = Object.assign({{}}, {opts_arg}, extra || {{}});\n"
        f"    return AsciinemaPlayer.create({src_arg}, {el_arg}, o);\n"
        f"  }};\n"
        f"  window.__talkPlayer = window.__talkMount({{}});")
    s = s[:m.start()] + boot + s[m.end():]

    js = (JS.replace("__MARKERS__", json.dumps(markers))
            .replace("__SPEEDS__", json.dumps(SPEEDS)))
    s = s.replace("</head>", CSS + "</head>", 1)
    s = s.replace("<body>", "<body>" + BAR, 1)
    if "<body>" not in html.read_text():          # some templates omit <body>
        s = s.replace(CSS + "</head>", CSS + "</head>", 1)
    s = s.replace("</body>", js + "</body>", 1)

    html.write_text(s)
    print(f"{html.name}: speed control ({', '.join(str(x) + 'x' for x in SPEEDS)}) "
          f"and {len(markers)} chapters")


if __name__ == "__main__":
    main()
