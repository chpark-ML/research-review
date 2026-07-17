# Slide deck — paper review (Beamer, XeLaTeX, ~12-15 min).
#
# Usage:
#   make              → builds build/<slug>.pdf, named after the paper folder (e.g. ma-rag.pdf)
#   make rebuild      → force-rebuild (clean + all)
#   make view         → opens the built PDF
#   make clean        → removes build/ directory
#
# XeLaTeX is required (CJK fonts, unicode, system fonts). All intermediate
# artifacts (.aux .log .nav .snm .toc .out .synctex.gz) go to ./build/,
# keeping the source directory clean (out-of-tree build).

TEX       := slide.tex
# Output PDF is named after the paper slug (parent dir of slides/), e.g. ma-rag.pdf.
JOB       := $(notdir $(patsubst %/,%,$(dir $(CURDIR))))
BUILD_DIR := build
PDF       := $(BUILD_DIR)/$(JOB).pdf

XELATEX_FLAGS := -interaction=nonstopmode -halt-on-error -file-line-error \
                 -synctex=1 -output-directory=$(BUILD_DIR) -jobname=$(JOB)

.PHONY: all rebuild view clean distclean

all: $(PDF)

rebuild: clean all

$(PDF): $(TEX) | $(BUILD_DIR)
	xelatex $(XELATEX_FLAGS) $(TEX)
	xelatex $(XELATEX_FLAGS) $(TEX)   # second pass resolves TOC / cross-refs

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

view: $(PDF)
	@if   command -v open     >/dev/null; then open      $(PDF); \
	 elif command -v xdg-open >/dev/null; then xdg-open  $(PDF); \
	 else echo "Open $(PDF) manually."; fi

clean distclean:
	rm -rf $(BUILD_DIR)
