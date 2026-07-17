#!/usr/bin/env python3
"""Extract a single figure from an arXiv paper PDF and save as PNG.

Pipeline:
1. Download arXiv PDF via curl-equivalent (urllib).
2. Locate caption bbox by text search.
3. Compute rough crop region above (or below) caption, excluding page header.
4. Render at low DPI for autotrim; convert PIL bbox of non-white pixels back
   to PDF coordinates to find tight bbox.
5. Re-render tight bbox at requested DPI via PyMuPDF, save PNG.

Usage::

    python3 extract_figure.py \\
        --arxiv-id 2305.12788 \\
        --page 1 \\
        --caption "Figure 1:" \\
        --out graphcare_overview.png \\
        --dpi 250

See sibling SKILL.md for the full procedure.
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
import urllib.request

import fitz  # PyMuPDF
from PIL import Image, ImageChops


def _autotrim_bbox(
    page: fitz.Page,
    rough_rect: fitz.Rect,
    scan_dpi: int = 72,
    pad_pt: float = 4.0,
) -> fitz.Rect:
    """Render rough_rect at scan_dpi, find non-background bbox, return PDF rect."""
    zoom = scan_dpi / 72
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=rough_rect, alpha=False)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    bg = Image.new(img.mode, img.size, img.getpixel((0, 0)))
    bbox = ImageChops.difference(img, bg).getbbox()
    if not bbox:
        return rough_rect
    px0, py0, px1, py1 = bbox
    inv = 1 / zoom
    return fitz.Rect(
        max(rough_rect.x0, rough_rect.x0 + px0 * inv - pad_pt),
        max(rough_rect.y0, rough_rect.y0 + py0 * inv - pad_pt),
        min(rough_rect.x1, rough_rect.x0 + px1 * inv + pad_pt),
        min(rough_rect.y1, rough_rect.y0 + py1 * inv + pad_pt),
    )


def _download_arxiv_pdf(arxiv_id: str, dest: str) -> None:
    url = f"https://arxiv.org/pdf/{arxiv_id}"
    urllib.request.urlretrieve(url, dest)


def extract_figure(
    pdf_path: str,
    page_idx: int,
    caption: str,
    out_png: str,
    dpi: int = 250,
    header_skip_pt: float = 70.0,
    caption_above: bool = False,
    manual_bbox: tuple[float, float, float, float] | None = None,
) -> None:
    """Extract a figure from ``pdf_path`` page ``page_idx`` into ``out_png``."""
    doc = fitz.open(pdf_path)
    page = doc[page_idx]
    page_rect = page.rect

    if manual_bbox is not None:
        tight = fitz.Rect(*manual_bbox)
    else:
        hits = page.search_for(caption)
        if not hits:
            raise SystemExit(f"caption {caption!r} not found on page {page_idx} of {pdf_path}")
        cap = hits[0]
        if caption_above:
            rough = fitz.Rect(page_rect.x0 + 5, cap.y1 + 2, page_rect.x1 - 5, page_rect.y1 - header_skip_pt)
        else:
            rough = fitz.Rect(page_rect.x0 + 5, page_rect.y0 + header_skip_pt, page_rect.x1 - 5, cap.y0 - 2)
        tight = _autotrim_bbox(page, rough)

    zoom = dpi / 72
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=tight, alpha=False)
    pix.save(out_png)
    print(
        f"[extract] page={page_idx} tight={tight.width:.0f}x{tight.height:.0f}pt → "
        f"{pix.width}x{pix.height}px → {out_png} ({os.path.getsize(out_png):,} B)",
        file=sys.stderr,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--arxiv-id", help="arXiv identifier, e.g. 2305.12788")
    src.add_argument("--pdf", help="Path to a local paper PDF")
    parser.add_argument("--page", type=int, required=True, help="Page index, 0-based")
    parser.add_argument("--caption", default="Figure 1:", help="Caption prefix to anchor on")
    parser.add_argument("--out", required=True, help="Output PNG path")
    parser.add_argument("--dpi", type=int, default=250, help="Render DPI (default 250)")
    parser.add_argument(
        "--header-skip-pt",
        type=float,
        default=70.0,
        help="Skip this many pt from page top (or bottom with --caption-above) "
        "to exclude conference-paper page headers",
    )
    parser.add_argument(
        "--caption-above",
        action="store_true",
        help="Caption appears ABOVE the figure (uncommon); crop downward instead",
    )
    parser.add_argument(
        "--bbox",
        nargs=4,
        type=float,
        metavar=("X0", "Y0", "X1", "Y1"),
        help="Manual figure bbox in PDF points; skips caption search and autotrim",
    )
    args = parser.parse_args()

    if args.arxiv_id:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            _download_arxiv_pdf(args.arxiv_id, tmp_path)
            extract_figure(
                tmp_path,
                args.page,
                args.caption,
                args.out,
                dpi=args.dpi,
                header_skip_pt=args.header_skip_pt,
                caption_above=args.caption_above,
                manual_bbox=tuple(args.bbox) if args.bbox else None,
            )
        finally:
            os.remove(tmp_path)
    else:
        extract_figure(
            args.pdf,
            args.page,
            args.caption,
            args.out,
            dpi=args.dpi,
            header_skip_pt=args.header_skip_pt,
            caption_above=args.caption_above,
            manual_bbox=tuple(args.bbox) if args.bbox else None,
        )


if __name__ == "__main__":
    main()
