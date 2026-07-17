#!/usr/bin/env python3
"""Apply a two-color keyword-emphasis scheme to a Beamer slide.tex, safely.

Usage:  python3 apply_emphasis.py <slide.tex> <edits.json>

edits.json schema:
  [ { "key": "<unique substring of the frame TITLE>",
      "edits": [ { "find": "<verbatim substring, unique within that frame>",
                   "polarity": "pos" | "neg" } ] } ]

For each entry it locates the frame whose title-region (first ~240 chars after
\\begin{frame}) contains `key`, then wraps each `find` with \\good{...} (pos,
bold blue) or \\warn{...} (neg, bold magenta). The transform is WRAP-ONLY: a
span is replaced by prefix+span+'}', so the original content is preserved by
construction. `find` must occur exactly once in its frame, else it is skipped.

Requires the preamble to define \\good / \\warn (see references/preamble.tex).
After running, ALWAYS rebuild and visually check — bolding can overflow tight
frames (Hard Rule 8).
"""
import json, sys

WRAP = {"pos": ("\\good{", "}"), "neg": ("\\warn{", "}")}


def find_frame_blocks(text):
    """(start, end) char offsets of each \\begin{frame}...\\end{frame} after \\begin{document}."""
    doc = text.find("\\begin{document}")
    blocks = []
    i = 0
    while True:
        s = text.find("\\begin{frame}", i)
        if s == -1:
            break
        i = s + 1
        if s < doc:
            continue
        e = text.find("\\end{frame}", s)
        if e == -1:
            continue
        blocks.append((s, e + len("\\end{frame}")))
    return blocks


def main():
    if len(sys.argv) != 3:
        print(__doc__); sys.exit(1)
    slide_path, edits_path = sys.argv[1], sys.argv[2]
    with open(slide_path, encoding="utf-8") as f:
        text = f.read()
    with open(edits_path, encoding="utf-8") as f:
        entries = json.load(f)

    blocks = find_frame_blocks(text)
    pieces, block_strs, last = [], [], 0
    for (s, e) in blocks:
        pieces.append(text[last:s])
        block_strs.append(text[s:e])
        last = e
    tail = text[last:]

    applied = skipped = 0
    report = []
    used = set()
    for entry in entries:
        key = entry.get("key", "")
        edits = entry.get("edits", []) or []
        bidx = next((i for i, b in enumerate(block_strs)
                     if i not in used and key in b[:240]), None)
        if bidx is None:
            report.append(f"[FRAME NOT FOUND] key={key!r} ({len(edits)} skipped)")
            skipped += len(edits)
            continue
        used.add(bidx)
        block = block_strs[bidx]
        for ed in sorted(edits, key=lambda x: -len(x.get("find", ""))):
            find, pol = ed.get("find", ""), ed.get("polarity", "")
            if not find or pol not in WRAP:
                report.append(f"  [BAD] {key!r} {pol!r} {find!r}"); skipped += 1; continue
            pre, post = WRAP[pol]
            if pre + find + post in block:
                report.append(f"  [ALREADY] {key[:22]} {pol} {find!r}"); skipped += 1; continue
            n = block.count(find)
            if n != 1:
                report.append(f"  [NOT-UNIQUE x{n}] {key[:22]} {pol} {find!r}"); skipped += 1; continue
            pos = block.find(find)
            if block[max(0, pos - 7):pos].endswith(("\\good{", "\\warn{")):
                report.append(f"  [WRAPPED] {key[:22]} {pol} {find!r}"); skipped += 1; continue
            block = block.replace(find, pre + find + post, 1)
            applied += 1
            report.append(f"  [OK] {key[:24]:24s} {pol}  {find!r}")
        block_strs[bidx] = block

    out = []
    for i, gap in enumerate(pieces):
        out.append(gap); out.append(block_strs[i])
    out.append(tail)
    newtext = "".join(out)

    n_good = newtext.count("\\good{") - text.count("\\good{")
    n_warn = newtext.count("\\warn{") - text.count("\\warn{")
    if n_good + n_warn != applied:
        print("!! WRAP COUNT MISMATCH", n_good, n_warn, applied); sys.exit(2)

    with open(slide_path, "w", encoding="utf-8") as f:
        f.write(newtext)
    print("\n".join(report))
    print(f"\n=== applied={applied}  skipped={skipped}  (+good={n_good} +warn={n_warn}) ===")


if __name__ == "__main__":
    main()
