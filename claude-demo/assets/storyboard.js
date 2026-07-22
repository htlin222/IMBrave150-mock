/* =========================================================================
   STORYBOARD — "How I do real-world data analysis with Claude Code"
   A curated 1-hour walkthrough of the IMbrave150 synthetic pipeline.
   Every number and every console block below is VERBATIM from a real run
   of the repo's scripts. Figures are the real SVGs produced by that run.
   ========================================================================= */
(function () {
	"use strict";

	/* -------- Lucide icons (inline SVG, no external deps) -------- */
	const LI = {
		sparkle:
			'<path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .962 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.962 0z"/>',
		database:
			'<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/><path d="M3 12A9 3 0 0 0 21 12"/>',
		scale:
			'<path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>',
		trending: '<path d="M16 7h6v6"/><path d="m22 7-8.5 8.5-5-5L2 17"/>',
		fork: '<circle cx="12" cy="18" r="3"/><circle cx="6" cy="6" r="3"/><circle cx="18" cy="6" r="3"/><path d="M18 9v2c0 .6-.4 1-1 1H7c-.6 0-1-.4-1-1V9"/><path d="M12 12v3"/>',
		repeat:
			'<path d="m17 2 4 4-4 4"/><path d="M3 11v-1a4 4 0 0 1 4-4h14"/><path d="m7 22-4-4 4-4"/><path d="M21 13v1a4 4 0 0 1-4 4H3"/>',
		file: '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v5h5"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/>',
		chevron: '<path d="m9 18 6-6-6-6"/>',
		chevronDown: '<path d="m6 9 6 6 6-6"/>',
		check: '<path d="M20 6 9 17l-5-5"/>',
		arrowRight: '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
		arrowUp: '<path d="m5 12 7-7 7 7"/><path d="M12 19V5"/>',
		plus: '<path d="M5 12h14"/><path d="M12 5v14"/>',
		mic: '<path d="M12 19v3"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><rect x="9" y="2" width="6" height="13" rx="3"/>',
	};
	const ic = (n) =>
		`<svg class="lucide" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${LI[n]}</svg>`;

	/* -------- small HTML builders (keep scenes readable) -------- */
	const spark = `<span class="spark">${ic("sparkle")}</span>`;

	function mac(title, beatsHTML, promptText, promptStep) {
		return `
    <div class="session">
      <div class="mac">
        <div class="titlebar">
          <div class="lights"><span class="light r"></span><span class="light y"></span><span class="light g"></span></div>
          <div class="wtitle">${title}</div>
        </div>
        <div class="sess-body">
          <div class="sess-scroll"><div class="thread-inner">
            <div class="sess-user-slot"></div>
            <div class="sess-think-slot"></div>
            <div class="sess-beats">${beatsHTML}</div>
            <div class="sess-status-slot"></div>
          </div></div>
          <div class="sess-composer">
            <div class="cc-box">
              <div class="cc-input"><span class="prompt-text" data-type data-step="${promptStep}" data-text="${promptText.replace(/"/g, "&quot;")}"></span></div>
              <div class="cc-row">
                <button class="cc-icon cc-plus" tabindex="-1">${ic("plus")}</button>
                <div class="cc-toggle"><span class="on">Chat</span><span>Cowork</span></div>
                <div class="grow"></div>
                <div class="cc-model"><b>Fable 5</b> <span class="tier">Max</span> ${ic("chevronDown")}</div>
                <button class="cc-icon cc-mic" tabindex="-1">${ic("mic")}</button>
                <button class="cc-stop" data-stop tabindex="-1" title="Stop"><span class="cc-sq"></span></button>
                <button class="cc-send" data-send title="Send">${ic("arrowUp")}</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>`;
	}
	const asst = (step, html) =>
		`<div class="turn sbeat" data-step="${step}"><div class="a-text">${html}</div></div>`;
	function tool(step, verb, label, head, pre) {
		return `<div class="turn sbeat" data-step="${step}">
      <div class="tool-row pending"><span class="chev">${ic("chevron")}</span> <span class="verb">${verb}</span> ${label}</div>
      <div class="tool-detail pending"><div class="head">${head}</div><pre>${pre}</pre></div>
    </div>`;
	}
	const fig = (step, src, cap) =>
		`<div class="turn sbeat" data-step="${step}"><div class="figure-card"><img src="figures/${src}" alt="${cap}"><div class="cap">${cap}</div></div></div>`;
	const say = (step, html) =>
		`<div class="turn sbeat" data-step="${step}"><div class="callout">${spark}<div>${html}</div></div></div>`;

	/* -------- raw-data table (tabbed viewer) -------- */
	// headers: [{t, hl}]; rows: [[cell,...]] — a highlighted header highlights its column
	function dtable(headers, rows) {
		const head = `<tr>${headers.map((h) => `<th class="${h.hl ? "hl" : ""}">${h.t}</th>`).join("")}</tr>`;
		const body = rows
			.map((r) => `<tr>${r.map((c, i) => `<td class="${headers[i].hl ? "hl" : ""}">${c === "" ? '<span class="na">·</span>' : c}</td>`).join("")}</tr>`)
			.join("");
		return `<div class="data-table"><table class="dt"><thead>${head}</thead><tbody>${body}</tbody></table></div>`;
	}

	/* =====================================================================
     SCENES
     ===================================================================== */
	const scenes = [];

	/* 0 — TITLE ---------------------------------------------------------- */
	scenes.push({
		kind: "title",
		act: "Opening",
		title: "Title",
		duration: 2,
		html: `
      <div class="title-wordmark">${spark} Claude Code <span class="pill">Live methods walkthrough</span></div>
      <div class="eyebrow">${spark} A real-world data analysis, start to finish</div>
      <h1 class="display">How I do real-world<br>data analysis<br>with Claude&nbsp;Code</h1>
      <p class="subhead">Ten messy hospital exports, one session, a submission-ready manuscript.</p>
      <div class="title-meta">
        <div class="item"><div class="k">Case study</div><div class="v">IMbrave150 (synthetic)</div></div>
        <div class="item"><div class="k">Endpoint</div><div class="v">Overall survival, HCC</div></div>
        <div class="item"><div class="k">Runtime</div><div class="v">~60 minutes</div></div>
        <div class="item"><div class="k">Presenter</div><div class="v">林協霆 · 和信治癌中心腫瘤內科部</div></div>
      </div>`,
		notes: `<ul>
      <li>Open warm. This is a <b>process</b> talk, not a results talk. The goal: the audience leaves knowing <b>how</b> to drive Claude Code through a full analysis.</li>
      <li>Frame the honesty up front: the data are <b>fully synthetic</b>, modelled on the real IMbrave150 trial (Finn 2020, NEJM). No real patients. We teach the method; the numbers happen to land on the trial.</li>
      <li>Promise the arc: messy data → causal inference → survival → subgroups → robustness → the written paper.</li>
      <li><span class="cue">key</span> Press <b>S</b> now to check the presenter clock is running. Press <b>→</b> to advance.</li>
    </ul>`,
	});

	/* 1 — THE QUESTION + PIPELINE MAP ----------------------------------- */
	scenes.push({
		kind: "concept",
		act: "Opening",
		title: "The question & the map",
		duration: 3,
		stepNotes: [
			"state the question",
			"reveal the 6-stage map one node at a time",
			"land the meta-move",
		],
		html: `
      <div class="eyebrow">${spark} The question</div>
      <h2 class="scene-h">Can Claude Code take me from raw EHR exports<br>to a defensible manuscript — and can I trust it?</h2>
      <p class="scene-lede">Run the <b>real pipeline</b>. Verify every number. Then replay it, clean. That's what you're watching.</p>
      <div class="pipe">
        <div class="node" data-step="1"><div class="ic">${ic("database")}</div><div class="t">Aggregate</div><div class="d">10 hospitals · 3 EHR dialects → one cohort</div></div>
        <span class="arrow" data-step="1">${ic("arrowRight")}</span>
        <div class="node" data-step="2"><div class="ic">${ic("scale")}</div><div class="t">De-confound</div><div class="d">propensity-score matching</div></div>
        <span class="arrow" data-step="2">${ic("arrowRight")}</span>
        <div class="node" data-step="3"><div class="ic">${ic("trending")}</div><div class="t">Survival</div><div class="d">Kaplan–Meier · Cox</div></div>
        <span class="arrow" data-step="3">${ic("arrowRight")}</span>
        <div class="node" data-step="4"><div class="ic">${ic("fork")}</div><div class="t">Subgroups</div><div class="d">forest plot</div></div>
        <span class="arrow" data-step="4">${ic("arrowRight")}</span>
        <div class="node" data-step="5"><div class="ic">${ic("repeat")}</div><div class="t">Robustness</div><div class="d">120 specs · TMLE</div></div>
        <span class="arrow" data-step="5">${ic("arrowRight")}</span>
        <div class="node" data-step="6"><div class="ic">${ic("file")}</div><div class="t">Manuscript</div><div class="d">IMRaD, cross-referenced</div></div>
      </div>
      <div style="margin-top:26px" data-step="7">
        <div class="callout">${spark}<div><b>The meta-move:</b> a subagent runs the genuine analysis end-to-end; then we regenerate it as this narrated demo. Fidelity first, polish second.</div></div>
      </div>`,
		notes: `<ul>
      <li>Ask the room: “How many of you have inherited data from more than one site?” — everyone. That pain is the hook.</li>
      <li>Walk the six nodes as you reveal them. Each node = one chapter of this talk.</li>
      <li><span class="cue">beat 3</span> Land the trust point: I did <b>not</b> ask Claude to make up a nice story. I ran the real scripts, checked them against an answer key, <b>then</b> curated. Say the phrase “fidelity first, polish second.”</li>
    </ul>`,
	});

	/* 2 — ACT 1: THE MESS (dialect table) ------------------------------- */
	scenes.push({
		kind: "concept",
		act: "Act I · Data aggregation",
		title: "The data does not arrive tidy",
		duration: 3,
		stepNotes: [
			"set up the mess",
			"Alpha row",
			"Beta row",
			"Gamma row",
			"the point: harmonise before you analyse",
		],
		html: `
      <div class="eyebrow">${spark} Act I · Aggregation</div>
      <h2 class="scene-h">Ten hospitals. Three EHR dialects. One schema you have to invent.</h2>
      <div class="cols wide-left">
        <div>
          <table class="dtable">
            <thead><tr><th>Vendor</th><th>Sites</th><th>What is different</th></tr></thead>
            <tbody>
              <tr data-step="1"><td><span class="tag alpha">Alpha</span></td><td>H01·H04·H07·H10</td><td>Canonical layout; blank = missing</td></tr>
              <tr data-step="2"><td><span class="tag beta">Beta</span></td><td>H02·H05·H08</td><td><code>AtezoBev</code>; sex <code>M/F</code>; albumin <b>g/L</b>, bilirubin <b>µmol/L</b>; <code>os_death</code></td></tr>
              <tr data-step="3"><td><span class="tag gamma">Gamma</span></td><td>H03·H06·H09</td><td><code>A+B</code>/<code>SOR</code>; Child–Pugh <code>A5/A6</code>; <b>no continuous AFP</b>; <code>time_os</code></td></tr>
            </tbody>
          </table>
          <p class="scene-lede" style="margin-top:16px" data-step="4">Site type &amp; region aren't in the patient files — they live in <code>hospitals_meta.csv</code> and must be joined on <code>hospital_id</code>.</p>
        </div>
        <div class="stack">
          <div class="stat" data-step="1"><div class="v clay">10</div><div class="k">hospital files</div></div>
          <div class="stat" data-step="4"><div class="v">~5–6%</div><div class="k">missing lab values</div></div>
          <div class="callout" data-step="4">${spark}<div>Rename, recode, convert units, parse <code>A5→5</code> — <b>then</b> pool.</div></div>
        </div>
      </div>`,
		notes: `<ul>
      <li>This slide earns the whole talk. Real-world data is <b>never</b> one clean CSV. Dwell on the unit traps: albumin in g/L vs g/dL is a factor of 10 — silently wrong if you miss it.</li>
      <li>Gamma has <b>no continuous AFP</b>, only the ≥400 flag. Point out that's all PSM needs — a nice teaching beat about “measure what the estimand requires.”</li>
      <li><span class="cue">beat 5</span> Transition: “I could hand-write this harmoniser… or I could describe the target schema to Claude Code and let it reconcile the dialects.” → next scene.</li>
    </ul>`,
	});

	/* 2b — ACT 1: LOOK AT THE RAW DATA (tabbed viewer) ------------------- */
	scenes.push({
		kind: "data",
		act: "Act I · Data aggregation",
		title: "Look at the raw data",
		duration: 4,
		stepNotes: ["H01 · Alpha — tidy, blanks = missing", "H02 · Beta — units & codes differ", "H03 · Gamma — no continuous AFP"],
		html: `
      <div class="eyebrow">${spark} Act I · The raw exports</div>
      <h2 class="scene-h">First move: open the files and actually look.</h2>
      <div class="session"><div class="mac">
        <div class="titlebar">
          <div class="lights"><span class="light r"></span><span class="light y"></span><span class="light g"></span></div>
          <div class="wtitle">raw hospital exports — three EHR dialects</div>
        </div>
        <div class="data-body">
          <div class="data-tabbar">
            <button class="tab-btn active" data-tab-btn="0">H01 Northshore <span class="tag alpha">Alpha</span></button>
            <button class="tab-btn" data-tab-btn="1">H02 Riverside <span class="tag beta">Beta</span></button>
            <button class="tab-btn" data-tab-btn="2">H03 Metropolitan <span class="tag gamma">Gamma</span></button>
          </div>
          <div class="data-panels">
            <div class="data-tab active" data-tab-idx="0">
              <div class="data-caption">Canonical, tidy layout. A <b>blank</b> cell means missing (see <code>bilirubin_mg_dl</code>, row 1).</div>
              ${dtable(
								[{ t: "patient_id" }, { t: "arm" }, { t: "sex" }, { t: "child_pugh_score" }, { t: "albumin_g_dl" }, { t: "bilirubin_mg_dl" }, { t: "afp_ng_ml" }, { t: "afp_ge_400" }, { t: "os_time_months" }, { t: "os_event" }],
								[
									["RW-00001", "Atezo+Bev", "Male", "5", "4.3", "", "141.0", "0", "4.00", "0"],
									["RW-00002", "Sorafenib", "Male", "5", "3.1", "1.11", "10.6", "0", "8.82", "0"],
									["RW-00003", "Sorafenib", "Male", "5", "3.5", "1.04", "4.6", "0", "14.26", "1"],
									["RW-00004", "Atezo+Bev", "Female", "5", "3.4", "1.75", "5506.1", "1", "6.41", "0"],
								],
							)}
            </div>
            <div class="data-tab" data-tab-idx="1">
              <div class="data-caption">Red columns differ: <b>AtezoBev</b>, <b>M/F</b>, albumin <b>g/L</b>, bilirubin <b>µmol/L</b>, <code class="hl">os_death</code> — all need recoding.</div>
              ${dtable(
								[{ t: "patient_id" }, { t: "treatment", hl: 1 }, { t: "sex", hl: 1 }, { t: "cp_score" }, { t: "albumin_g_L", hl: 1 }, { t: "bilirubin_umol_L", hl: 1 }, { t: "afp" }, { t: "afp_over_400", hl: 1 }, { t: "os_months" }, { t: "os_death", hl: 1 }],
								[
									["RW-00321", "Sorafenib", "F", "5", "41.0", "7.9", "16195.0", "Yes", "21.92", "0"],
									["RW-00322", "AtezoBev", "M", "5", "42.0", "20.0", "3.5", "No", "3.57", "0"],
									["RW-00323", "Sorafenib", "M", "5", "35.0", "11.3", "34.0", "No", "9.86", "0"],
									["RW-00324", "AtezoBev", "M", "5", "36.0", "15.4", "857.7", "Yes", "8.66", "1"],
								],
							)}
            </div>
            <div class="data-tab" data-tab-idx="2">
              <div class="data-caption">Different codes: <b>A+B/SOR</b>, <code class="hl">male</code> 1/0, Child–Pugh <code class="hl">A5/A6</code>, only <code class="hl">afp_high</code> — <b>no continuous AFP</b>.</div>
              ${dtable(
								[{ t: "record_id" }, { t: "regimen", hl: 1 }, { t: "male", hl: 1 }, { t: "child_pugh", hl: 1 }, { t: "alb" }, { t: "tbili" }, { t: "afp_high", hl: 1 }, { t: "time_os" }, { t: "event_os" }],
								[
									["RW-00606", "A+B", "1", "A5", "4.4", "1.16", "0", "2.04", "0"],
									["RW-00607", "SOR", "1", "A6", "3.8", "1.51", "0", "0.32", "0"],
									["RW-00608", "A+B", "1", "A5", "4.0", "0.73", "0", "13.20", "0"],
									["RW-00609", "A+B", "1", "A5", "4.5", "1.29", "0", "22.20", "0"],
								],
							)}
            </div>
          </div>
          <div class="data-hint">click a table to enlarge · then press ↑ ↓ to switch dialect in the zoomed view</div>
        </div>
      </div></div>`,
		notes: `<ul>
      <li>Make the point physically: before any statistics, you <b>open the raw files</b>. Tab through the three vendors so the audience sees the mess is real, not abstract.</li>
      <li>Alpha is tidy. On <b>Beta</b>, trace one row: albumin <b>41 g/L</b> (not 4.1 g/dL!), bilirubin in µmol/L, <code>AtezoBev</code>, <code>os_death</code>. On <b>Gamma</b>, there is <b>no continuous AFP</b> — only <code>afp_high</code>.</li>
      <li>Click a table to enlarge and read the columns; press <b>↑ ↓</b> in the zoom to flip between dialects side-by-side. Then: “this is what Claude Code has to reconcile.” → the harmonise session.</li>
    </ul>`,
	});

	/* 3 — ACT 1 SESSION: harmonise & pool ------------------------------- */
	scenes.push({
		kind: "session",
		act: "Act I · Data aggregation",
		title: "Session — harmonise & pool",
		duration: 5,
		stepNotes: [
			"type the prompt (zoom)",
			"Claude reads a Beta + Gamma file",
			"it writes the harmoniser",
			"runs it — round-trip PASS, N=1800",
			"per-hospital atezo share = the confounder",
			"land it",
		],
		html: `
      <div class="eyebrow">${spark} Act I · Live session</div>
      <h2 class="scene-h">“Harmonise the ten dialects and pool them.”</h2>
      ${mac(
				"claude — harmonise 10 hospitals · Fable 5",
				[
					asst(
						2,
						`<p>I'll inspect the three dialects first, write one reconciler, and validate the round-trip against the answer key.</p>`,
					),
					tool(
						2,
						"Ran",
						"Read H02_Riverside_General.csv, H03_Metropolitan_Cancer_Ctr.csv",
						"hospitals/ · Beta + Gamma samples",
						`Beta : treatment=<span class="hl">AtezoBev</span>  sex=M/F  albumin_<span class="hl">g_l</span>  bili_<span class="hl">umol_l</span>  os_death
Gamma: regimen=<span class="hl">A+B</span>/SOR  child_pugh=<span class="hl">A5</span>/A6  <span class="hl">afp_high</span> only  time_os/event_os`,
					),
					tool(
						3,
						"Ran",
						"Write harmonize_hospitals.py",
						"harmonize_hospitals.py · reconciler",
						`<span class="dim"># per-dialect column map + unit conversions</span>
albumin_g_dl = albumin_g_l / <span class="hl">10</span>
bilirubin_mg_dl = bilirubin_umol_l / <span class="hl">17.1</span>
child_pugh_score = int(child_pugh.lstrip("A"))   <span class="dim"># "A5" → 5</span>
arm = {"AtezoBev":"Atezo+Bev","A+B":"Atezo+Bev","SOR":"Sorafenib",...}
df = df.merge(meta, on="<span class="hl">hospital_id</span>")   <span class="dim"># join site type/region</span>`,
					),
					tool(
						4,
						"Ran",
						"python harmonize_hospitals.py",
						"$ .venv/bin/python harmonize_hospitals.py",
						`Harmonised 10 hospitals -> <span class="hl">1800 patients</span>, 27 cols
Round-trip validation vs answer key: <span class="hl">PASS</span>`,
					),
					tool(
						5,
						"Ran",
						"atezo share by hospital",
						"$ python - (pooled.groupby('hospital_id'))",
						`H01 <span class="hl">0.659</span> Academic   H04 <span class="hl">0.379</span> Community
H03 0.613 Academic   H07 <span class="hl">0.347</span> Community
H06 0.648 Academic   H10 0.446 Regional
<span class="dim"># academic centres prescribe atezo ~2x more → site-level confounding</span>`,
					),
					say(
						6,
						`Pooled: <b>N = 1800</b> (Atezo 962 / Sora 838). Validated against the key. But treatment share swings <b>35% → 66%</b> by hospital — the cohort is <b>confounded by indication</b>. That's Act II.`,
					),
				].join(""),
				"Read the three EHR dialects, write one harmoniser that reconciles columns/units/codes, pool all 10 files, join hospitals_meta, and validate the round-trip.",
				1,
			)}`,
		notes: `<ul>
      <li><span class="cue">beat 1</span> Let the prompt <b>type</b> — the window zooms. Say out loud what a good prompt contains: the <b>target</b> (one schema), the <b>hard parts</b> (units, codes), and a <b>check</b> (round-trip vs key). Specify the verification and the agent will do it.</li>
      <li><span class="cue">beat 4</span> The <b>PASS</b> line is the trust moment — the harmoniser reproduces the answer key exactly. I didn't eyeball it.</li>
      <li><span class="cue">beat 5</span> The atezo-share table is the punchline: prescribing culture varies by site → a real confounder → sets up PSM. Don't rush this.</li>
    </ul>`,
	});

	/* 4 — ACT 2 CONCEPT: confounding ------------------------------------ */
	scenes.push({
		kind: "concept",
		act: "Act II · De-confounding",
		title: "Why the naive answer lies",
		duration: 3,
		stepNotes: [
			"the trap: naive HR looks great",
			"why it's biased",
			"the fix in one line",
		],
		html: `
      <div class="eyebrow">${spark} Act II · Causal inference</div>
      <h2 class="scene-h">The naive hazard ratio is <span style="color:var(--clay-emph)">too good to be true.</span></h2>
      <div class="cols">
        <div class="stack">
          <div class="stat-row">
            <div class="stat" data-step="1"><div class="v clay">0.505</div><div class="k">naive, unadjusted OS HR</div><div class="ci">95% CI 0.43–0.60</div></div>
            <div class="stat" data-step="1"><div class="v grey">0.58</div><div class="k">the truth (built into the DGP)</div><div class="ci">= published trial</div></div>
          </div>
          <p class="scene-lede" data-step="2">Treatment wasn't randomised. Atezo+Bev patients were <b>healthier to start</b> — so the raw comparison <b>over-states</b> the benefit.</p>
        </div>
        <div class="stack">
          <ul class="beats">
            <li data-step="2"><span class="mk">${ic("check")}</span><div>All confounders are <b>measured</b> and in the CSV — no unmeasured confounding by design</div></li>
            <li data-step="2"><span class="mk">${ic("check")}</span><div>That's the <b>ignorability</b> assumption PSM needs to recover a causal effect</div></li>
            <li data-step="3"><span class="mk">${ic("arrowRight")}</span><div>Estimate a propensity score, match treated↔control on it, and the imbalance disappears</div></li>
          </ul>
          <div class="callout" data-step="3">${spark}<div><b>Estimand first, method second.</b> We want the effect of the drug, not of being the kind of patient who gets the drug.</div></div>
        </div>
      </div>`,
		notes: `<ul>
      <li>This is the conceptual heart of the talk. Sell the intuition <b>before</b> the machinery: 0.505 vs 0.58 — the naive number is <b>more extreme</b>, and that gap is confounding, not the drug.</li>
      <li>Stress the honest caveat: PSM only works because here <b>all</b> confounders are measured. In real life you argue for that assumption; you don't get it for free.</li>
      <li><span class="cue">beat 3</span> Tee up the session: “Watch me ask for the whole PSM workflow — estimate, match, and <b>check balance</b> — in one prompt.”</li>
    </ul>`,
	});

	/* 5 — ACT 2 SESSION: PSM -------------------------------------------- */
	scenes.push({
		kind: "session",
		act: "Act II · De-confounding",
		title: "Session — propensity-score matching",
		duration: 6,
		stepNotes: [
			"type prompt (zoom)",
			"fit PS on 11 confounders",
			"1:1 caliper match → 706 pairs",
			"balance table: |SMD| collapses",
			"Love plot + overlap",
			"matched HR 0.578 recovers truth",
		],
		html: `
      <div class="eyebrow">${spark} Act II · Live session</div>
      <h2 class="scene-h">“Estimate a propensity score, match 1:1, and prove the balance.”</h2>
      ${mac(
				"claude — psm_imbrave150.py · Fable 5",
				[
					asst(
						2,
						`<p>Logistic PS on the 11 measured confounders, 1:1 nearest-neighbour with a 0.2·SD caliper on logit(PS), then standardised mean differences before vs after.</p>`,
					),
					tool(
						2,
						"Ran",
						"fit propensity model",
						"$ python psm_imbrave150.py  ·  [2]",
						`Propensity model fitted on <span class="hl">11 covariates</span>
(age, ecog, child_pugh, afp&ge;400, MVI, EHS, bclc_C, albi&ge;2, varices, sex, asia)`,
					),
					tool(
						3,
						"Ran",
						"1:1 caliper matching",
						"$ ... [3]",
						`[1] NAIVE unadjusted OS HR : <span class="hl">0.505</span> (0.43-0.60)  &lt;- biased
[3] 1:1 caliper matching -> <span class="hl">706 matched pairs</span> (1412 patients, caliper=0.114)`,
					),
					tool(
						4,
						"Ran",
						"covariate balance |SMD|",
						"$ ... [4]  rule of thumb |SMD| &lt; 0.10",
						`  covariate                before   after
  age                       0.210   <span class="hl">0.019</span>
  afp_ge_400                0.228   <span class="hl">0.017</span>
  macrovascular_invasion    0.225   <span class="hl">0.044</span>
  extrahepatic_spread       0.204   <span class="hl">0.038</span>
  albi_ge2                  0.178   <span class="hl">0.034</span>
  varices_at_baseline       0.176   <span class="hl">0.012</span>
  <span class="dim"># every covariate now well under 0.05</span>`,
					),
					fig(
						5,
						"love_plot.svg",
						"Love plot — standardised mean differences collapse below 0.1 after matching",
					),
					fig(
						5,
						"ps_overlap.svg",
						"Propensity-score overlap — good common support across arms",
					),
					tool(
						6,
						"Ran",
						"Cox on matched cohort",
						"$ ... [5] survival",
						`OS  HR (matched) : <span class="hl">0.578</span> (0.48-0.70)   [truth 0.58, trial 0.58]
PFS HR (matched) : <span class="hl">0.632</span> (0.55-0.72)
OS  HR (full-cohort regression adjustment) : <span class="hl">0.563</span>   <span class="dim"># agrees</span>`,
					),
					say(
						6,
						`From a biased <b>0.505</b> to a matched <b>0.578</b> — and regression adjustment independently lands at 0.563. Confounding removed; two methods agree.`,
					),
				].join(""),
				"Estimate a logistic propensity score on all measured confounders, do 1:1 caliper matching on logit(PS), report SMD balance before/after with a Love plot and overlap plot, then Cox on the matched cohort.",
				1,
			)}`,
		notes: `<ul>
      <li><span class="cue">beat 4</span> The balance table is the evidence a reviewer wants. Before: 0.18–0.23. After: all &lt; 0.05. Say “|SMD| &lt; 0.1 is the convention; we're comfortably under.”</li>
      <li><span class="cue">beat 5</span> Love plot = the picture of that table. Overlap plot = we're not extrapolating. These two plots pre-empt the two most common PSM objections.</li>
      <li><span class="cue">beat 6</span> Triangulation: PSM 0.578, regression 0.563. When two different assumptions agree, you believe it more. This is the moment to say “I now trust the effect.”</li>
    </ul>`,
	});

	/* 6 — ACT 3 CONCEPT: survival --------------------------------------- */
	scenes.push({
		kind: "concept",
		act: "Act III · Survival",
		title: "Why Kaplan–Meier, not percentages",
		duration: 2,
		stepNotes: ["censoring exists", "so use KM/Cox", "what we'll show"],
		html: `
      <div class="eyebrow">${spark} Act III · Time-to-event</div>
      <h2 class="scene-h">Patients are censored. Percentages lie; survival curves don't.</h2>
      <div class="cols">
        <ul class="beats">
          <li data-step="1"><span class="mk">1</span><div>Staggered accrual + one administrative cutoff → many patients are <b>still alive at last contact</b></div></li>
          <li data-step="1"><span class="mk">2</span><div>A raw “% dead” throws that information away; <b>Kaplan–Meier</b> uses every follow-up month</div></li>
          <li data-step="2"><span class="mk">3</span><div><b>Cox</b> gives the hazard ratio; <b>log-rank</b> tests the curve separation</div></li>
          <li data-step="3"><span class="mk">${ic("arrowRight")}</span><div>We run all three on the <b>matched</b> cohort — the de-confounded comparison</div></li>
        </ul>
        <div class="stack">
          <div class="callout" data-step="2">${spark}<div>The matched cohort keeps <b>706 pairs</b>. Now the KM curves compare like with like.</div></div>
          <div class="stat" data-step="3"><div class="v">1412</div><div class="k">patients in the matched survival analysis</div></div>
        </div>
      </div>`,
		notes: `<ul>
      <li>Quick conceptual scene — keep it to ~2 minutes. The audience mostly knows KM; the fresh point is that we run it on the <b>matched</b> cohort, so survival + causal inference compose.</li>
      <li>Foreshadow the payoff: “If matching worked, these curves should reproduce the randomised trial we never got to run.”</li>
    </ul>`,
	});

	/* 7 — ACT 3 SESSION: KM + Cox --------------------------------------- */
	scenes.push({
		kind: "session",
		act: "Act III · Survival",
		title: "Session — Kaplan–Meier & Cox",
		duration: 5,
		stepNotes: [
			"type prompt (zoom)",
			"KM fit + log-rank",
			"OS curve",
			"PFS curve",
			"we recovered the RCT",
		],
		html: `
      <div class="eyebrow">${spark} Act III · Live session</div>
      <h2 class="scene-h">“Plot KM for OS and PFS on the matched cohort, with the HR.”</h2>
      ${mac(
				"claude — survival on matched cohort · Fable 5",
				[
					asst(
						2,
						`<p>KaplanMeierFitter per arm, log-rank test, and CoxPH for the HR — on the 706 matched pairs.</p>`,
					),
					tool(
						2,
						"Ran",
						"KaplanMeierFitter + logrank",
						"$ python — lifelines on matched cohort",
						`Deaths: Atezo+Bev 24.7% | Sorafenib 39.4%
OS  HR : <span class="hl">0.578</span>  95% CI 0.48-0.70   log-rank p <span class="hl">&lt; 0.001</span>
12-mo OS: Atezo 70.0% vs Sora 57.8%`,
					),
					fig(
						3,
						"km_os_matched.svg",
						"Overall survival — PSM-matched cohort · HR 0.58, log-rank p < 0.001",
					),
					fig(
						4,
						"km_pfs_matched.svg",
						"Progression-free survival — PSM-matched cohort · HR 0.63",
					),
					say(
						5,
						`Matched OS HR <b>0.58</b> with clean curve separation — <b>identical to the randomised IMbrave150 trial</b> (Finn 2020, HR 0.58). We recovered the RCT answer from messy observational data.`,
					),
				].join(""),
				"On the matched cohort, fit Kaplan–Meier survival by arm for OS and PFS, run the log-rank test, fit Cox for the hazard ratio, and render publication-clean curves.",
				1,
			)}`,
		notes: `<ul>
      <li><span class="cue">beat 3</span> Let the OS curve breathe on screen. Point at the separation and the shaded CIs. Note the median lines and the at-risk logic.</li>
      <li><span class="cue">beat 5</span> The emotional peak of the analysis: matched HR 0.58 = the real trial's 0.58. Say it plainly — “observational data, done carefully, reproduced the randomised result.” Then immediately temper: consistency ≠ proof; that's why we do subgroups and robustness next.</li>
    </ul>`,
	});

	/* 8 — ACT 4 SESSION: subgroup forest -------------------------------- */
	scenes.push({
		kind: "session",
		act: "Act IV · Subgroups",
		title: "Session — subgroup forest",
		duration: 4,
		stepNotes: [
			"type prompt (zoom)",
			"compute HR per subgroup",
			"the forest plot",
			"consistency = no red flags",
		],
		html: `
      <div class="eyebrow">${spark} Act IV · Live session</div>
      <h2 class="scene-h">“Is the effect consistent across subgroups?”</h2>
      ${mac(
				"claude — subgroup forest · Fable 5",
				[
					asst(
						2,
						`<p>Cox HR + 95% CI within each pre-specified subgroup on the matched cohort — region, ECOG, AFP, macrovascular invasion, BCLC, etiology.</p>`,
					),
					tool(
						2,
						"Ran",
						"per-subgroup Cox",
						"$ python — matched cohort, by subgroup",
						`Overall               0.58 (0.48-0.70)  n=1412
Region: Asia          0.61 (0.47-0.80)  Rest 0.55 (0.42-0.72)
ECOG 0                0.61  ECOG 1 0.54
AFP&ge;400               0.59  AFP&lt;400 0.54
Macrovasc. invasion   yes 0.61  no 0.54
BCLC C 0.59   BCLC A/B 0.51   HBV 0.63  HCV 0.56  Nonviral 0.53`,
					),
					fig(
						3,
						"forest_subgroup.svg",
						"Subgroup OS hazard ratios — every point estimate 0.51–0.63, every CI excludes 1.0",
					),
					say(
						4,
						`All 13 subgroups sit between <b>0.51 and 0.63</b>; every confidence interval <b>excludes 1.0</b>. No subgroup reverses — the benefit is consistent, with no data-dredged surprises.`,
					),
				].join(""),
				"Compute the OS hazard ratio and 95% CI within each pre-specified subgroup on the matched cohort, and draw a standard forest plot with a reference line at HR = 1.",
				1,
			)}`,
		notes: `<ul>
      <li>Frame subgroups honestly: they are <b>hypothesis-generating</b>, under-powered, and prone to false positives. The right reading here is <b>consistency</b>, not hunting for a winner.</li>
      <li><span class="cue">beat 3</span> Trace the forest: all squares left of 1.0, all whiskers clear of it. Note BCLC A/B is widest (smallest n) — honesty about precision.</li>
      <li>Anticipate the question “did you correct for multiplicity?” — answer: these are descriptive/consistency checks, not confirmatory tests.</li>
    </ul>`,
	});

	/* 9 — ACT 5 SESSION: robustness ------------------------------------- */
	scenes.push({
		kind: "session",
		act: "Act V · Robustness",
		title: "Session — multiverse & TMLE",
		duration: 5,
		stepNotes: [
			"type prompt (zoom)",
			"120-spec multiverse",
			"the multiverse figure",
			"TMLE doubly-robust",
			"one conclusion, many roads",
		],
		html: `
      <div class="eyebrow">${spark} Act V · Live session</div>
      <h2 class="scene-h">“How much does the answer depend on my choices?”</h2>
      ${mac(
				"claude — robustness · Fable 5",
				[
					asst(
						2,
						`<p>A specification multiverse — 120 defensible analytic pipelines — plus a doubly-robust TMLE that targets the marginal risk difference instead of the hazard ratio.</p>`,
					),
					tool(
						2,
						"Ran",
						"robustness_multiverse.py",
						"$ python robustness_multiverse.py  ·  120 specs",
						`Adjusted specifications : <span class="hl">120</span>  (PSM 90 / regression 15 / IPTW 15)
median HR <span class="hl">0.583</span>   IQR 0.560-0.608   range 0.515-0.699
below HR 1.0 : <span class="hl">100%</span>  (every spec favours atezo+bev)`,
					),
					fig(
						3,
						"robustness_multiverse.png",
						"Specification multiverse — 120 analytic choices, HR distribution tight around 0.58",
					),
					tool(
						4,
						"Ran",
						"tmle_demo.py",
						"$ python tmle_demo.py  ·  death by 12 months",
						`NAIVE complete-case : -0.228   &lt;- biased
G-computation       : -0.168
IPTW                : -0.140
AIPW (doubly robust): -0.144
TMLE (doubly robust): <span class="hl">-0.150</span> (SE 0.037)  95% CI [-0.221, -0.078]
<span class="dim">TRUE from DGP       : -0.154   ← TMLE lands on the truth</span>`,
					),
					say(
						5,
						`Across <b>120 specifications</b> the HR barely moves (IQR 0.56–0.61); a doubly-robust TMLE hits the ground truth at <b>−0.15</b>. The conclusion isn't an artifact of one lucky pipeline.`,
					),
				].join(""),
				"Run a specification multiverse across reasonable PSM/regression/IPTW choices and summarise the HR distribution; then a doubly-robust TMLE/AIPW for the 12-month risk difference, compared against the true DGP value.",
				1,
			)}`,
		notes: `<ul>
      <li>This is the scene that separates a careful analyst from a lucky one. The multiverse answers “garden of forking paths” — I didn't cherry-pick a pipeline; 120 of them agree.</li>
      <li><span class="cue">beat 4</span> TMLE targets a <b>different estimand</b> (marginal risk difference), on a different scale, and still recovers the truth (−0.150 vs −0.154). Say “estimand first, method second” again — callback to Act II.</li>
      <li>Great place to pause for questions before we switch from analysis to writing.</li>
    </ul>`,
	});

	/* 10 — ACT 6 CONCEPT: IMRaD writing workflow ------------------------ */
	scenes.push({
		kind: "concept",
		act: "Act VI · Manuscript",
		title: "The writing workflow",
		duration: 3,
		stepNotes: [
			"Methods from the scripts",
			"Results from the outputs",
			"Discussion cross-references both",
			"assemble IMRaD",
		],
		html: `
      <div class="eyebrow">${spark} Act VI · From analysis to paper</div>
      <h2 class="scene-h">The manuscript is <span style="color:var(--clay-emph)">generated from the evidence</span>, not narrated from memory.</h2>
      <p class="scene-lede">Every section has a source. Methods ← <b>scripts</b>. Results ← <b>outputs</b>. Discussion ← both, <b>cross-referenced</b>.</p>
      <div class="imrad">
        <div class="card" data-step="1"><div class="lbl">Methods</div><div class="src">Written from the analysis <b>scripts</b> — the exact model, caliper, covariates.</div><div class="arrow-in">← harmonize · psm · robustness .py</div></div>
        <div class="card" data-step="2"><div class="lbl">Results</div><div class="src">Written from the <b>console outputs</b> — verbatim HRs, CIs, balance, p-values.</div><div class="arrow-in">← run logs + figures</div></div>
        <div class="card" data-step="3"><div class="lbl">Discussion</div><div class="src">Written from Methods + Results; each sentence tagged to its evidence.</div><div class="arrow-in">← Methods + Results + xrefs</div></div>
        <div class="card" data-step="4"><div class="lbl">Manuscript</div><div class="src">Assembled IMRaD with a structured abstract and honest limitations.</div><div class="arrow-in">← all of the above</div></div>
      </div>
      <div style="margin-top:22px" data-step="4"><div class="callout">${spark}<div><b>Traceability is the point.</b> Every number in the paper can be clicked back to the script and the run that produced it — no hallucinated statistics.</div></div></div>`,
		notes: `<ul>
      <li>This is the slide that makes methodologists lean in. The failure mode of “LLM writes my paper” is invented numbers. We defuse it structurally: the model only writes from artifacts it just produced.</li>
      <li>Explain the cross-reference tags they'll see next: little monospace chips like <span class="cue">psm.py [5]</span> pinning each claim to its source. That's how you'd defend the paper to a reviewer — or to yourself in six months.</li>
    </ul>`,
	});

	/* 11 — ACT 6 SESSION: Methods --------------------------------------- */
	scenes.push({
		kind: "session",
		act: "Act VI · Manuscript",
		title: "Session — write Methods",
		duration: 4,
		stepNotes: [
			"type prompt (zoom)",
			"Claude reads the scripts",
			"drafts Methods from them",
		],
		html: `
      <div class="eyebrow">${spark} Act VI · Live session</div>
      <h2 class="scene-h">“Write the Methods — read it off the actual scripts.”</h2>
      ${mac(
				"claude — draft Methods · Fable 5",
				[
					asst(
						2,
						`<p>Reading the pipeline so the Methods reflect what the code truly does, not what I assume.</p>`,
					),
					tool(
						2,
						"Ran",
						"Read harmonize_hospitals.py, psm_imbrave150.py, robustness_multiverse.py",
						"3 files · the analysis pipeline",
						`<span class="dim"># extracted: 11-covariate logistic PS · 1:1 NN caliper 0.2*SD on logit(PS)
# balance = standardised mean differences · Cox on matched · 120-spec multiverse</span>`,
					),
					asst(
						3,
						`<p><b>Methods.</b> Ten hospital extracts in three EHR dialects were harmonised to a common schema (unit conversions, code recoding, site-metadata join) and pooled (N&nbsp;=&nbsp;1800). Treatment was atezolizumab–bevacizumab versus sorafenib. A logistic propensity score was estimated from eleven measured confounders (age, ECOG, Child–Pugh score, AFP≥400, macrovascular invasion, extrahepatic spread, BCLC-C, ALBI≥2, varices, sex, region). Patients were matched 1:1 by nearest neighbour on the logit propensity score with a 0.2·SD caliper; balance was assessed by standardised mean differences. Overall and progression-free survival were compared by Kaplan–Meier, log-rank, and Cox proportional-hazards models on the matched cohort. Robustness was evaluated with a 120-specification multiverse and a doubly-robust TMLE for the 12-month risk difference.</p>`,
					),
				].join(""),
				"Read harmonize_hospitals.py, psm_imbrave150.py and robustness_multiverse.py, and write a Methods section that states the exact propensity model, matching rule, balance metric, and survival models — no invented detail.",
				1,
			)}`,
		notes: `<ul>
      <li>The move to teach here: <b>ground the prose in the source</b>. Claude reads the scripts, then writes Methods. If the code says caliper 0.2·SD, the Methods say 0.2·SD. No drift.</li>
      <li>Point out this also catches <b>your</b> errors — if the write-up and the code disagree, one of them is wrong, and you find out now.</li>
    </ul>`,
	});

	/* 12 — ACT 6 SESSION: Results (with xrefs) -------------------------- */
	scenes.push({
		kind: "session",
		act: "Act VI · Manuscript",
		title: "Session — write Results",
		duration: 4,
		stepNotes: [
			"type prompt (zoom)",
			"Results pulled from run logs",
			"every number carries an xref",
		],
		html: `
      <div class="eyebrow">${spark} Act VI · Live session</div>
      <h2 class="scene-h">“Write Results from the run logs — tag every number to its source.”</h2>
      ${mac(
				"claude — draft Results · Fable 5",
				[
					asst(
						2,
						`<p>Pulling numbers straight from the captured console output so nothing is paraphrased.</p>`,
					),
					asst(
						3,
						`<p><b>Results.</b> The pooled cohort comprised 1800 patients (962 atezolizumab–bevacizumab, 838 sorafenib) across ten hospitals, with atezolizumab use varying by site from 35% to 66% <span class="xref">harmonize.py</span>. The unadjusted OS hazard ratio was biased at 0.505 (0.43–0.60) <span class="xref">psm.py&nbsp;[1]</span>. Caliper matching produced 706 pairs with all standardised mean differences below 0.05 <span class="xref">psm.py&nbsp;[4]</span>. In the matched cohort the OS HR was 0.578 (0.48–0.70), log-rank p&nbsp;&lt;&nbsp;0.001, and PFS HR 0.632 <span class="xref">psm.py&nbsp;[5]</span>. Regression adjustment (0.563) and a doubly-robust TMLE (risk difference −0.150; 95% CI −0.221 to −0.078) agreed <span class="xref">tmle.py</span>. Across 120 specifications the median HR was 0.583 (IQR 0.560–0.608), all below 1.0 <span class="xref">multiverse.py</span>; subgroup HRs ranged 0.51–0.63 <span class="xref">forest</span>.</p>`,
					),
				].join(""),
				"Write the Results section using only the captured console numbers. Attach a cross-reference tag to every quantitative claim pointing to the script and step that produced it.",
				1,
			)}`,
		notes: `<ul>
      <li><span class="cue">beat 3</span> Walk one sentence and its chip: “matched OS HR 0.578 … <b>psm.py [5]</b>.” That chip is the receipt. A reviewer can open psm_imbrave150.py, step [5], and see 0.578.</li>
      <li>This is the antidote to the #1 fear about AI writing. The numbers are quoted, not generated, and each is pinned to a reproducible source.</li>
    </ul>`,
	});

	/* 13 — ACT 6 SESSION: Discussion ------------------------------------ */
	scenes.push({
		kind: "session",
		act: "Act VI · Manuscript",
		title: "Session — draft Discussion",
		duration: 4,
		stepNotes: [
			"type prompt (zoom)",
			"Discussion reasons over Methods+Results",
			"honest limitations",
		],
		html: `
      <div class="eyebrow">${spark} Act VI · Live session</div>
      <h2 class="scene-h">“Now the Discussion — reason over Methods and Results, and be honest.”</h2>
      ${mac(
				"claude — draft Discussion · Fable 5",
				[
					asst(
						2,
						`<p>Synthesising: what the numbers mean, why they're credible, and where they could break.</p>`,
					),
					asst(
						3,
						`<p><b>Discussion.</b> Careful adjustment moved the estimate from a biased 0.505 to a matched 0.578, recovering the effect built into the data-generating process and matching the randomised IMbrave150 trial (HR 0.58) <span class="xref">psm.py&nbsp;[5]</span>. Agreement between propensity matching, regression adjustment, and TMLE — methods relying on different assumptions — makes residual modelling bias unlikely <span class="xref">tmle.py</span>. The specification multiverse shows the conclusion is not an artifact of one analytic path <span class="xref">multiverse.py</span>.</p>`,
					),
					asst(
						4,
						`<p><b>Limitations.</b> These data are <b>fully synthetic</b> and cannot support any clinical claim. Propensity methods assume no unmeasured confounding; here that holds by construction, but real cohorts rarely guarantee it. Subgroup analyses are hypothesis-generating and under-powered. The estimand is a marginal or conditional average effect, not an individual one.</p>`,
					),
				].join(""),
				"Draft the Discussion from the Methods and Results: interpret the shift from naive to adjusted, argue credibility from method-agreement and the multiverse, and state honest limitations including the synthetic nature and the no-unmeasured-confounding assumption.",
				1,
			)}`,
		notes: `<ul>
      <li>The Discussion is where judgement lives — and where an LLM can bluff. Counter it by forcing it to reason from Methods + Results only, and to <b>lead with limitations</b>.</li>
      <li><span class="cue">beat 4</span> Read the limitations aloud. The synthetic-data caveat is non-negotiable; the no-unmeasured-confounding caveat is the intellectually honest one. A good paper is confident about method and humble about assumptions.</li>
    </ul>`,
	});

	/* 14 — ACT 6 REVEAL: assembled manuscript --------------------------- */
	scenes.push({
		kind: "manuscript",
		act: "Act VI · Manuscript",
		title: "The assembled manuscript",
		duration: 3,
		stepNotes: [
			"title + abstract",
			"Methods + Results",
			"Discussion + limitations",
		],
		html: `
      <div class="eyebrow">${spark} Act VI · The deliverable</div>
      <h2 class="scene-h" style="margin-bottom:14px">One session in, a submission-ready draft out.</h2>
      <div class="manuscript">
        <div class="msec on"><div class="mtitle">Recovering a randomised treatment effect from pooled multi-hospital observational data: a propensity-score and doubly-robust case study (synthetic IMbrave150)</div>
        <div class="mauthors">H.-T. Lin · Analysis performed with Claude Code · Teaching example, synthetic data</div></div>
        <div class="mcols">
          <div class="msec" data-step="1"><h4>Abstract</h4>
            <p><b>Background.</b> Observational HCC cohorts pooled across hospitals are confounded by indication. We test whether a careful causal-inference workflow recovers a known treatment effect in a fully synthetic, IMbrave150-modelled cohort.</p>
            <p><b>Methods.</b> Ten EHR extracts in three dialects were harmonised and pooled (N=1800). A logistic propensity score on eleven confounders drove 1:1 caliper matching; survival was compared by Kaplan–Meier and Cox, with TMLE and a 120-spec multiverse for robustness.</p>
            <p><b>Results.</b> The naive OS HR (0.505) was biased; matching (706 pairs, all |SMD|&lt;0.05) gave OS HR 0.578 (0.48–0.70), concordant with regression (0.563), TMLE (−0.150), and the multiverse median (0.583).</p>
            <p><b>Conclusions.</b> A disciplined pipeline recovered the built-in effect (HR 0.58) — matching the real trial — illustrating method, not evidence about the drugs.</p></div>
          <div class="msec" data-step="2"><h4>Methods</h4>
            <p>Harmonisation reconciled column names, units (albumin, bilirubin), and codes across Alpha/Beta/Gamma dialects, joining site metadata on hospital_id. Propensity: logistic regression on age, ECOG, Child–Pugh, AFP≥400, macrovascular invasion, extrahepatic spread, BCLC-C, ALBI≥2, varices, sex, region. Matching: 1:1 nearest neighbour, 0.2·SD caliper on logit(PS). Balance: standardised mean differences. Survival: KM, log-rank, Cox on the matched cohort.</p>
            <h4>Results</h4>
            <p>Atezolizumab use varied 35–66% by hospital <span class="xref">harmonize.py</span>. Naive OS HR 0.505 <span class="xref">psm.py [1]</span>; matched OS HR 0.578, PFS 0.632, log-rank p&lt;0.001 <span class="xref">psm.py [5]</span>; all subgroup HRs 0.51–0.63 <span class="xref">forest</span>; multiverse median 0.583, 100% &lt;1.0 <span class="xref">multiverse.py</span>.</p></div>
          <div class="msec" data-step="3"><h4>Discussion</h4>
            <p>Adjustment moved the estimate from 0.505 to 0.578, recovering the generative truth and the randomised trial. Concordance across matching, regression, and TMLE — different assumptions — argues against residual bias.</p>
            <h4>Limitations</h4>
            <p>Data are synthetic and support no clinical claim. Propensity methods assume no unmeasured confounding, true here by construction only. Subgroups are hypothesis-generating.</p></div>
        </div>
      </div>`,
		notes: `<ul>
      <li>Let the finished artifact land. This is what an hour bought: a structured abstract, Methods, Results, Discussion, and limitations — every number traceable.</li>
      <li>Be explicit about what this is <b>not</b>: it's a first draft and a teaching artifact, not a finished submission and not evidence about atezolizumab. You still bring the judgement, the literature, and the accountability.</li>
      <li><span class="cue">beat 3</span> Transition to the close: “So what actually made this trustworthy?”</li>
    </ul>`,
	});

	/* 15 — CLOSER: the pattern + takeaways ------------------------------ */
	scenes.push({
		kind: "concept",
		act: "Close",
		title: "What made it trustworthy",
		duration: 4,
		stepNotes: ["takeaway 1", "2", "3", "4"],
		html: `
      <div class="eyebrow">${spark} The pattern worth stealing</div>
      <h2 class="scene-h">It wasn't the model. It was the <span style="color:var(--clay-emph)">workflow.</span></h2>
      <div class="takeaways">
        <div class="takeaway" data-step="1"><div class="n">1</div><div><div class="t">Specify the check, not just the task</div><div class="d">“Validate the round-trip against the key,” “prove the balance,” “tag every number.” The agent does what you make verifiable.</div></div></div>
        <div class="takeaway" data-step="2"><div class="n">2</div><div><div class="t">Triangulate before you believe</div><div class="d">PSM, regression, TMLE, and a 120-spec multiverse agreeing is worth more than any single HR.</div></div></div>
        <div class="takeaway" data-step="3"><div class="n">3</div><div><div class="t">Ground the writing in artifacts</div><div class="d">Methods from scripts, Results from logs, every claim cross-referenced. No hallucinated statistics.</div></div></div>
        <div class="takeaway" data-step="4"><div class="n">4</div><div><div class="t">Fidelity first, polish second</div><div class="d">Run the true pipeline, verify it, then curate. This talk is that principle applied to itself.</div></div></div>
      </div>
      <div style="margin-top:26px" data-step="4"><div class="callout">${spark}<div>Claude Code didn't replace the statistician. It <b>compressed the distance</b> between a question and a defensible, reproducible answer — and kept the receipts.</div></div></div>`,
		notes: `<ul>
      <li>Land the thesis: the trust came from the <b>workflow</b>, and the workflow is model-agnostic. These four habits transfer to any analysis.</li>
      <li>Repeat #1 — it's the highest-leverage idea for the audience: <b>make the task verifiable and the agent will verify it.</b></li>
      <li>Keep the human-in-the-loop framing: you own the estimand, the assumptions, and the accountability. The tool keeps receipts.</li>
    </ul>`,
	});

	/* 16 — END: reproduce ----------------------------------------------- */
	scenes.push({
		kind: "title",
		act: "Close",
		title: "Thank you / reproduce",
		duration: 2,
		html: `
      <div class="title-wordmark">${spark} Claude Code <span class="pill">Reproduce it yourself</span></div>
      <h1 class="display" style="font-size:clamp(28px,4.6vw,54px)">Thank you.</h1>
      <p class="subhead">The whole pipeline is deterministic and open — fixed seeds, byte-for-byte reproducible.</p>
      <div class="stack" style="margin-top:30px;max-width:640px">
        <div class="figure-card" style="background:var(--bg-page)"><pre style="font-family:var(--font-mono);font-size:14px;line-height:1.7;color:var(--text);margin:0;padding:6px 4px">make setup     <span style="color:var(--text-faint)"># venv + deps</span>
make data      <span style="color:var(--text-faint)"># 10 hospitals + randomised trial</span>
make analyze   <span style="color:var(--text-faint)"># harmonise · PSM · TMLE</span>
make figure    <span style="color:var(--text-faint)"># robustness multiverse</span></pre></div>
      </div>
      <div class="title-meta">
        <div class="item"><div class="k">Source study</div><div class="v">Finn RS et al., NEJM 2020;382:1894</div></div>
        <div class="item"><div class="k">Data</div><div class="v">100% synthetic · teaching only</div></div>
        <div class="item"><div class="k">Keys</div><div class="v">S speaker · O overview · F full · ? help</div></div>
      </div>`,
		notes: `<ul>
      <li>Close on reproducibility — the credibility backstop. Anyone can run <span class="cue">make</span> and get the same CSVs and the same numbers you just saw.</li>
      <li>Restate the caveat one final time: synthetic data, teaching example, no clinical claims. Then open the floor.</li>
      <li>Thank the room. Offer the repo.</li>
    </ul>`,
	});

	/* ---- 繁體中文講稿（按場景順序，按 i 切換顯示） ---- */
	const zhNotes = [
		// 0 Title
		`<ul>
      <li>開場放輕鬆。今天要看的是<b>流程</b>，不是結果炫耀——目標是讓大家離場時知道「怎麼一步步操作 Claude Code 走完一整份分析」。</li>
      <li>先把誠實講在前面：這批資料<b>完全是合成的</b>，照著真實的 IMbrave150 試驗（Finn 2020, NEJM）建模，沒有任何真實病人。我們教的是方法，數字剛好落在試驗附近而已。</li>
      <li>這裡的主角是 agent（AI 代理，也就是會自己動手去讀檔、跑程式的 AI，不只是陪你聊天）。你看到的每個結果，它都是真的去執行出來的。</li>
      <li>預告整條主線：亂七八糟的原始資料 → 因果推論 → 存活分析 → 次族群 → 穩健性檢驗 → 最後生出一篇論文。</li>
      <li><span class="cue">key</span> 現在按 <b>S</b> 確認講者計時器有在跑；按 <b>→</b> 前進；按 <b>i</b> 可以切換中英文講稿。</li>
    </ul>`,
		// 1 question + map
		`<ul>
      <li>先問全場：「在座有多少人接手過來自不只一個院所的資料？」——幾乎每個人都舉手。這個痛就是今天的鉤子。</li>
      <li>核心問題就寫在投影片上：Claude Code 能不能帶我從雜亂的原始電子病歷，一路走到一篇站得住腳的論文——而且我敢不敢信它？</li>
      <li>節點一個一個亮出來，帶著大家走這六站：整併資料、去除混雜（confounding，就是兩組病人本來條件就不一樣，害你把病人的差別誤當成藥效）、存活分析、次族群、穩健性、論文。每一站就是這場演講的一章。</li>
      <li><span class="cue">beat 3</span> 把信任這件事講清楚：我<b>沒有</b>叫 Claude 編一個漂亮故事。我是真的去跑那些程式、拿結果去對「答案鍵」（事先算好的正確答案，用來核對 AI 跑得對不對），對上了<b>之後</b>才策展重演。這時說出那句話——「先忠實，後打磨」。</li>
    </ul>`,
		// 2 dialect concept
		`<ul>
      <li>這一頁撐得起整場演講：真實世界的資料<b>從來不是</b>一份乾淨的 CSV。停在單位陷阱上多講兩句——albumin 用 g/L 還是 g/dL，差的是 10 倍；漏看就默默算錯，而且不會有人跳出來提醒你。</li>
      <li>三家醫院、三種電子病歷「方言」，欄位名、性別寫法、單位、甚至用藥代碼全都不一樣，你得自己發明一套統一的規格把它們對齊。</li>
      <li>Gamma 這家<b>沒有連續的 AFP</b>數值，只有「是否 ≥400」這個旗標。這剛好是 PSM（傾向分數配對，把有用藥和沒用藥的病人依條件一對一配起來、讓兩組站上同一起跑點再比）唯一需要的——是個很好的教學點：「量測到 estimand（你真正想估的那個量）需要的東西就夠了」。</li>
      <li>還有一個坑：院所類型和地區根本不在病人檔裡，而是躺在 <code>hospitals_meta.csv</code>，要靠 <code>hospital_id</code> 併進來才有。</li>
      <li><span class="cue">beat 5</span> 收尾轉場：「我可以自己手寫這個整併程式……或者，我可以把目標規格用白話描述給 Claude Code，讓它去把這幾種方言喬到一致。」→ 進下一幕。</li>
    </ul>`,
		// 3 data viewer
		`<ul>
      <li>開場先做一個實體動作:還沒跑任何統計,第一件事是把<b>原始檔案打開來親眼看</b>。這是刻意的——讓台下看到「亂」是真的,不是我在抽象講講。</li>
      <li>逐頁切三家醫院,讓大家感受到三種 EHR「方言」(每家醫院匯出的欄位名、單位、代碼都不一樣)。Alpha(H01)最乾淨、格式標準;<b>空白格就代表資料缺漏</b>(看 <code>bilirubin_mg_dl</code> 第一列)。</li>
      <li>Beta(H02)帶大家追一列:albumin 寫成 <b>41 g/L</b>,不是 4.1 g/dL——差整整 10 倍!bilirubin 用 µmol/L,欄位叫 <code>AtezoBev</code>、<code>os_death</code>,全都得改過來。</li>
      <li>Gamma(H03)最麻煩:<b>沒有連續的 AFP 數值</b>,只給一個「是否 ≥400」的旗標 <code>afp_high</code>。</li>
      <li>點表格可放大讀欄位,放大後按 <b>↑ ↓</b> 就能並排比對不同方言。收尾一句:「這就是 Claude Code 等一下要幫我們整併的東西。」→ 接整併 session。</li>
    </ul>`,
		// 4 harmonise session
		`<ul>
      <li><span class="cue">beat 1</span> 先讓 prompt(你用白話寫給 AI 的交代,要它做什麼)一個字一個字打出來,視窗會放大。當場點出:一個好指令有三件事——<b>目標</b>(全部併成一張表)、<b>難點</b>(單位、代碼要換算)、還有<b>檢查</b>(跑完要跟答案鍵對)。你把驗收標準講明,AI 就會自己去驗。</li>
      <li>接著是全場第一次看到 AI「真的動手」:它先去<b>讀</b> Beta、Gamma 兩個檔案(這叫 tool call / 工具動作——不是憑空講,是真的執行去讀檔),看懂每家欄位長什麼樣。</li>
      <li>然後它自己<b>寫出一支程式</b> <code>harmonize_hospitals.py</code> 來換算:albumin 除以 10、bilirubin 除以 17.1、把 "A5" 變成 5、各種藥名統一成一套講法。</li>
      <li><span class="cue">PASS</span> 這行是信任時刻:程式跑完,結果跟事先算好的<b>答案鍵</b>(正確答案)完全吻合,顯示 <b>PASS</b>。強調:我沒有用眼睛瞄一瞄,是機器對過的。合併後 <b>N = 1800</b>(Atezo 962 / Sora 838)。</li>
      <li><span class="cue">beat 5</span> 最後這張各院 atezo 佔比表是關鍵梗:用藥比例從 <b>35% 跳到 66%</b>,學術中心開 atezo 大約是社區醫院的兩倍。這代表「開哪種藥」跟「在哪家醫院」綁在一起——這就是<b>混雜</b>(兩組病人本來就不一樣),正好鋪陳下一幕的 PSM。別急著帶過。</li>
    </ul>`,
		// 5 confounding
		`<ul>
      <li>這是全場觀念的核心。先賣直覺、再談機制:<b>0.505</b>(沒做任何調整、直接比出來的存活風險比)比真值 <b>0.58</b> 更<b>極端</b>——這裡的 HR / 風險比是一個數字,小於 1 代表用藥組死亡風險較低。這段差距是<b>混雜</b>(兩組病人本來就不一樣)造成的假象,不是藥真的更神。</li>
      <li>為什麼會這樣?治療<b>不是隨機分配</b>的:本來就比較健康的病人更容易被開 Atezo+Bev,所以直接比,就會<b>高估</b>藥效。</li>
      <li>要講的誠實但書:PSM(傾向分數配對——把有用藥和沒用藥的病人依條件一對一配起來,先站上同一起跑點再比)之所以能成立,是因為這裡<b>所有</b>會影響的混雜因子都有量到、都在 CSV 裡(這叫 ignorability 假設)。真實世界你得自己論證這件事,不會白白送你。</li>
      <li>一句話收:<b>先想清楚要估什麼,再選方法</b>——我們要的是「藥本身的效果」,不是「會拿到這種藥的那種病人本來就比較好」的效果。</li>
      <li><span class="cue">beat 3</span> 帶到下一幕 session:「看我用<b>一個 prompt</b> 就把整套 PSM 流程要下來——估計傾向分數、配對、還要<b>驗平衡</b>。」</li>
    </ul>`,
		// 6 PSM session
		`<ul>
      <li>這一頁是整個「去混雜」的實作核心。一句話：先估每個病人的<b>傾向分數</b>（他「會被開這個藥」的機率），再把有用藥和沒用藥的病人依條件一對一配起來，讓兩組先站上同一個起跑點再比。</li>
      <li><span class="cue">beat 4</span> 平衡表就是審稿者最想看的那份證據。看每個條件配對前後的差距（|SMD|，也就是兩組差多少）：配對<b>前</b>是 0.18–0.23，配對<b>後</b>全部掉到 <code>&lt;0.05</code>。可以講「慣例是 |SMD| &lt; 0.1 就算平衡，我們遠低於這條線」。</li>
      <li><span class="cue">beat 5</span> Love plot 就是把那張表畫成圖，一眼看出所有點都收進門檻內；overlap（重疊）圖則證明兩組的條件範圍是重疊的、我們沒有硬去外推不存在的病人。這兩張圖正好擋掉 PSM 最常被挑的兩個毛病。</li>
      <li>提醒觀眾對比：沒調整的原始 HR 是 <b>0.505</b>，比真值還更極端——那是混雜、不是藥效；配對後才回到 <b>0.578</b>。</li>
      <li><span class="cue">beat 6</span> 三角驗證（用兩種思路不同的方法各算一遍，結果一致才敢信）：配對算出 <b>0.578</b>，另一條路的回歸調整獨立算出 <b>0.563</b>。兩種假設不一樣的方法都指到同一個地方——這就是可以停下來說「我現在真的相信這個效果」的時刻。</li>
    </ul>`,
		// 7 KM concept
		`<ul>
      <li>快速觀念頁，控制在 ~2 分鐘。先講為什麼不能只用「死亡百分比」：病人是陸續收案、卻只有一個統計截止點，很多人到最後一次回診都<b>還活著</b>（這叫 censoring，資料被截斷）。</li>
      <li>直接算「% 死亡」會把這些人的追蹤時間整個丟掉；<b>Kaplan–Meier</b>（存活曲線，隨時間畫出還活著的比例那條往下走的線）則用上每一個追蹤月份的資訊。</li>
      <li>台下大多熟 KM，真正的新意是：我們把它跑在<b>配對後</b>的世代上——存活分析和因果推論就這樣接了起來。配對後留下 <b>706 對</b>、1412 位病人，KM 曲線才是拿同類比同類。</li>
      <li>預告高潮：如果配對真的有效，這兩條曲線應該會<b>重現那個我們其實沒機會做的隨機試驗</b>。</li>
    </ul>`,
		// 8 KM session
		`<ul>
      <li>這是全場高潮頁，節奏要刻意慢下來。一個 prompt 就在配對後世代跑完 KM、log-rank 檢定，還有 Cox（一次算出風險比、又能同時考慮多個因素的方法），並畫出可以直接投稿的曲線。</li>
      <li>先報數字：死亡率 Atezo+Bev 24.7% vs Sorafenib 39.4%，12 個月存活 70.0% vs 57.8%——差距很直觀。</li>
      <li><span class="cue">beat 3</span> 讓 OS 曲線在畫面上多停一會兒。用手指出兩條線的分離、以及陰影的信賴帶（估計的不確定範圍），順帶提中位數線和 at-risk（各時間點還在追蹤的人數）的邏輯。</li>
      <li><span class="cue">beat 5</span> 情緒最高點：配對後 OS <b>HR 0.58</b>、log-rank <code>p &lt; 0.001</code>，曲線乾淨分開——這和真實的隨機試驗 IMbrave150（Finn 2020，HR 0.58）<b>一模一樣</b>。可以平實地說一句：「觀察資料，只要做得夠仔細，就重現了隨機試驗的答案。」</li>
      <li>然後立刻收斂、別讓它膨脹：一致 ≠ 證明。正因為如此，接下來才要做子群和穩健度檢驗。</li>
    </ul>`,
		// 9 subgroup
		`<ul>
      <li>先把子群分析的態度講誠實：子群分析是<b>假設生成</b>（提出新問題，不是下定論）、每一格病人變少所以檢定力不足、很容易跑出偽陽性。所以我們要看的是<b>一致性</b>，不是在十三個子群裡挑出「效果最好的那一群」來說嘴。</li>
      <li>用一句話幫新手定錨：這張圖不是要找贏家，是要問「不管切哪一刀，藥的好處會不會突然消失、甚至反過來」。</li>
      <li><span class="cue">beat 3</span> 帶大家掃這張森林圖：十三個子群的點估計全落在 <b>0.51 到 0.63</b> 之間，每一條信賴區間都<b>不碰到 1.0</b>（HR＝1 就是沒差；跨過 1 才代表可能沒效）。沒有任何一個子群翻盤。</li>
      <li>特別指一下 BCLC A/B 那條最寬——因為它人數最少（n 最小），信賴區間就寬。這是對「精準度」的誠實，寬不代表有問題，只代表證據薄一點。</li>
      <li>預先接住台下一定會問的：「你有沒有校正多重比較？」——回答：這裡是描述性的一致性檢查，不是拿來下結論的確認性檢定，所以定位本來就不同。</li>
    </ul>`,
		// 10 robustness
		`<ul>
      <li>這一頁是把「謹慎的分析者」和「運氣好的分析者」分開的關鍵。台下心裡的懷疑是：「你是不是試了很多種分析，剛好挑到最好看的那一個？」這頁就是正面回答它。</li>
      <li>先講多元宇宙（multiverse）：分析路上每個小選擇——配對方式、要不要調整、用哪套加權——都可能悄悄左右結論（這叫分岔花園）。我們不挑一條，而是把 <b>120 種</b>都算得過去的分析組合<b>全部各跑一遍</b>，結果 HR 幾乎不動（IQR 0.56–0.61），100% 都站在 atezo+bev 這邊。所以不是我 cherry-pick，是 120 條路都同意。</li>
      <li><span class="cue">beat 4</span> 再上 TMLE 交叉印證：這是一套思路完全不同的估計方法，它估的是<b>另一個要估的量</b>（estimand，就是「你到底想估哪個數字」）——不是風險比，而是 12 個月的絕對死亡風險差，尺度都換了，結果卻還是命中真值（−0.150 對上真實的 −0.154）。</li>
      <li>再喊一次「先想清楚要估什麼，再選方法」（estimand first, method second）——這是回扣第二幕講過的觀念。換一把尺、換一套方法，答案還是同一個，才真正安心。</li>
      <li>這裡很適合停下來讓大家問問題，因為接下來我們要從「做分析」切換到「寫論文」。</li>
    </ul>`,
		// 11 IMRaD workflow
		`<ul>
      <li>這是讓方法學者身體往前傾的一頁。大家對「叫 AI 幫我寫論文」最大的恐懼，就是它會<b>憑空編數字</b>。我們要正面點破這個恐懼。</li>
      <li>我們的解法不是靠叮嚀，而是靠結構：模型<b>只能</b>從它剛剛親手跑出來的產物寫——Methods 來自<b>分析程式</b>、Results 來自<b>console 的實際輸出</b>、Discussion 只從前兩者推理。每一段都有出處，不是憑記憶講故事。</li>
      <li>預告等一下畫面上會出現的 xref chip（交叉引用標籤）：每個數字旁邊都有一個小小的等寬字標籤，像 <span class="cue">psm.py [5]</span>，點下去就跳回產生這個數字的那段程式和那次執行紀錄。</li>
      <li>用一句話收尾：可追溯性才是重點。論文裡每個數字都能點回源頭，等於數字是「引用」而不是「生成」——這就是你將來面對審稿人、或半年後面對自己時，敢拍胸脯的底氣，沒有半個統計是 AI 幻想出來的。</li>
    </ul>`,
		// 12 methods
		`<ul>
      <li>這一整段(場景 12、13、14)要教的核心動作只有一句：<b>把論文文字紮根在真實產物上</b>。不是叫 AI 憑印象寫,而是讓它先去讀我們真正跑過的東西,再照著寫。</li>
      <li>看它的做法:這個 agent(會自己一步步動手做事的 AI,不只是聊天,而是真的去讀檔、跑程式)先<b>把三支分析程式讀一遍</b>,再動筆寫方法段——它寫的是「程式實際做了什麼」,不是「它猜我大概做了什麼」。</li>
      <li>舉個最具體的例子:程式裡配對的門檻寫的是 caliper <code>0.2·SD</code>(配對時允許的最大差距,差太多就不配成一對),那 Methods 就一字不差地寫 0.2·SD。程式怎麼寫,文字就怎麼寫,中間不准漂移。</li>
      <li>它也把方法段的每個關鍵細節都對齊了程式:11 個混雜因素的傾向分數模型、1:1 最近鄰配對、用標準化平均差看平衡、120 種設定的多元宇宙。這些不是它編的,是從 <code>psm_imbrave150.py</code> 這些檔案裡抄實的。</li>
      <li>順帶一個好處:這樣還會抓到<b>你自己</b>的錯。萬一寫出來的方法跟程式對不上,那一定有一邊寫錯了——你現在就會發現,而不是等審稿人幫你發現。</li>
    </ul>`,
		// 13 results
		`<ul>
      <li>方法段對齊程式,結果段就對齊<b>執行紀錄</b>:我要它只用剛剛跑出來、被記錄下來的 console 數字來寫,一個字都不准自己改寫或潤色。</li>
      <li>關鍵是每個數字後面那個小標籤——xref chip(交叉引用標籤,論文裡每個數字旁的小標記,點下去會跳回產生這個數字的那段程式或紀錄)。像 <code>psm.py&nbsp;[5]</code> 就是這個意思。</li>
      <li><span class="cue">beat 3</span> 帶大家走一句話配它的標籤:「配對後 OS HR 0.578 … <b>psm.py [5]</b>」。那個標籤就是<b>收據</b>——審稿人可以打開 <code>psm_imbrave150.py</code>,翻到第 [5] 步,親眼看到 0.578 就在那裡。</li>
      <li>整段每個數字都這樣配:35% 到 66% 配 <code>harmonize.py</code>、未校正的 0.505 配 <code>psm.py [1]</code>、706 對配 <code>psm.py [4]</code>、TMLE 配 <code>tmle.py</code>、120 種設定配 <code>multiverse.py</code>。沒有一個數字是孤兒。</li>
      <li>這正是大家對「AI 寫論文」最大恐懼的解藥。你怕它亂編數字?這裡的數字是<b>引用、不是生成</b>——它是從紀錄裡抄出來、還附上出處的,每一個都能一路追回可重現的來源。</li>
    </ul>`,
		// 14 discussion
		`<ul>
      <li>討論段是全篇最靠<b>判斷</b>的地方——也正因為這樣,最容易被 AI 唬過去,講出一堆聽起來漂亮、其實沒根據的話。</li>
      <li>對付它的辦法有兩招:一是逼它<b>只能從 Methods 和 Results 推理</b>,不准引進新東西;二是逼它<b>先講限制</b>,把話說滿之前先把底牌攤開。</li>
      <li>看它推理的線:從偏誤的 0.505 校正到配對後的 0.578,剛好命中資料裡預設的真值、也對上隨機分派的 IMbrave150 試驗(HR 0.58);再加上三種假設不同的方法(配對、迴歸校正、TMLE)都同意,還有 120 種設定的多元宇宙撐腰——這叫可信,不叫運氣好。</li>
      <li><span class="cue">beat 4</span> 這一段一定要念出來:資料是<b>完全合成的</b>,不能拿來下任何臨床結論——這是硬底線,沒得商量;還有傾向分數方法假設「沒有沒量到的混雜」,這裡是設計出來剛好成立,但真實世界的世代研究幾乎沒人敢保證。</li>
      <li>最後一句也別漏:這裡估的是<b>群體層級的平均效果</b>(estimand,先講清楚你到底想估哪個數字),不是某一個病人身上的效果。一篇好論文,對方法要有自信,對假設要謙虛。</li>
    </ul>`,
		// 15 manuscript
		`<ul>
      <li>讓成品先落地、停一下再講。這就是一小時換到的東西：一份結構完整的摘要、Methods、Results、Discussion，還有限制——而且<b>每一個數字都追得回它的出處</b>。</li>
      <li>帶觀眾看它的骨架：標題、摘要、方法、結果、討論，全是論文該有的段落；不是 AI 隨手生的一段文字，是一份可以接著改的初稿。</li>
      <li>接著要很誠實地講清楚它<b>不是</b>什麼：這是<b>初稿、是教材</b>，不是可以直接投稿的定稿，也<b>不是關於 atezolizumab 這個藥的證據</b>。</li>
      <li>把責任留在人身上：判斷、查文獻、為結論負責，這些還是你的事;AI 幫你把粗活做完並留好收據，最後拍板的是你。</li>
      <li><span class="cue">beat 3</span> 轉場收尾:「那——到底是什麼讓這整套結果，值得信?」帶進最後的總結。</li>
    </ul>`,
		// 16 takeaways
		`<ul>
      <li>收全場主軸:讓人敢信的,不是用了哪個厲害的 AI 模型,而是這套<b>流程</b>——所以它跟你用哪家的 AI 無關,這四個習慣可以搬到任何一份分析上。</li>
      <li>特別重講第一點,這是對台下最有用的一句:<b>把任務寫成「可以驗證」的樣子,AI 就會真的去驗證。</b>你交代它「跟答案鍵對一遍」「證明配對後兩組真的平衡」「每個數字都貼上出處標籤」,它就照著查給你看,而不是嘴上說做完了。</li>
      <li>第二個習慣——先<b>三角驗證</b>再相信:傾向分數配對、迴歸、TMLE、再加 120 種組合的多元宇宙分析,四種方法都指向同一個答案,遠比單一個 HR 更有份量。</li>
      <li>第三個習慣——寫作要<b>紮根在原始碼</b>:Methods 來自程式、Results 來自跑出來的紀錄,每句話都有交叉引用,沒有一個是 AI 掰出來的統計數字。</li>
      <li>第四個習慣——<b>先求真、再求美</b>:先老老實實把真的流程跑一遍、驗過,最後才做排版與潤飾;這場演講本身,就是拿這個原則套在自己身上做出來的。</li>
      <li>最後定調:Claude Code 沒有取代統計學家。要估什麼、假設是什麼、結論由誰負責,都還在你手上;它做的是<b>把「一個問題」到「一個站得住腳、又能重現的答案」之間的距離大幅壓短</b>——而且沿路把收據都留好。</li>
    </ul>`,
		// 17 end
		`<ul>
      <li>收在「可重現」這件事上——這是可信度最後的靠山:整條流程是決定性的、種子固定,任何人在自己電腦上跑一次 <span class="cue">make</span>,都會拿到跟你剛剛看到<b>一模一樣</b>的 CSV 和數字。</li>
      <li>指著螢幕上的四行指令帶過一遍:<code>make setup</code> 裝環境、<code>make data</code> 產生十間醫院加隨機試驗的資料、<code>make analyze</code> 做整併與配對與 TMLE、<code>make figure</code> 出穩健性的多元宇宙圖——不是黑箱,是可以自己跑的。</li>
      <li>最後再把但書講一次,清清楚楚地收:<b>資料 100% 合成、純教學用途、不構成任何臨床主張</b>;原始設定仿的是 Finn RS et al., NEJM 2020;382:1894。</li>
      <li>謝謝在場的各位,把 repo 位置留給大家,然後開放提問。</li>
    </ul>`,
	]
	scenes.forEach((s, i) => { if (zhNotes[i]) s.notesZh = zhNotes[i]; });

	window.STORYBOARD = { scenes };
})();
