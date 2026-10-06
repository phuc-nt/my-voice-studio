#!/usr/bin/env python3
"""Chấm điểm các file đã tạo: độ giống clip mẫu, độ sạch (DNSMOS) và chữ bị nuốt.

Dùng được cho thư mục của ab-test.sh (outputs/ab-*) và của speak.py (outputs/speak-*).
Điểm giống giọng lấy từ model huấn luyện trên tiếng Anh, nên chỉ để so tương đối giữa các
cấu hình của cùng một giọng. Tai người vẫn là phép đo cuối cùng.

Dùng:
  uv run scripts/score.py outputs/ab-261004-201500 --profile <profile_id>
  uv run scripts/score.py outputs/ab-261004-201500 --ref recordings/tro-chuyen-01-take2.wav
  uv run scripts/score.py a.wav b.wav --ref clip.wav --text "Câu đã đọc." --no-asr
"""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

import vslib


def texts_for(files: list[Path], fallback: str | None) -> dict[Path, str]:
    """Văn bản gốc của từng file: từ report.json (speak.py), text.txt (ab-test.sh) hoặc --text."""
    out = {}
    for f in files:
        report, single = f.parent / "report.json", f.parent / "text.txt"
        if report.exists() and f.stem.startswith("chunk-"):
            chunks = {i["n"]: i["text"] for i in json.loads(report.read_text(encoding="utf-8"))["chunks"]}
            out[f] = chunks.get(int(f.stem.split("-")[1]), "")
        elif fallback:
            out[f] = fallback
        elif single.exists() and f.stem != "final":
            out[f] = single.read_text(encoding="utf-8").strip()
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", help="file WAV hoặc thư mục kết quả")
    ap.add_argument("--ref", type=Path, help="clip mẫu để so độ giống")
    ap.add_argument("--profile", help="lấy clip mẫu từ profile này trong VoiceStudio")
    ap.add_argument("--text", help="văn bản gốc, nếu thư mục không có text.txt hay report.json")
    ap.add_argument("--no-asr", action="store_true", help="không chép lời để soát chữ")
    a = ap.parse_args()

    files = [f for f in vslib.audio_files(a.paths) if ".tmp" not in f.name]
    if not files:
        vslib.die("không có file audio nào")
    texts = texts_for(files, a.text)
    c = vslib.client() if (a.profile or (texts and not a.no_asr)) else None

    ref = a.ref
    if a.profile:
        ref = vslib.profile_audio(c, a.profile, Path(tempfile.mkdtemp()) / "ref.wav")
    ref_emb = vslib.speaker_embedding(ref) if ref else None

    rows = []
    for f in files:
        row = {"file": f.name, "sim": vslib.similarity(ref_emb, vslib.speaker_embedding(f)) if ref else "",
               **vslib.dnsmos(vslib.load_audio(f, 16000)), "wer": "", "missing": "", "heard": ""}
        if f in texts and not a.no_asr:
            try:
                row["heard"] = vslib.transcribe(c, f)
                cmp = vslib.compare(texts[f], row["heard"])
                row["wer"], row["missing"] = cmp["wer"], "; ".join(cmp["missing"])
            except RuntimeError as e:
                row["heard"] = f"(chưa chép lời được: {e})"
        rows.append(row)

    rows.sort(key=lambda r: -(r["sim"] or 0))
    cols = ["file", "sim", "sig", "bak", "ovrl", "wer", "missing", "heard"]
    print(f"{'file':40} {'giống':>6} {'giọng':>6} {'nền':>5} {'tổng':>5} {'sai':>6}  thiếu")
    for r in rows:
        print(f"{r['file'][:40]:40} {r['sim']!s:>6} {r['sig']:>6} {r['bak']:>5} {r['ovrl']:>5} {r['wer']!s:>6}  {r['missing']}")

    dirs = {f.parent for f in files}
    if len(dirs) == 1:
        tsv = dirs.pop() / "scores.tsv"
        tsv.write_text("\n".join(["\t".join(cols)] + ["\t".join(str(r[k]) for k in cols) for r in rows]) + "\n",
                       encoding="utf-8")
        print(f"\nĐã ghi {tsv}")


if __name__ == "__main__":
    main()
