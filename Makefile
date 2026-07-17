# Root delegator — slide builds for a per-paper deck.
#
# Each reviewed paper lives in papers/<slug>/ with a self-contained slide
# deck at papers/<slug>/slides/. Select the paper with PAPER=<slug>.
#
# Usage:
#   make slide        PAPER=ma-rag   → build papers/ma-rag/slides/build/ma-rag.pdf and open it
#   make slide-build  PAPER=ma-rag   → build only (no auto-open)
#   make slide-check  PAPER=ma-rag   → slide count vs time budget (SLIDE_MIN / SLIDE_MAX)
#   make page-count   PAPER=ma-rag   → slide page count
#   make clean        PAPER=ma-rag   → remove that deck's build/ dir
#
# Per-deck recipe detail (passes, intermediates) lives in
# papers/<slug>/slides/Makefile. Keep this file thin — it only delegates.

PAPER     ?= ma-rag
SLIDE_DIR := papers/$(PAPER)/slides
SLIDE_PDF := $(SLIDE_DIR)/build/$(PAPER).pdf

# --- Time budget (slides per minute) ------------------------------------
# Conference/seminar review talk: 1.0-1.5 slides/min. Bump alongside
# .claude/skills/slide-deck/SKILL.md § time budget. Single source of truth.
# Comprehensive deck (all paper figures + tables) → ~25-30 min review talk.
SLIDE_MIN ?= 18
SLIDE_MAX ?= 32

.PHONY: slide slide-build slide-check page-count clean help

help:
	@echo "targets: slide, slide-build, slide-check, page-count, clean"
	@echo "select paper:  make <target> PAPER=<slug>   (default PAPER=$(PAPER))"
	@echo "vars:          SLIDE_MIN=$(SLIDE_MIN)  SLIDE_MAX=$(SLIDE_MAX)"

slide-build:
	$(MAKE) -C $(SLIDE_DIR)

slide: slide-build
	$(MAKE) -C $(SLIDE_DIR) view

slide-check: slide-build
	@python3 -c "import fitz; n=fitz.open('$(SLIDE_PDF)').page_count; lo=$(SLIDE_MIN); hi=$(SLIDE_MAX); flag='OK' if lo<=n<=hi else 'WARN'; print(f'[{flag}] $(PAPER) slide: {n} pages (budget: {lo}-{hi})')"

page-count:
	@python3 -c "import fitz, os; p='$(SLIDE_PDF)'; print(f'$(PAPER) slide: {fitz.open(p).page_count} pages (budget: $(SLIDE_MIN)-$(SLIDE_MAX))' if os.path.exists(p) else f'[skip] {p} missing — run: make slide-build PAPER=$(PAPER)')"

clean:
	$(MAKE) -C $(SLIDE_DIR) clean
