#!/usr/bin/env python3
"""Chuyển một bản thu (WAV, M4A của iPhone, ...) thành clip mẫu WAV mono 48 kHz 24-bit.

Chỉ gộp kênh, cắt đoạn và cắt khoảng lặng hai đầu. Không lọc ồn, không chỉnh âm lượng,
vì model chép lại cả dấu vết xử lý.

Dùng:
  uv run scripts/prep-clip.py ban-thu.m4a recordings/tro-chuyen-01-take1.wav
  uv run scripts/prep-clip.py ban-thu.wav recordings/ke-chuyen-04-take2.wav --start 12.4 --end 19.8
"""
from __future__ import annotations

import argparse
from pathlib import Path

import soundfile as sf

import vslib

SR = 48000
PAD = 0.08  # giữ lại 80 ms trước và sau tiếng nói để không cắt vào âm đầu, âm cuối


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", type=Path)
    ap.add_argument("dest", type=Path)
    ap.add_argument("--start", type=float, help="giây bắt đầu trong bản thu gốc")
    ap.add_argument("--end", type=float, help="giây kết thúc trong bản thu gốc")
    ap.add_argument("--no-trim", action="store_true", help="không cắt khoảng lặng hai đầu")
    ap.add_argument("--force", action="store_true", help="ghi đè file đích")
    a = ap.parse_args()

    if not a.src.exists():
        vslib.die(f"không thấy {a.src}")
    if a.dest.suffix.lower() != ".wav":
        vslib.die("file đích phải có đuôi .wav")
    if a.dest.exists() and not a.force:
        vslib.die(f"{a.dest} đã có, thêm --force để ghi đè")

    info = vslib.probe(a.src)
    y = vslib.load_audio(a.src, SR, a.start, a.end)
    if len(y) == 0:
        vslib.die("đoạn chọn không có âm thanh")

    if not a.no_trim:
        y = vslib.trim_silence(y, SR, PAD)

    a.dest.parent.mkdir(parents=True, exist_ok=True)
    sf.write(a.dest, y, SR, subtype="PCM_24")
    print(f"Đã ghi {a.dest}: {len(y) / SR:.2f}s, WAV mono 48 kHz 24-bit")
    if info["sample_rate"] < SR:
        print(f"Lưu ý: bản gốc chỉ {info['sample_rate']} Hz, nâng lên 48 kHz không thêm chi tiết.")
    print(f"Kiểm tra tiếp: uv run scripts/check-clip.py {a.dest}")


if __name__ == "__main__":
    main()
