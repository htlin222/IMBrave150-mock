/* =========================================================================
   Deck engine — a step-through presentation player with a faithful
   Claude Code session player.

   Non-session scenes: every element with data-step="N" appears once the
   current step >= N (advance with →).

   Session scenes play like a real Claude Code run:
     step 1  → the prompt TYPES into the composer (window zooms in)
             → on finish it SENDS: the composer clears, the prompt rises
               into a user bubble, and the agent starts THINKING (shimmer)
             → then the response AUTO-PLAYS: each tool row appears as
               "Running…" (shimmer) and resolves to "Ran" with its output,
               assistant text streams in, figures fade up, a "Working…"
               status ticks at the bottom and finally reads "Done".
     The presenter can press → any time to push the next beat immediately,
     or just let it run. → past the last beat goes to the next scene.
   ========================================================================= */
(function () {
  "use strict";

  const SB = window.STORYBOARD;
  const deck = document.getElementById("deck");
  const progressFill = document.querySelector("#progress .fill");
  const chapters = document.getElementById("chapters");
  const counter = document.getElementById("scene-counter");
  const speaker = document.getElementById("speaker");
  const SPARK = '<svg class="lucide" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .962 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.962 0z"/></svg>';

  const sceneEls = [];
  let cur = 0, step = 0, maxStep = 0;
  let notesLang = "en";    // presenter-note language (toggle with "i")
  let typing = false;      // a prompt is typing
  let sent = false;        // the current session prompt has been sent
  let autoTimer = null;    // session auto-play timer
  const started = Date.now();

  /* ---------- sound fx (Web Audio synth, self-contained, opt-in) ----------
     No audio files — every sound is a short enveloped oscillator tone, so the
     deck stays 100% self-contained. Off by default (a talk shouldn't beep by
     surprise); toggle with M or the HUD speaker. The AudioContext is created
     on that first user gesture, satisfying browser autoplay policy. */
  const sfx = (function () {
    let ctx = null, master = null, on = false, lastKey = 0;
    function ensure() {
      if (ctx) return;
      const AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return;
      ctx = new AC();
      master = ctx.createGain();
      master.gain.value = 0.9;
      master.connect(ctx.destination);
    }
    function tone(freq, dur, type, peak, when) {
      if (!ctx) return;
      const t0 = when || ctx.currentTime;
      const o = ctx.createOscillator(), g = ctx.createGain();
      o.type = type || "sine";
      o.frequency.setValueAtTime(freq, t0);
      g.gain.setValueAtTime(0.0001, t0);
      g.gain.exponentialRampToValueAtTime(peak, t0 + 0.008);
      g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
      o.connect(g); g.connect(master);
      o.start(t0); o.stop(t0 + dur + 0.02);
    }
    const now = () => (ctx ? ctx.currentTime : 0);
    return {
      get on() { return on; },
      toggle() {
        on = !on;
        if (on) { ensure(); if (ctx && ctx.state === "suspended") ctx.resume(); tone(880, 0.10, "sine", 0.12); }
        return on;
      },
      key() {                                            // one keystroke while typing
        if (!on) return;
        const t = (window.performance && performance.now()) || 0;
        if (t - lastKey < 55) return;                    // throttle machine-gun typing
        lastKey = t; ensure();
        tone(1500 + Math.random() * 300, 0.028, "square", 0.014);
      },
      ready() { if (!on) return; ensure(); tone(660, 0.10, "sine", 0.06); tone(990, 0.12, "sine", 0.05, now() + 0.06); },
      send()  { if (!on) return; ensure(); tone(520, 0.10, "triangle", 0.09); tone(780, 0.12, "triangle", 0.07, now() + 0.05); },
      think() { if (!on) return; ensure(); tone(300, 0.20, "sine", 0.05); },
      tool()  { if (!on) return; ensure(); tone(430, 0.05, "square", 0.04); },   // low beep as a tool starts (Running)
      ran()   { if (!on) return; ensure(); tone(720, 0.06, "sine", 0.05); },     // higher confirm as it resolves (Ran)
      done()  { if (!on) return; ensure(); const t = now(); tone(660, 0.10, "sine", 0.07, t); tone(880, 0.10, "sine", 0.07, t + 0.08); tone(1320, 0.16, "sine", 0.06, t + 0.16); },
      scene() { if (!on) return; ensure(); tone(200, 0.12, "sine", 0.05); tone(400, 0.14, "sine", 0.035, now() + 0.03); },
    };
  })();

  /* ---------- build scenes ---------- */
  SB.scenes.forEach((sc, i) => {
    const el = document.createElement("section");
    el.className = "scene " + (sc.kind || "concept") + "-scene";
    el.dataset.index = i;
    el.innerHTML = `<div class="scene-inner">${sc.html}</div>`;
    el.addEventListener("click", () => {
      if (document.body.classList.contains("overview")) { toggleOverview(false); go(i); }
    });
    deck.appendChild(el);
    sceneEls.push(el);
  });
  SB.scenes.forEach((sc, i) => {
    const t = document.createElement("div");
    t.className = "tick"; t.title = sc.title || "";
    t.addEventListener("click", () => go(i));
    chapters.appendChild(t);
  });
  const ticks = [...chapters.children];

  /* ---------- helpers ---------- */
  const isSession = () => (SB.scenes[cur].kind === "session");
  function stepsIn(el) {
    let m = 0;
    el.querySelectorAll("[data-step]").forEach(n => { m = Math.max(m, +n.dataset.step || 0); });
    const tabs = el.querySelectorAll("[data-tab-idx]").length;   // tabbed data viewer
    return Math.max(m, tabs ? tabs - 1 : 0);
  }
  function scrollToLast(el) {
    const scroll = el.querySelector(".sess-scroll");
    if (!scroll) return;
    const shown = [...scroll.querySelectorAll(".sbeat.show, .sess-think, .u-msg-turn, .sess-status")];
    const last = shown[shown.length - 1];
    if (last) scroll.scrollTo({ top: last.offsetTop - 30, behavior: "smooth" });
  }

  /* reveal all [data-step] up to s (non-session, and session final state) */
  function applyStep(el, s) {
    el.querySelectorAll("[data-step]").forEach(n => {
      const ns = +n.dataset.step || 0, on = ns <= s;
      n.classList.toggle("on", on);
      n.classList.toggle("show", on);
      n.classList.toggle("cur", ns === s);
    });
    // tabbed data viewer: activate the tab matching the current step
    const tabs = el.querySelectorAll("[data-tab-idx]");
    if (tabs.length) {
      const active = Math.max(0, Math.min(tabs.length - 1, s));
      tabs.forEach((t, i) => t.classList.toggle("active", i === active));
      el.querySelectorAll("[data-tab-btn]").forEach((b, i) => b.classList.toggle("active", i === active));
    }
    scrollToLast(el);
  }

  function typewriter(node, text, done) {
    typing = true;
    node.classList.add("typing");
    node.textContent = "";
    const mac = node.closest(".mac"); if (mac) mac.classList.add("zoom");
    document.body.classList.add("prompt-focus");
    let i = 0;
    (function tick() {
      if (i <= text.length) { node.textContent = text.slice(0, i); sfx.key(); i++; setTimeout(tick, 20 + Math.random() * 30); }
      else {
        // Typed and PENDING: keep the caret, the zoom and the dim, and wait
        // for the presenter to send. The typing guard releases so the next →
        // triggers the actual send + thinking animation.
        typing = false;
        document.body.classList.add("prompt-ready");
        sfx.ready();
        done && done();
      }
    })();
  }

  /* ---------- session: send + thinking + auto-play ---------- */
  function clearAuto() { if (autoTimer) { clearTimeout(autoTimer); autoTimer = null; } }

  function toolCount(el) { return el.querySelectorAll(".sess-beats .tool-row").length; }

  function sendPrompt(el) {
    sfx.send();
    const promptNode = el.querySelector("[data-type]");
    if (promptNode) promptNode.classList.remove("typing");
    const mac = el.querySelector(".mac"); if (mac) mac.classList.remove("zoom");
    document.body.classList.remove("prompt-focus", "prompt-ready");
    const box = el.querySelector(".cc-box"); if (box) box.classList.add("generating");
    const text = (promptNode && (promptNode.dataset.text || promptNode.textContent)) || "";
    // rise into a user bubble
    const slot = el.querySelector(".sess-user-slot");
    if (slot) { slot.innerHTML = `<div class="turn u-msg-turn"><div class="u-msg"><div class="bubble"></div></div></div>`; slot.querySelector(".bubble").textContent = text; }
    // clear the composer
    if (promptNode) promptNode.textContent = "";
    el.querySelector(".sess-composer .input") && el.querySelector(".sess-composer .input").classList.add("empty");
    sent = true;
    // thinking shimmer, then collapse
    const think = el.querySelector(".sess-think-slot");
    const secs = 3 + Math.floor(Math.random() * 4);
    if (think) {
      think.innerHTML = `<div class="sess-think"><span class="spark">${SPARK}</span><span class="shimmer-label">Thinking…</span></div>`;
      sfx.think();
      scrollToLast(el);
      setTimeout(() => {
        think.innerHTML = `<div class="sess-think collapsed"><span class="spark-mini">${SPARK}</span> Thought for ${secs}s</div>`;
        startWorking(el);
        autoAdvance(el);      // begin revealing the response
      }, 1300);
    } else { startWorking(el); autoAdvance(el); }
    renderSpeaker(); updateChrome();
  }

  function startWorking(el) {
    const s = el.querySelector(".sess-status-slot");
    if (s) s.innerHTML = `<div class="sess-status working"><span class="spark">${SPARK}</span> <span class="shimmer-label">Working…</span></div>`;
  }
  function finishWorking(el) {
    const s = el.querySelector(".sess-status-slot");
    if (s) s.innerHTML = `<div class="sess-status done"><span class="spark-mini">${SPARK}</span> Done · ${toolCount(el)} tool ${toolCount(el) === 1 ? "call" : "calls"}</div>`;
    const box = el.querySelector(".cc-box"); if (box) box.classList.remove("generating");
    sfx.done();
  }

  /* reveal every response beat at step s; animate tool rows Running→Ran */
  function revealBeat(el, s) {
    const beats = el.querySelectorAll(`.sess-beats [data-step="${s}"]`);
    beats.forEach(beat => {
      beat.classList.add("show", "on");
      const row = beat.querySelector(".tool-row");
      const detail = beat.querySelector(".tool-detail");
      if (row && detail) {
        const verb = row.querySelector(".verb");
        row.classList.add("running", "pending");
        if (verb) verb.textContent = "Running";
        sfx.tool();
        setTimeout(() => {
          row.classList.remove("running", "pending");
          row.classList.add("open");
          if (verb) verb.textContent = "Ran";
          detail.classList.remove("pending");
          sfx.ran();
          scrollToLast(el);
        }, 780 + Math.random() * 260);
      }
    });
    scrollToLast(el);
  }

  function beatDelay(el, s) {
    const beat = el.querySelector(`.sess-beats [data-step="${s}"]`);
    if (!beat) return 900;
    if (beat.querySelector(".tool-row")) return 1500;   // running + read time
    if (beat.querySelector(".figure-card")) return 1500;
    if (beat.querySelector(".callout")) return 1200;
    return 1150;
  }

  /* auto-play: keep revealing response beats on timers until the last one */
  function autoAdvance(el) {
    clearAuto();
    if (step >= maxStep) { finishWorking(el); return; }
    autoTimer = setTimeout(() => {
      step++;
      revealBeat(el, step);
      renderSpeaker(); updateChrome();
      if (step >= maxStep) { finishWorking(el); }
      else autoAdvance(el);
    }, beatDelay(el, step + 1));
  }

  /* ---------- navigation ---------- */
  function renderScene(enter) {
    sceneEls.forEach((el, i) => el.classList.toggle("active", i === cur));
    const el = sceneEls[cur];
    if (enter) { el.classList.remove("enter"); void el.offsetWidth; el.classList.add("enter"); }
    el.querySelectorAll(".typing").forEach(n => n.classList.remove("typing"));
    const mac = el.querySelector(".mac"); if (mac) mac.classList.remove("zoom");
    maxStep = stepsIn(el);
    updateChrome();
  }

  function next() {
    if (typing) return;
    const el = sceneEls[cur];
    if (isSession()) {
      if (step < 1) {                       // step 0 → type the prompt
        step = 1;
        const typer = el.querySelector(`[data-type][data-step="1"]`);
        if (typer && typer.dataset.typed !== "1") {
          typer.dataset.typed = "1";
          typewriter(typer, typer.dataset.text || "", () => { renderSpeaker(); updateChrome(); });
        } else { sendPrompt(el); }
        updateChrome(); renderSpeaker();
        return;
      }
      if (!sent) { sendPrompt(el); return; }
      if (step < maxStep) {                 // push the next response beat now
        clearAuto();
        step++; revealBeat(el, step);
        if (step >= maxStep) finishWorking(el); else autoAdvance(el);
        renderSpeaker(); updateChrome();
        return;
      }
      clearAuto();
      go(cur + 1);
      return;
    }
    // non-session
    if (step < maxStep) {
      step++;
      applyStep(el, step);
      renderSpeaker(); updateChrome();
    } else go(cur + 1);
  }

  function prev() {
    if (typing) return;
    clearAuto();
    if (step > 0) { go(cur, false); }       // restart the current scene clean
    else go(cur - 1, true);
  }

  function go(i, toEnd) {
    clearAuto();
    document.body.classList.remove("prompt-focus", "prompt-ready");
    // a focused HUD/nav button would otherwise swallow the first Space/Enter
    if (document.activeElement && document.activeElement.blur) document.activeElement.blur();
    i = Math.max(0, Math.min(SB.scenes.length - 1, i));
    if (i !== cur) sfx.scene();
    cur = i; step = 0; sent = false; typing = false;
    renderScene(true);
    const el = sceneEls[cur];
    // reset dynamic session bits
    el.querySelectorAll("[data-type]").forEach(t => { t.dataset.typed = ""; t.textContent = ""; t.classList.remove("typing"); });
    const us = el.querySelector(".sess-user-slot"); if (us) us.innerHTML = "";
    const th = el.querySelector(".sess-think-slot"); if (th) th.innerHTML = "";
    const st = el.querySelector(".sess-status-slot"); if (st) st.innerHTML = "";
    const box0 = el.querySelector(".cc-box"); if (box0) box0.classList.remove("generating");
    el.querySelectorAll(".sess-beats .tool-row").forEach(r => { r.classList.remove("running", "open"); r.classList.add("pending"); const v = r.querySelector(".verb"); if (v) v.textContent = "Ran"; });
    el.querySelectorAll(".sess-beats .tool-detail").forEach(d => d.classList.add("pending"));
    applyStep(el, 0);

    if (toEnd) {                            // reveal a whole scene at once (stepping back in)
      step = maxStep;
      if (isSession()) {
        sent = true;
        const typer = el.querySelector("[data-type]");
        const txt = typer ? (typer.dataset.text || "") : "";
        const slot = el.querySelector(".sess-user-slot");
        if (slot) { slot.innerHTML = `<div class="turn u-msg-turn"><div class="u-msg"><div class="bubble"></div></div></div>`; slot.querySelector(".bubble").textContent = txt; }
        const think = el.querySelector(".sess-think-slot");
        if (think) think.innerHTML = `<div class="sess-think collapsed"><span class="spark-mini">${SPARK}</span> Thought for 5s</div>`;
        el.querySelectorAll(".sess-beats [data-step]").forEach(b => b.classList.add("show", "on"));
        el.querySelectorAll(".sess-beats .tool-row").forEach(r => { r.classList.remove("running", "pending"); r.classList.add("open"); });
        el.querySelectorAll(".sess-beats .tool-detail").forEach(d => d.classList.remove("pending"));
        finishWorking(el);
      } else {
        applyStep(el, maxStep);
      }
    }
    renderSpeaker(); updateChrome();
  }

  function updateChrome() {
    const total = SB.scenes.length;
    const frac = (cur + (maxStep ? step / maxStep : 0)) / total;
    progressFill.style.width = (frac * 100).toFixed(1) + "%";
    counter.textContent = `${String(cur + 1).padStart(2, "0")} / ${String(total).padStart(2, "0")}`;
    ticks.forEach((t, i) => { t.classList.toggle("active", i === cur); t.classList.toggle("done", i < cur); });
  }

  /* ---------- speaker mode ---------- */
  let clockTimer = null;
  function fmt(ms) { const s = Math.max(0, Math.floor(ms / 1000)); return `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`; }
  function renderSpeaker() {
    if (!document.body.classList.contains("speaker")) return;
    const sc = SB.scenes[cur], nx = SB.scenes[cur + 1];
    const cues = sc.stepNotes || [];
    const cue = step > 0 && cues[step - 1] ? cues[step - 1] : (cues[0] || "");
    speaker.querySelector(".sp-title").textContent = sc.title || "";
    speaker.querySelector(".sp-act").textContent = (sc.act || "") + (sc.duration ? `  ·  ~${sc.duration} min` : "");
    const langBtn = speaker.querySelector(".sp-lang");
    if (langBtn) langBtn.textContent = notesLang === "zh" ? "EN" : "中文";
    const useZh = notesLang === "zh" && sc.notesZh;
    speaker.querySelector(".sp-notes").innerHTML = (useZh ? sc.notesZh : sc.notes) || "";
    speaker.querySelector(".sp-step").innerHTML = maxStep ? `<b>Beat ${step}/${maxStep}</b>${cue ? " · " + cue : ""}` : "Single beat";
    speaker.querySelector(".sp-next .nx").textContent = nx ? nx.title : "— end —";
  }
  function tickClock() { if (document.body.classList.contains("speaker")) speaker.querySelector(".sp-clock .big").textContent = fmt(Date.now() - started); }
  function toggleSpeaker() {
    document.body.classList.toggle("speaker");
    if (document.body.classList.contains("speaker")) { renderSpeaker(); clockTimer = setInterval(tickClock, 1000); tickClock(); }
    else if (clockTimer) clearInterval(clockTimer);
    renderScene(false);
  }

  /* ---------- overview ---------- */
  function toggleOverview(force) {
    const on = force !== undefined ? force : !document.body.classList.contains("overview");
    document.body.classList.toggle("overview", on);
    if (on) { clearAuto(); sceneEls.forEach(el => { el.querySelectorAll("[data-step]").forEach(n => n.classList.add("on", "show")); }); }
    else { renderScene(false); go(cur, false); }
  }

  /* ---------- click-to-zoom conversation blocks ----------
     Click a block to enlarge it; while open, ↑/↓ (or ←/→) step to the
     previous/next block in the SAME conversation. Esc closes. */
  const zoom = document.getElementById("zoom");
  const zcard = zoom.querySelector(".zcard");
  let zoomList = [], zoomIdx = -1;
  const zoomOpen = () => zoom.classList.contains("show");

  function collectBlocks(fromEl) {
    const scene = fromEl.closest(".scene");
    if (!scene) return [fromEl];
    // data tables: zoom through all three dialects with ↑/↓
    if (fromEl.closest(".data-table")) return [...scene.querySelectorAll(".data-table")];
    return [...scene.querySelectorAll(".sess-scroll .turn, .sess-scroll .u-msg-turn")]
      .filter(n => n.classList.contains("u-msg-turn") || n.classList.contains("show"));
  }
  function renderZoom() {
    const el = zoomList[zoomIdx]; if (!el) return;
    zcard.innerHTML =
      `<div class="zmeta">${zoomIdx + 1} / ${zoomList.length}` +
      `<span class="zhint">↑ ↓ move · Esc close</span></div>` +
      `<div class="zbody">${el.innerHTML}</div>`;
    zcard.scrollTop = 0;
  }
  function openZoomFor(el) {
    zoomList = collectBlocks(el);
    zoomIdx = Math.max(0, zoomList.indexOf(el));
    renderZoom();
    zoom.classList.add("show");
  }
  function zoomStep(d) {
    if (!zoomList.length) return;
    zoomIdx = Math.max(0, Math.min(zoomList.length - 1, zoomIdx + d));
    renderZoom();
  }
  function closeZoom() { zoom.classList.remove("show"); zcard.innerHTML = ""; zoomList = []; zoomIdx = -1; }

  deck.addEventListener("click", (e) => {
    if (document.body.classList.contains("overview") || zoomOpen()) return;
    // the composer send button really sends the prompt
    const sb = e.target.closest("[data-send]");
    if (sb) { e.stopPropagation(); sb.blur(); clickSend(); return; }
    const st = e.target.closest("[data-stop]");
    if (st) { e.stopPropagation(); st.blur(); clearAuto(); if (isSession()) finishWorking(sceneEls[cur]); return; }
    // tabbed data viewer: clicking a tab jumps to that dialect
    const tb = e.target.closest("[data-tab-btn]");
    if (tb) { e.stopPropagation(); tb.blur(); step = +tb.dataset.tabBtn || 0; applyStep(sceneEls[cur], step); updateChrome(); renderSpeaker(); return; }
    const block = e.target.closest(".sess-scroll .turn, .sess-scroll .u-msg-turn, .data-table");
    if (block) { e.stopPropagation(); openZoomFor(block); }
    // (navigation is keyboard / on-screen arrows only — clicking a block
    //  zooms it; clicking elsewhere does nothing, so a page never advances
    //  by accident and never needs a second click.)
  });

  /* clicking the clay send button types (if needed) then sends the prompt */
  function clickSend() {
    if (!isSession()) return;
    const el = sceneEls[cur];
    if (sent || typing) return;
    const typer = el.querySelector("[data-type]");
    if (typer && typer.dataset.typed !== "1") {
      typer.dataset.typed = "1"; step = 1;
      typewriter(typer, typer.dataset.text || "", () => sendPrompt(el));
    } else {
      sendPrompt(el);
    }
  }
  zoom.addEventListener("click", (e) => { if (e.target === zoom || e.target.closest(".zclose")) closeZoom(); });

  /* ---------- fullscreen / help ---------- */
  function toggleFull() { if (!document.fullscreenElement) document.documentElement.requestFullscreen && document.documentElement.requestFullscreen(); else document.exitFullscreen && document.exitFullscreen(); }
  const help = document.getElementById("help");
  function toggleHelp() { help.classList.toggle("show"); }
  const soundBtn = document.querySelector('[data-act="sound"]');
  function toggleSound() { sfx.toggle(); if (soundBtn) { soundBtn.textContent = sfx.on ? "🔊" : "🔇"; soundBtn.classList.toggle("on", sfx.on); } }

  /* ---------- keyboard ---------- */
  document.addEventListener("keydown", (e) => {
    // when a conversation block is zoomed, arrows step between blocks
    if (zoomOpen()) {
      switch (e.key) {
        case "ArrowUp": case "ArrowLeft": case "PageUp": e.preventDefault(); zoomStep(-1); return;
        case "ArrowDown": case "ArrowRight": case " ": case "PageDown": e.preventDefault(); zoomStep(1); return;
        case "Escape": e.preventDefault(); closeZoom(); return;
        default: return;   // swallow other keys while zoomed
      }
    }
    if (help.classList.contains("show") && e.key !== "?" && e.key !== "Escape") { help.classList.remove("show"); return; }
    switch (e.key) {
      case "ArrowRight": case " ": case "PageDown": e.preventDefault(); next(); break;
      case "ArrowLeft": case "PageUp": e.preventDefault(); prev(); break;
      case "ArrowDown": e.preventDefault(); go(cur + 1); break;
      case "ArrowUp": e.preventDefault(); go(cur - 1); break;
      case "Home": go(0); break;
      case "End": go(SB.scenes.length - 1); break;
      case "s": case "S": toggleSpeaker(); break;
      case "i": case "I":
        if (!document.body.classList.contains("speaker")) { notesLang = "zh"; toggleSpeaker(); }
        else { notesLang = notesLang === "en" ? "zh" : "en"; renderSpeaker(); }
        break;
      case "f": case "F": toggleFull(); break;
      case "m": case "M": toggleSound(); break;
      case "o": case "O": toggleOverview(); break;
      case "c": case "C": chapters.classList.toggle("show"); break;
      case "?": toggleHelp(); break;
      case "Escape": closeZoom(); document.body.classList.remove("overview"); help.classList.remove("show"); break;
    }
  });
  document.querySelectorAll("[data-act]").forEach(b => b.addEventListener("click", () => {
    const a = b.dataset.act;
    if (a === "speaker") toggleSpeaker(); else if (a === "full") toggleFull(); else if (a === "overview") toggleOverview();
    else if (a === "sound") toggleSound();
    else if (a === "help") toggleHelp(); else if (a === "prev") prev(); else if (a === "next") next();
    else if (a === "lang") { notesLang = notesLang === "en" ? "zh" : "en"; renderSpeaker(); }
    b.blur();   // release focus so keyboard keeps controlling the deck
  }));
  document.addEventListener("mousemove", (e) => {
    if (e.clientY > window.innerHeight - 60) chapters.classList.add("show");
    else if (!chapters.matches(":hover")) chapters.classList.remove("show");
  });

  /* ---------- init (hash deep-link, ?reveal, ?speaker) ---------- */
  const h = parseInt(location.hash.slice(1), 10);
  go(Number.isFinite(h) ? h - 1 : 0, /reveal/.test(location.search));
  if (/speaker/.test(location.search)) toggleSpeaker();
})();
