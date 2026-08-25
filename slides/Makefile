# slides/ — build the presentation PDF.
#
# The same Marp version and the same .marprc.yml are used by CI
# (.github/workflows/slides.yml), so `make` here reproduces the released file.

DECK    := deck.md
THEME   := theme.css
OUT     := dist/imbrave150-mission-by-mission.pdf
MARP    ?= npx --yes @marp-team/marp-cli@4.0.0

# Marp drives a headless Chrome. On macOS the Homebrew `chromium` shim is
# often a dangling symlink, so prefer a real Chrome if one is installed.
CHROME_CANDIDATES := \
	/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
	/Applications/Chromium.app/Contents/MacOS/Chromium
CHROME_PATH ?= $(firstword $(wildcard $(CHROME_CANDIDATES)))
export CHROME_PATH

# The overflow check needs Pillow. The repo venv has it; bare python3 usually
# does not.
PYTHON ?= $(if $(wildcard ../.venv/bin/python),../.venv/bin/python,python3)

.PHONY: all pdf html png watch clean check

all: pdf

pdf: $(OUT)

$(OUT): $(DECK) $(THEME) .marprc.yml
	@mkdir -p dist
	$(MARP) $(DECK) --config .marprc.yml --pdf -o $(OUT)
	@echo "→ $(OUT)"

# A self-contained HTML deck, handy for presenting without a PDF viewer.
html: $(DECK) $(THEME)
	@mkdir -p dist
	$(MARP) $(DECK) --config .marprc.yml --html-output-dir dist \
		--output dist/index.html
	@echo "→ dist/index.html"

# One PNG per slide, rasterised from the built PDF. This is far faster than
# asking Marp to screenshot each slide, and it checks the artefact we ship.
png: $(OUT)
	@mkdir -p dist/png
	@rm -f dist/png/*.png
	pdftoppm -png -r 96 $(OUT) dist/png/slide

# Fails if any slide's content runs past the bottom edge. Marp silently
# clips overflow, so this is the only way to catch a too-full slide.
check: png
	@$(PYTHON) tools/check_overflow.py dist/png

watch:
	$(MARP) $(DECK) --config .marprc.yml --watch --preview

clean:
	rm -rf dist
