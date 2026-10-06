#!/usr/bin/env python3
"""Tạo profile giọng trong VoiceStudio từ một clip mẫu và transcript, với Language Vietnamese.

Clip được đo trước bằng check-clip; clip bị "LỖI" sẽ không được tạo profile trừ khi thêm --force.

Dùng:
  uv run scripts/make-profile.py lan01 recordings/tro-chuyen-01-take2.wav \\
      "Sáng nay mình dậy sớm, pha một ấm trà nóng rồi ngồi ngoài hiên nghe những hạt mưa nhỏ rơi trên mái tôn."
  uv run scripts/make-profile.py lan02 clip.wav --transcript-file clip.txt
"""
from __future__ import annotations

import argparse
import importlib.util
import unicodedata
from pathlib import Path

import vslib


def load_check():
    spec = importlib.util.spec_from_file_location("check_clip", Path(__file__).with_name("check-clip.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name", help="tên profile, ví dụ lan01")
    ap.add_argument("clip", type=Path)
    ap.add_argument("transcript", nargs="?", help="lời đã đọc trong clip, khớp từng chữ")
    ap.add_argument("--transcript-file", type=Path)
    ap.add_argument("--force", action="store_true", help="vẫn tạo dù clip bị LỖI")
    a = ap.parse_args()

    text = a.transcript or (a.transcript_file.read_text(encoding="utf-8") if a.transcript_file else "")
    text = unicodedata.normalize("NFC", " ".join(text.split()))
    if not text:
        vslib.die("thiếu transcript. Transcript khớp từng chữ giúp model bám giọng tốt hơn.")
    if any(ch.isdigit() for ch in text):
        vslib.die("transcript có chữ số. Hãy viết số thành chữ đúng như đã đọc.")

    m = load_check().measure(a.clip)
    print(f"{m['verdict']}: {a.clip} ({m['duration']:.1f}s)")
    for i in m["issues"]:
        print(f"  - {i}")
    if m["verdict"] == "LỖI" and not a.force:
        vslib.die("clip chưa đạt, sửa rồi chạy lại hoặc thêm --force")

    c = vslib.client()
    if any(p["name"] == a.name for p in c.get("/profiles").json()):
        vslib.die(f"đã có profile tên {a.name}")
    with open(a.clip, "rb") as f:
        r = c.post("/profiles", files={"ref_audio": (a.clip.name, f, "audio/wav")},
                   data={"name": a.name, "ref_text": text, "language": "Vietnamese"})
    if r.status_code != 200:
        vslib.die(vslib.api_error(r))
    p = r.json()
    print(f"Đã tạo profile {p['name']}, id: {p['id']}")
    print("Việc còn lại trong app: xác nhận đây là giọng của bạn (consent) nếu app yêu cầu.")
    print(f'Thử ngay: uv run scripts/speak.py {p["id"]} "Ma, mà, má, mả, mã, mạ. Bà ba bán bánh bò."')


if __name__ == "__main__":
    main()
