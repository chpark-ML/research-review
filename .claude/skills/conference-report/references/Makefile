# 학회 참관 리포트 빌드 (XeLaTeX + gs 압축)
# <conf>/report/ 에 복사해 사용.
TEX = report.tex
PDF = report.pdf

.PHONY: all clean
all: $(PDF)

$(PDF): $(TEX)
	xelatex -interaction=nonstopmode -halt-on-error $(TEX)
	xelatex -interaction=nonstopmode -halt-on-error $(TEX)
	@# 화질 함정: 사진 표시 폭이 절반이면 같은 dpi에서 실효 픽셀도 절반.
	@# /ebook 150dpi는 축소 배치된 포스터 사진을 뭉갠다 — /prepress 300dpi 고정.
	@if command -v gs >/dev/null 2>&1; then \
	  gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.5 -dPDFSETTINGS=/prepress \
	     -dNOPAUSE -dQUIET -dBATCH -dDetectDuplicateImages=true \
	     -dColorImageResolution=300 -dGrayImageResolution=300 \
	     -sOutputFile=$(PDF).tmp $(PDF) && mv -f $(PDF).tmp $(PDF); \
	  echo ">> compressed report.pdf ($$(du -h $(PDF) | cut -f1))"; \
	else echo ">> gs 없음: 원본 해상도 PDF 유지"; fi
	@$(MAKE) clean

clean:
	rm -f report.aux report.log report.out report.toc report.pdf.tmp
