#!/usr/bin/env python3
"""Dò dấu nhận biết giọng tổng hợp (AudioSeal) mà VoiceStudio gắn vào audio đã tạo.

Nhận mọi file audio hoặc video ffmpeg đọc được (WAV, M4A, MP4...). Endpoint của app chỉ đọc
WAV mono, nên script tự tách tiếng và gộp về mono trước khi gửi. File không rời khỏi máy.

Dấu chịu được đổi tần số mẫu, chuẩn hoá độ to và mã hoá AAC, nhưng có thể mất khi trộn nền
dày lên trên giọng. Kết quả "không thấy dấu" trên bản đã trộn vì vậy không chứng minh audio
không phải giọng tổng hợp; hãy giữ tệp giọng chưa trộn để đối chiếu.

Dùng:
  uv run scripts/check-watermark.py giong.wav video.mp4
  uv run scripts/check-watermark.py --json video.mp4
"""
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

import vslib


def detect(c, path: Path) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "mono.wav"
        r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-vn", "-ac", "1", str(wav)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            vslib.die(f"không đọc được {path}: {r.stderr.strip()}")
        with open(wav, "rb") as f:
            res = c.post("/watermark/detect", files={"file": ("mono.wav", f)})
    if res.status_code != 200:
        vslib.die(f"không dò được {path.name}: {vslib.api_error(res)}")
    data = res.json()
    if data.get("error"):
        vslib.die(f"không dò được {path.name}: {data['error']}")
    return {"file": path.name, "watermarked": bool(data["is_watermarked"]),
            "confidence": round(float(data["confidence"]), 3), "source": data.get("source")}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", type=Path, nargs="+")
    ap.add_argument("--json", action="store_true", help="in JSON thay vì bảng")
    a = ap.parse_args()

    c = vslib.client()
    results = [detect(c, f) for f in a.files]
    if a.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return
    for r in results:
        verdict = "CÓ DẤU" if r["watermarked"] else "KHÔNG THẤY DẤU"
        print(f"{r['file']:<40} {verdict:<15} độ tin cậy {r['confidence']:.2f}")


if __name__ == "__main__":
    main()
