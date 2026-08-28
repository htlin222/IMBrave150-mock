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
# 1.5x is the default: the whole 64-minute recording plays in 42:45, which is
# the slot it was built for, and nothing on screen becomes hard to read.
DEFAULT_SPEED = 1.5

CSS = """
<style>
  /* The generated page centres its single child with `html,body{display:flex}`.
     Turning that into a column, and letting the bar stretch across it, keeps
     the player centred while the controls span the full width at the top. */
  html, body {
    flex-direction: column !important;
    align-items: center !important;
    justify-content: flex-start !important;
  }
  body { background: #16161e; }

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
  #talkbar .sp { margin-left: auto; }
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
    max-width: 34vw;
  }
  #talkbar .now { color: #a6adc8; font-variant-numeric: tabular-nums;
                  min-width: 3.4em; }

  /* --- chapter side pane -------------------------------------------------
     The dropdown is fine at desk size, but on a projector — and especially in
     fullscreen, where a <select> popup renders unpredictably — a standing list
     is easier to hit and lets the room see where you are. */
  #talkpane {
    position: fixed; top: 0; right: 0; bottom: 0; width: 340px; z-index: 40;
    background: #1e1e2e; border-left: 1px solid #313244;
    color: #cdd6f4; font: 15px/1.45 ui-sans-serif, -apple-system, sans-serif;
    overflow-y: auto; transform: translateX(100%);
    transition: transform .18s ease-out;
    padding: 14px 0 24px;
  }
  #talkpane.open { transform: none; }
  #talkpane h3 {
    margin: 0 0 10px; padding: 0 18px; font-size: 13px; font-weight: 600;
    letter-spacing: .08em; text-transform: uppercase; color: #7f849c;
  }
  #talkpane .ch {
    display: flex; gap: 12px; padding: 8px 18px; cursor: pointer;
    border-left: 3px solid transparent;
  }
  #talkpane .ch:hover { background: #313244; }
  #talkpane .ch.on { background: #313244; border-left-color: #cdd6f4;
                     font-weight: 600; }
  #talkpane .ch.stage { color: #f9e2af; }
  #talkpane .ch .t { color: #7f849c; font-variant-numeric: tabular-nums;
                     min-width: 3.6em; }
  /* Opening the pane must not cover the right edge of the terminal, so shift
     the whole centred column left by the pane's width while it is open. */
  body { transition: padding-right .18s ease-out; }
  body.pane-open { padding-right: 340px; }

  /* --- fullscreen --------------------------------------------------------
     The generated page pins the player at min(94vw, 1100px), so going
     fullscreen made the window bigger and left the terminal exactly the size
     it already was. In fullscreen it should be the largest 16:9 box that fits
     under the bar — and narrower again when the chapter pane is out.
     A body class rather than :fullscreen alone, so the same rules apply
     whichever vendor prefix the browser reports. */
  body.fs { padding: 0; }
  body.fs #talkbar { border-bottom-color: #45475a; }
  body.fs #player {
    width: min(100vw, (100vh - 56px) * 16 / 9) !important;
    max-width: 100vw !important;
    border-radius: 0;
  }
  body.fs.pane-open #player {
    width: min(calc(100vw - 340px), (100vh - 56px) * 16 / 9) !important;
  }

  /* --- selection popover and the zoom overlay ----------------------------
     Terminal text is small on a projector. Select a line, blow it up. */
  #talkpop {
    position: fixed; z-index: 60; display: none;
    background: #cdd6f4; color: #1e1e2e; border-radius: 6px;
    padding: 7px 14px; font: 600 15px/1 ui-sans-serif, -apple-system, sans-serif;
    cursor: pointer; box-shadow: 0 4px 14px rgba(0,0,0,.45);
    white-space: nowrap;
  }
  #talkpop:after {
    content: ""; position: absolute; left: 50%; bottom: -6px; margin-left: -6px;
    border: 6px solid transparent; border-top-color: #cdd6f4; border-bottom: 0;
  }
  #talkzoom {
    position: fixed; inset: 0; z-index: 70; display: none;
    background: #11111b; padding: 3vh 3vw 8vh;
    align-items: center; justify-content: center;
  }
  #talkzoom.open { display: flex; }
  #talkzoom pre {
    margin: 0; color: #e6e6e6; white-space: pre-wrap; word-break: break-word;
    font-family: "Cascadia Code", "Source Code Pro", Menlo, Consolas, monospace;
    line-height: 1.35; text-align: left; max-width: 100%; max-height: 100%;
  }
  #talkzoom .close {
    position: absolute; top: 18px; right: 22px; z-index: 71;
    background: #313244; color: #cdd6f4; border: 1px solid #45475a;
    border-radius: 6px; padding: 8px 16px; cursor: pointer;
    font: 600 16px ui-sans-serif, -apple-system, sans-serif;
  }
  #talkzoom .hint {
    position: absolute; bottom: 22px; left: 0; right: 0; text-align: center;
    color: #6c7086; font: 15px ui-sans-serif, -apple-system, sans-serif;
  }
</style>
"""

BAR = """
<div id="talkbar">
  <div class="grp"><span class="lbl">Speed</span><span id="tb-speed"></span></div>
  <div class="grp"><span class="lbl">Chapter</span>
    <select id="tb-chapters"></select>
    <button id="tb-prev" title="previous chapter">&larr;</button>
    <button id="tb-next" title="next chapter">&rarr;</button>
    <button id="tb-pane" title="chapter list">&#9776;</button>
  </div>
  <div class="grp sp"><button id="tb-play">Pause</button><span class="now" id="tb-now">0:00</span>
    <button id="tb-fs" title="fullscreen">&#9974;</button>
  </div>
</div>
<div id="talkpane"><h3>Chapters</h3><div id="tb-panelist"></div></div>
<div id="talkpop">&#128269; \u653e\u5927\u6587\u5b57</div>
<div id="talkzoom">
  <button class="close" id="tz-close">&times;</button>
  <pre id="tz-text"></pre>
  <div class="hint">Esc \u6216 \u00d7 \u96e2\u958b</div>
</div>
"""

JS = r"""
<script>
(function () {
  var MARKERS = __MARKERS__;
  var SPEEDS = __SPEEDS__;
  var state = { speed: __DEFAULT_SPEED__, playing: true };
  var el = document.getElementById('player');
  var mk = window.__talkMount;
  var player = window.__talkPlayer;

  function fmt(t) {
    t = Math.max(0, Math.floor(t));
    return Math.floor(t / 60) + ':' + String(t % 60).padStart(2, '0');
  }
  function currentTime() {
    try { var v = player.getCurrentTime(); return (typeof v === 'number') ? v : 0; }
    catch (e) { return 0; }
  }

  // asciinema-player takes speed only at construction, so changing it means
  // rebuilding the player where it stood. Its `startAt` is ignored on a rebuild
  // (measured: getCurrentTime comes back 0), so seek explicitly once the new
  // instance is alive, retrying because the first seek can land too early.
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

  function setSpeed(s) { if (s !== state.speed) remount(s, currentTime(), state.playing); }
  function jump(t) {
    try { player.seek(t); } catch (e) {}
    if (!state.playing) { try { player.play(); state.playing = true; } catch (e) {} }
    paint();
  }
  function toggle() {
    try {
      if (state.playing) { player.pause(); state.playing = false; }
      else { player.play(); state.playing = true; }
    } catch (e) {}
    paint();
  }
  function chapterIndex(t) {
    var i = 0;
    for (var k = 0; k < MARKERS.length; k++) { if (MARKERS[k].t <= t + 0.4) i = k; }
    return i;
  }

  // --- speed --------------------------------------------------------------
  var sp = document.getElementById('tb-speed');
  SPEEDS.forEach(function (s) {
    var b = document.createElement('button');
    b.textContent = s + '\u00d7';
    b.dataset.speed = s;
    b.onclick = function () { setSpeed(s); };
    sp.appendChild(b);
  });

  // --- chapters: dropdown and side pane ------------------------------------
  var sel = document.getElementById('tb-chapters');
  var list = document.getElementById('tb-panelist');
  var pane = document.getElementById('talkpane');
  var rows = [];
  MARKERS.forEach(function (m, i) {
    var o = document.createElement('option');
    o.value = i; o.textContent = fmt(m.t) + '  ' + m.label;
    sel.appendChild(o);

    var d = document.createElement('div');
    d.className = 'ch' + (/^[\u25AE]/.test(m.label) ? ' stage' : '');
    d.innerHTML = '<span class="t"></span><span class="l"></span>';
    d.firstChild.textContent = fmt(m.t);
    d.lastChild.textContent = m.label.replace(/^[\u25AE\u25B8$]\s*/, '');
    d.onclick = function () { jump(m.t); };
    list.appendChild(d);
    rows.push(d);
  });
  sel.onchange = function () { jump(MARKERS[+sel.value].t); };
  document.getElementById('tb-prev').onclick = function () {
    var i = chapterIndex(currentTime());
    if (currentTime() - MARKERS[i].t < 2 && i > 0) i--;
    jump(MARKERS[i].t);
  };
  document.getElementById('tb-next').onclick = function () {
    jump(MARKERS[Math.min(MARKERS.length - 1, chapterIndex(currentTime()) + 1)].t);
  };
  var paneBtn = document.getElementById('tb-pane');
  paneBtn.onclick = function () {
    var open = !pane.classList.contains('open');
    pane.classList.toggle('open', open);
    document.body.classList.toggle('pane-open', open);
    paneBtn.setAttribute('aria-pressed', String(open));
    if (open) scrollPane();
  };
  function scrollPane() {
    var on = list.querySelector('.ch.on');
    if (on) on.scrollIntoView({ block: 'center' });
  }

  // --- play / pause / fullscreen -------------------------------------------
  var pb = document.getElementById('tb-play');
  pb.onclick = toggle;
  var fsBtn = document.getElementById('tb-fs');
  fsBtn.onclick = function () {
    // The player's own fullscreen button expands only the terminal, which hides
    // this bar and the pane. Fullscreen the document instead.
    var el = document.documentElement;
    if (document.fullscreenElement || document.webkitFullscreenElement) {
      (document.exitFullscreen || document.webkitExitFullscreen).call(document);
    } else {
      (el.requestFullscreen || el.webkitRequestFullscreen).call(el);
    }
  };
  function onFsChange() {
    var on = !!(document.fullscreenElement || document.webkitFullscreenElement);
    document.body.classList.toggle('fs', on);
    fsBtn.setAttribute('aria-pressed', String(on));
  }
  document.addEventListener('fullscreenchange', onFsChange);
  document.addEventListener('webkitfullscreenchange', onFsChange);

  // --- click anywhere to pause ---------------------------------------------
  // A drag is a text selection, not a click, so compare down/up positions
  // before treating it as one. Chrome fires this for the terminal too, and the
  // player has its own handler there, so ignore clicks that land inside it.
  var downAt = null;
  document.addEventListener('mousedown', function (e) { downAt = [e.clientX, e.clientY]; });
  document.addEventListener('mouseup', function (e) {
    if (!downAt) return;
    var moved = Math.abs(e.clientX - downAt[0]) + Math.abs(e.clientY - downAt[1]);
    downAt = null;
    if (moved > 6) return;                       // a selection drag
    if (e.target.closest('#talkbar, #talkpane, #talkpop, #talkzoom')) return;
    if (e.target.closest('.ap-player')) return;  // the player toggles this itself
    if (String(window.getSelection())) return;
    toggle();
  });

  // --- selection popover and zoom ------------------------------------------
  var pop = document.getElementById('talkpop');
  var zoom = document.getElementById('talkzoom');
  var ztext = document.getElementById('tz-text');
  var selected = '';

  function hidePop() { pop.style.display = 'none'; }

  document.addEventListener('selectionchange', function () {
    var s = window.getSelection();
    if (!s || s.isCollapsed || !String(s).trim()) { hidePop(); return; }
    var node = s.anchorNode;
    node = node && (node.nodeType === 1 ? node : node.parentElement);
    if (!node || !node.closest('.ap-player')) { hidePop(); return; }
    var r = s.getRangeAt(0).getBoundingClientRect();
    if (!r.width && !r.height) { hidePop(); return; }
    selected = String(s);
    pop.style.display = 'block';
    var w = pop.offsetWidth;
    pop.style.left = Math.max(8, Math.min(window.innerWidth - w - 8,
                     r.left + r.width / 2 - w / 2)) + 'px';
    pop.style.top = Math.max(8, r.top - pop.offsetHeight - 10) + 'px';
  });

  pop.onclick = function () {
    if (!selected.trim()) return;
    hidePop();
    if (state.playing) toggle();
    ztext.textContent = selected.replace(/\n{3,}/g, '\n\n').replace(/\s+$/, '');
    zoom.classList.add('open');
    fitZoom();
  };

  // Binary-search the largest font size whose rendered block still fits.
  function fitZoom() {
    var maxW = zoom.clientWidth - 2 * (0.03 * window.innerWidth);
    var maxH = zoom.clientHeight - (0.03 + 0.08) * window.innerHeight;
    var lo = 10, hi = 220, best = 14;
    for (var i = 0; i < 18; i++) {
      var mid = (lo + hi) / 2;
      ztext.style.fontSize = mid + 'px';
      if (ztext.scrollWidth <= maxW && ztext.scrollHeight <= maxH) { best = mid; lo = mid; }
      else hi = mid;
    }
    ztext.style.fontSize = Math.floor(best) + 'px';
  }
  window.addEventListener('resize', function () {
    if (zoom.classList.contains('open')) fitZoom();
  });

  function closeZoom() {
    zoom.classList.remove('open');
    var s = window.getSelection(); if (s) s.removeAllRanges();
  }
  document.getElementById('tz-close').onclick = closeZoom;
  zoom.addEventListener('mouseup', function (e) {
    if (e.target === zoom) closeZoom();
  });

  // --- paint ---------------------------------------------------------------
  function paint() {
    Array.prototype.forEach.call(sp.children, function (b) {
      b.setAttribute('aria-pressed', String(+b.dataset.speed === state.speed));
    });
    pb.textContent = state.playing ? 'Pause' : 'Play';
    var t = currentTime();
    document.getElementById('tb-now').textContent = fmt(t);
    var i = chapterIndex(t);
    if (+sel.value !== i) sel.value = i;
    rows.forEach(function (d, k) { d.classList.toggle('on', k === i); });
  }
  setInterval(paint, 500);
  paint();

  // --- keys ----------------------------------------------------------------
  document.addEventListener('keydown', function (e) {
    if (e.target.tagName === 'SELECT') return;
    if (e.key === 'Escape' && zoom.classList.contains('open')) { closeZoom(); e.preventDefault(); return; }
    if (e.key === 'x' && zoom.classList.contains('open')) { closeZoom(); e.preventDefault(); return; }
    if (zoom.classList.contains('open')) return;
    var i = SPEEDS.indexOf(state.speed);
    if (e.key === '+' || e.key === '=') { setSpeed(SPEEDS[Math.min(SPEEDS.length - 1, i + 1)]); e.preventDefault(); }
    else if (e.key === '-' || e.key === '_') { setSpeed(SPEEDS[Math.max(0, i - 1)]); e.preventDefault(); }
    else if (e.key === 'n') { document.getElementById('tb-next').click(); e.preventDefault(); }
    else if (e.key === 'p') { document.getElementById('tb-prev').click(); e.preventDefault(); }
    else if (e.key === 'c') { paneBtn.click(); e.preventDefault(); }
    else if (e.key === 'f') { document.getElementById('tb-fs').click(); e.preventDefault(); }
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
        f"  window.__talkPlayer = window.__talkMount({{speed: {DEFAULT_SPEED}}});")
    s = s[:m.start()] + boot + s[m.end():]

    js = (JS.replace("__MARKERS__", json.dumps(markers))
            .replace("__SPEEDS__", json.dumps(SPEEDS))
            .replace("__DEFAULT_SPEED__", json.dumps(DEFAULT_SPEED)))
    s = s.replace("</head>", CSS + "</head>", 1)
    s = s.replace("<body>", "<body>" + BAR, 1)
    if "<body>" not in html.read_text():          # some templates omit <body>
        s = s.replace(CSS + "</head>", CSS + "</head>", 1)
    s = s.replace("</body>", js + "</body>", 1)

    html.write_text(s)
    print(f"{html.name}: speed control ({', '.join(str(x) + 'x' for x in SPEEDS)}), "
          f"default {DEFAULT_SPEED}x, {len(markers)} chapters")


if __name__ == "__main__":
    main()
