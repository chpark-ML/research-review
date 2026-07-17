#!/usr/bin/env python3
"""현장 사진을 리포트용 assets 사본으로 정규화.

- EXIF orientation을 픽셀에 구워 넣는다(exif_transpose).
  XeLaTeX(xdvipdfmx)는 EXIF를 무시하므로 이 단계가 없으면 세로 사진이 눕는다.
- 최대 2000px로 다운샘플(q85) — 원본은 건드리지 않는다.

사용: python3 normalize_photos.py <src_dir> <dst_dir>
      (src_dir 하위 구조를 dst_dir에 그대로 미러링)
"""
import os
import sys

from PIL import Image, ImageOps

EXTS = ('.jpg', '.jpeg', '.png')


def main(src_root: str, dst_root: str) -> None:
    for dirpath, _dirnames, filenames in os.walk(src_root):
        for f in sorted(filenames):
            if not f.lower().endswith(EXTS):
                continue
            src = os.path.join(dirpath, f)
            rel = os.path.relpath(src, src_root)
            dst = os.path.join(dst_root, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            im = Image.open(src)
            ori = im.getexif().get(274, 1)  # EXIF orientation tag
            im = ImageOps.exif_transpose(im)
            im.thumbnail((2000, 2000))
            im.convert('RGB').save(dst, quality=85)  # EXIF는 저장 시 제거됨
            print(f'{rel:45s} ori={ori} -> {im.size[0]}x{im.size[1]}')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
