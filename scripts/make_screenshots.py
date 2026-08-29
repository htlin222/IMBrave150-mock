#!/usr/bin/env python3
"""Regenerate docs/img/ — the screenshots the README and the repo card use.

Every terminal image here is a real frame of `slides/cast/walk.cast`, seeked to
a named second and captured from the same self-contained player the audience
sees. Nothing is mocked up, which matters: the whole claim of this repository
is that the session happened.

    python3 scripts/make_screenshots.py            # all of it
    python3 scripts/make_screenshots.py --frames   # just the terminal frames
    python3 scripts/make_screenshots.py --cover    # just the social card

Needs Google Chrome (headless, for the player) and Pillow. The figures are
copied out of a finished `live-demo/workspace/`; if you have not run the demo,
those steps are skipped and the committed copies stay as they are.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "img"
CAST_PAGE = ROOT / "slides" / "cast" / "walk.html"
WS = ROOT / "live-demo" / "workspace"

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
]

# (seconds into walk.cast, output name, why this moment)
#
# Seconds, not markers: a marker fires when a prompt is *submitted*, and the
# interesting frame is a minute or two later when the answer is on screen.
FRAMES = [
    (560, "recording-baseline.png",
     "the covariate-by-covariate baseline table, with the plain-English "
     "prompt that asked for it still visible in the composer"),
    (378, "recording-prompt.png",
     "a prompt highlighted as it is submitted, above the reasoning about "
     "AFP being measured two different ways in different hospitals"),
    (1075, "recording-reasoning.png",
     "the balance check: why IPTW and Cox disagree, and which of the "
     "model's own coefficients are not to be believed"),
]

# Figures produced by the run itself.
FIGURES = [
    ("figures/km_os.png", "km-os.png"),
    ("figures/multiverse.png", "multiverse.png"),
    ("figures/forest.png", "forest.png"),
]

COVER = OUT / "social-preview.png"
COVER_SIZE = (1280, 640)          # GitHub's social-preview slot

TITLE = "Running a study without writing code"
SUB = ("Ten hospital exports, three EHR schemas, one AI agent — and every "
       "prompt that produced the result.")
FOOT = "github.com/htlin222/IMBrave150-mock — synthetic data, no real patient"

# Left column of the cover: the numbers, and what each one is.
NUMBERS = [
    ("unadjusted, and wrong", "HR 0.505"),
    ("after matching 706 pairs", "HR 0.578"),
    ("of 120 specifications cross 1.0", "none"),
]


def chrome() -> str:
    for c in CHROME_CANDIDATES:
        if Path(c).exists():
            return c
    sys.exit("no Chrome or Chromium found — cannot capture the player")


def capture(seconds: float, dest: Path, size=(1600, 900)) -> None:
    """Screenshot walk.html paused at `seconds`.

    The page exposes its player as window.__talkPlayer (see
    slides/tools/add_player_controls.py). Pausing before AND after the seek
    matters: seek() resolves asynchronously and the player resumes on its own
    if it was playing when the seek landed.
    """
    page = CAST_PAGE.read_text()
    inject = f"""
<script>
(function () {{
  function go() {{
    var p = window.__talkPlayer;
    if (!p) {{ setTimeout(go, 50); return; }}
    p.pause();
    Promise.resolve(p.seek({seconds})).then(function () {{ p.pause(); }});
  }}
  go();
}})();
</script>
"""
    tmp = Path(tempfile.mkdtemp()) / "shot.html"
    tmp.write_text(page.replace("</body>", inject + "</body>")
                   if "</body>" in page else page + inject)
    subprocess.run(
        [chrome(), "--headless", "--disable-gpu", "--hide-scrollbars",
         f"--window-size={size[0]},{size[1]}", f"--screenshot={dest}",
         # Virtual time lets the player's timers run to completion instantly;
         # without it the screenshot lands on a half-rendered frame.
         "--virtual-time-budget=15000", tmp.as_uri()],
        capture_output=True, timeout=240, check=False)
    shutil.rmtree(tmp.parent, ignore_errors=True)
    if not dest.exists():
        sys.exit(f"chrome produced nothing for t={seconds}")
    print(f"  {dest.name}  t={int(seconds)//60}:{int(seconds)%60:02d}  "
          f"{dest.stat().st_size // 1024} KB")


def font(*names, size: int):
    from PIL import ImageFont
    roots = [Path.home() / "Library/Fonts", Path("/Library/Fonts"),
             Path("/System/Library/Fonts"), Path("/usr/share/fonts")]
    for name in names:
        for r in roots:
            for p in r.rglob(name):
                try:
                    return ImageFont.truetype(str(p), size)
                except OSError:
                    continue
    return ImageFont.load_default(size=size)


def wrap(draw, text: str, f, width: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=f) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def cover() -> None:
    """A split card: the title on the left, the real terminal on the right.

    Overlaying text on the screenshot was tried first and is unreadable — at
    the size GitHub renders this, monospace behind a headline is just noise.
    A hard split keeps both legible.
    """
    from PIL import Image, ImageDraw, ImageEnhance

    W, H = COVER_SIZE
    BG = (22, 22, 31)
    PANEL = (30, 30, 46)       # the player's own background
    split = round(W * 0.585)

    src = OUT / "recording-baseline.png"
    if not src.exists():
        sys.exit(f"{src} missing — run with --frames first")

    card = Image.new("RGB", (W, H), BG)

    # --- right: a slice of the terminal, scaled so the text stays sharp ----
    shot = Image.open(src).convert("RGB")
    right_w = W - split
    scale = H / shot.height
    shot = shot.resize((round(shot.width * scale), H), Image.LANCZOS)
    # Crop from the left of the terminal: that is where the table sits.
    left = round(shot.width * 0.13)
    shot = shot.crop((left, 0, min(left + right_w, shot.width), H))
    if shot.width < right_w:
        shot = shot.resize((right_w, H), Image.LANCZOS)
    shot = ImageEnhance.Brightness(shot).enhance(0.78)
    card.paste(shot, (split, 0))

    d = ImageDraw.Draw(card)
    d.rectangle([(0, 0), (split - 1, H)], fill=PANEL)
    d.line([(split, 0), (split, H)], fill=(64, 66, 88), width=2)

    f_title = font("FiraSans-Bold.otf", "SFNS.ttf", "Helvetica.ttc", size=58)
    f_sub = font("FiraSans-Book.otf", "SFNS.ttf", "Helvetica.ttc", size=26)
    f_num = font("FiraCode-Medium.ttf", "Menlo.ttc", size=23)
    f_foot = font("FiraSans-Book.otf", "SFNS.ttf", "Helvetica.ttc", size=20)

    m = 58
    text_w = split - 2 * m

    lines = wrap(d, TITLE, f_title, text_w)
    y = 96
    for line in lines:
        d.text((m, y), line, font=f_title, fill=(246, 246, 251))
        y += 70

    y += 20
    for line in wrap(d, SUB, f_sub, text_w):
        d.text((m, y), line, font=f_sub, fill=(168, 172, 196))
        y += 38

    # The three numbers the repository actually turns on.
    y += 34
    for label, value in NUMBERS:
        d.text((m, y), value, font=f_num, fill=(226, 200, 130))
        d.text((m + 158, y + 2), label, font=f_foot, fill=(140, 144, 170))
        y += 36

    d.line([(m, H - 84), (split - m, H - 84)], fill=(62, 64, 86), width=1)
    d.text((m, H - 62), FOOT, font=f_foot, fill=(126, 130, 156))

    card.save(COVER, optimize=True)
    print(f"  {COVER.name}  {W}x{H}  {COVER.stat().st_size // 1024} KB")


def figures() -> None:
    for src_rel, name in FIGURES:
        src = WS / src_rel
        if not src.exists():
            print(f"  skipped {name} — no {src.relative_to(ROOT)} "
                  f"(run the demo first)")
            continue
        shutil.copy2(src, OUT / name)
        print(f"  {name}  {(OUT / name).stat().st_size // 1024} KB")


def squeeze() -> None:
    """Palette-quantise the PNGs, if pngquant is around.

    These are screenshots of text on a flat background: 256 colours is
    indistinguishable and roughly a third of the bytes. A README that costs a
    megabyte to open is a README people scroll past.
    """
    if not shutil.which("pngquant"):
        print("  pngquant not installed — leaving the PNGs full size")
        return
    before = sum(p.stat().st_size for p in OUT.glob("*.png"))
    for p in sorted(OUT.glob("*.png")):
        subprocess.run(["pngquant", "--force", "--skip-if-larger", "--quality",
                        "70-96", "--output", str(p), str(p)],
                       capture_output=True, check=False)
    after = sum(p.stat().st_size for p in OUT.glob("*.png"))
    print(f"  {before // 1024} KB -> {after // 1024} KB")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    only = {a.lstrip("-") for a in sys.argv[1:]}

    if not only or "frames" in only:
        print("terminal frames from slides/cast/walk.cast:")
        for seconds, name, _ in FRAMES:
            capture(seconds, OUT / name)
    if not only or "figures" in only:
        print("figures from the reference run:")
        figures()
    if not only or "cover" in only:
        print("social preview card:")
        cover()
    print("optimising:")
    squeeze()
    return 0


if __name__ == "__main__":
    sys.exit(main())
