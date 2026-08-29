#!/usr/bin/env python3
"""Render the speaker script into a page that is readable from a lectern.

Not linked from the landing page: it is the presenter's own lines, and the site
is public. Obscurity is not access control — put Cloudflare Access in front of
it if that matters.

Typeset for a phone or a second screen rather than for reading at a desk:
large body text, stage directions dimmed and set apart so the eye skips them,
stop headings marked so the right place can be found in a hurry.

    python3 tools/build_notes.py            # -> site/speaker-note/index.html
"""
import html
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent.parent
OUT = HERE / "site" / "speaker-note"

CSS = """
:root { --ink:#e9e9ec; --paper:#16161e; --dim:#8b8b98; --accent:#f9e2af;
        --rule:#2e2e3a; --card:#1e1e2e; }
@media (prefers-color-scheme: light) {
  :root { --ink:#16161e; --paper:#fff; --dim:#6b6b78; --accent:#8a6d00;
          --rule:#e2e2e8; --card:#f6f6f9; }
}
* { box-sizing:border-box; }
body { margin:0; background:var(--paper); color:var(--ink);
  font:400 20px/1.65 "IBM Plex Sans","Noto Sans TC",system-ui,sans-serif;
  padding:16px 18px 20vh; }
main { max-width:760px; margin:0 auto; }
h1 { font-size:30px; line-height:1.2; margin:8px 0 4px; }
h2 { font-size:22px; margin:36px 0 10px; padding:10px 12px;
     background:var(--card); border-left:4px solid var(--accent); border-radius:4px; }
h3 { font-size:19px; margin:26px 0 8px; color:var(--dim);
     text-transform:uppercase; letter-spacing:.08em; }
p { margin:0 0 14px; }
strong { font-weight:600; }
hr { border:0; border-top:1px solid var(--rule); margin:28px 0; }
code { font-family:"IBM Plex Mono",ui-monospace,monospace; font-size:.9em;
       background:var(--card); padding:1px 5px; border-radius:3px; }
blockquote { margin:0 0 14px; padding-left:14px; border-left:2px solid var(--rule); }
table { border-collapse:collapse; width:100%; font-size:17px; margin:0 0 16px; }
th,td { text-align:left; padding:7px 10px 7px 0; border-bottom:1px solid var(--rule); }
ul { padding-left:22px; }
li { margin-bottom:6px; }
/* Stage directions: present, but the eye should slide past them. */
.dir { color:var(--dim); font-size:.82em; font-style:italic; }
.top { position:sticky; top:0; background:var(--paper); padding:10px 0 8px;
       border-bottom:1px solid var(--rule); margin-bottom:10px;
       display:flex; gap:14px; align-items:baseline; flex-wrap:wrap; }
.top a { color:var(--dim); text-decoration:none; font-size:16px; }
.top a:hover { color:var(--ink); }
.top .now { margin-left:auto; font-size:15px; color:var(--dim); }
@media (max-width:520px) { body { font-size:19px; } h1 { font-size:25px; } }
"""


def main():
    src = HERE / "SCRIPT.md"
    if not src.exists():
        sys.exit(f"no script at {src}")
    if not subprocess.run(["command", "-v", "pandoc"], shell=False,
                          capture_output=True).returncode == 0:
        pass  # `command -v` via subprocess is unreliable; just try pandoc below

    try:
        body = subprocess.run(
            ["pandoc", "-f", "gfm", "-t", "html", str(src)],
            capture_output=True, text=True, check=True).stdout
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        sys.exit(f"pandoc is needed to render the notes: {e}")

    # Wrap the （…） stage directions so they can be dimmed. Done on the
    # rendered HTML so it applies inside paragraphs and list items alike.
    body = re.sub(r"（([^）]*)）", r'<span class="dir">（\1）</span>', body)

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "index.html").write_text(
        "<!doctype html>\n<html lang=\"zh-Hant\">\n<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "<meta name=\"robots\" content=\"noindex, nofollow\">\n"
        "<title>講稿 · Speaker notes</title>\n"
        f"<style>{CSS}</style>\n</head>\n<body>\n<main>\n"
        "<div class=\"top\">"
        "<a href=\"/talk\">&larr; 錄影</a>"
        "<a href=\"/\">首頁</a>"
        "<span class=\"now\">不對外公開，請勿分享連結</span>"
        "</div>\n"
        f"{body}\n</main>\n</body>\n</html>\n")
    size = (OUT / "index.html").stat().st_size
    print(f"speaker-note/index.html  {size // 1024} KB")


if __name__ == "__main__":
    main()
