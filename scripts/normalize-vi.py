#!/usr/bin/env python3
"""Viết số, ngày, tiền, đơn vị và chữ viết tắt thành chữ tiếng Việt trước khi đưa vào VoiceStudio.

Dùng thư viện sea-g2p. Giữ nguyên từng dòng và các tag [pause 500ms], [laughter], [[phiên âm]].

Số hàng nghìn được viết là "ngàn": trên một giọng thử, "tám nghìn sáu trăm" bị đọc thành
"tám sáu" ở cả năm seed, còn "tám ngàn sáu trăm" thì đủ chữ. Dùng --nghin để giữ "nghìn".

Giới hạn đã biết của sea-g2p: kết quả là chữ thường toàn bộ, ký hiệu "$" đọc thành "u s d",
và từ tiếng Anh chỉ được tách chữ chứ không phiên âm. Cần người hoặc Claude soát lại.

Dùng:
  uv run scripts/normalize-vi.py "Năm 2024 doanh thu tăng 15% lên 3,5 tỷ đồng."
  uv run scripts/normalize-vi.py -f bai-viet.txt > bai-viet.norm.txt
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

import vslib

EN_TAG = re.compile(r"</?en>")
NGHIN = re.compile(r"\bnghìn\b")


def segment(n, text: str) -> str:
    """Chuẩn hóa một phần chữ, giữ dấu câu ở cuối vì sea-g2p bỏ dấu phẩy cuối chuỗi."""
    text = text.strip()
    if not text:
        return ""
    out = n.normalize(text)
    return out + text[-1] if text[-1] in ",;:" and not out.endswith(text[-1]) else out


def normalize(text: str, ngan: bool = True) -> str:
    from sea_g2p import Normalizer

    n = Normalizer(lang="vi")
    lines = []
    for line in unicodedata.normalize("NFC", text).splitlines():
        # Chỉ chuẩn hóa phần chữ nằm giữa các tag, để tag không bị đọc thành chữ.
        parts, last = [], 0
        for m in vslib.TAG_RE.finditer(line):
            parts += [segment(n, line[last:m.start()]), m.group()]
            last = m.end()
        parts.append(segment(n, line[last:]))
        if ngan:  # không đụng vào chữ trong tag
            parts = [p if vslib.TAG_RE.fullmatch(p) else NGHIN.sub("ngàn", p) for p in parts]
        lines.append(" ".join(EN_TAG.sub("", p).strip() for p in parts if p))
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("text", nargs="?")
    ap.add_argument("-f", "--file", type=Path)
    ap.add_argument("--nghin", action="store_true", help='giữ "nghìn", không đổi thành "ngàn"')
    a = ap.parse_args()
    text = a.text if a.text is not None else (a.file.read_text(encoding="utf-8") if a.file else sys.stdin.read())
    print(normalize(text, ngan=not a.nghin))


if __name__ == "__main__":
    main()
