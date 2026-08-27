# slides/ — build the presentation PDFs.
#
# Three decks are built from one theme:
#   deck.md         12 slides — the talk. Signposts around a live demo.
#   deck-backup.md  the same, plus a recorded terminal screenshot after each
#                   signpost, for when the live demo will not cooperate.
#   deck-full.md    43 slides — the reference edition, for reading afterwards.
#
# CI (.github/workflows/slides.yml) uses this same Makefile and .marprc.yml, so
# `make` here reproduces exactly what gets released.

DECKS   := deck deck-backup deck-full
PDFS    := $(patsubst %,dist/imbrave150-%.pdf,$(DECKS))
THEME   := theme.css
MARP    ?= npx --yes @marp-team/marp-cli@4.0.0

# Marp drives a headless Chrome. On macOS the Homebrew `chromium` formula is
# often a dangling symlink into an app that was never installed, so prefer a
# real Google Chrome when one is present.
CHROME_CANDIDATES := \
	/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
	/Applications/Chromium.app/Contents/MacOS/Chromium
CHROME_PATH ?= $(firstword $(wildcard $(CHROME_CANDIDATES)))
export CHROME_PATH

# The overflow check needs Pillow. The repo venv has it; bare python3 usually
# does not.
PYTHON ?= $(if $(wildcard ../.venv/bin/python),../.venv/bin/python,python3)
SKILL  ?= $(HOME)/.claude/skills/agent-demo-recorder

.PHONY: all pdf deck html png watch clean check walk talk cast cast-html

all: pdf

pdf: $(PDFS)

# The talk deck alone — what you rebuild while editing.
deck: dist/imbrave150-deck.pdf

dist/imbrave150-%.pdf: %.md $(THEME) .marprc.yml
	@mkdir -p dist
	$(MARP) $< --config .marprc.yml --pdf -o $@
	@echo "-> $@"

# A self-contained HTML deck, for presenting without a PDF viewer.
html: deck.md $(THEME)
	@mkdir -p dist
	$(MARP) deck.md --config .marprc.yml --output dist/index.html
	@echo "-> dist/index.html"

# One PNG per slide, rasterised from the built PDFs. Far faster than asking
# Marp to screenshot each slide, and it checks the artefact we actually ship.
png: $(PDFS)
	@mkdir -p dist/png
	@rm -f dist/png/*.png
	@for d in $(DECKS); do \
		pdftoppm -png -r 96 dist/imbrave150-$$d.pdf dist/png/$$d; \
	done

# Fails if any slide's content runs past the bottom edge. Marp silently clips
# an overfull slide, so this is the only way to catch one.
check: png
	@$(PYTHON) tools/check_overflow.py dist/png

# --- the recorded session -------------------------------------------------
# One continuous agent session, driven prompt-by-prompt, recorded as terminal
# text rather than video. `cast` re-records (~10 min, needs a logged-in claude);
# `cast-html` just rebuilds the player from the existing recording.
# The walkthrough that gets presented: data, cleaning, exploring, analysis,
# writing. Plain prompts, no methodological detours. ~33 min, 22 min at 1.5x.
walk:
	./tools/record_walkthrough.sh
	$(PYTHON) tools/add_markers.py walk.cast walk-markers.tsv
	$(PYTHON) tools/trim_cast.py cast/walk.cast 6.2
	$(MAKE) cast-html

# The long version, with the methodological arguments in it. ~64 min.
talk:
	./tools/record_talk.sh
	$(PYTHON) tools/add_markers.py
	$(PYTHON) tools/trim_cast.py cast/talk-full.cast 6.2
	$(MAKE) cast-html

# The short 8-minute version: five prompts, no slides.
cast:
	./tools/record_cast.sh
	$(PYTHON) tools/add_markers.py talk.cast chapters.tsv
	$(MAKE) cast-html

# The generator makes a bare asciinema-player page; add_player_controls then
# bolts on the speed buttons and the chapter dropdown, which the player has no
# API for. Regenerating without that second step silently ships a page with no
# way to change speed, so the two always run together.
cast-html:
	@for c in walk talk-full talk; do \
		[ -f "cast/$$c.cast" ] || continue; \
		$(PYTHON) $(SKILL)/scripts/gen_html.py "cast/$$c.cast" --player --no-loop \
			--title "Mission by Mission" -o "cast/$$c.html"; \
		$(PYTHON) tools/add_player_controls.py "cast/$$c.html" "cast/$$c.cast"; \
	done
	@ls -lh cast/*.cast cast/*.html | awk '{print "  " $$9 "  " $$5}'

watch:
	$(MARP) deck.md --config .marprc.yml --watch --preview

clean:
	rm -rf dist
