#!/usr/bin/env python3
"""Đo clip mẫu theo các tiêu chí trong docs/voice-prep-guide-vietnamese.md và xếp hạng các take.

Dùng:
  uv run scripts/check-clip.py recordings/                     # mọi clip trong thư mục
  uv run scripts/check-clip.py recordings/tro-chuyen-01-*.wav  # so các take của một câu
  uv run scripts/check-clip.py --asr clip.wav                  # kèm lời do Whisper chép lại
  uv run scripts/check-clip.py --json clip.wav                 # in JSON cho công cụ khác đọc

Mã thoát là 1 nếu có clip nào bị "LỖI".
"""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np
import pyloudnorm

import vslib

SR = 48000


def measure(path) -> dict:
    info = vslib.probe(path)
    y = vslib.load_audio(path, SR)
    fdb = vslib.frame_db(y, SR)
    peak = vslib.db(float(np.abs(y).max()))
    # Khung im lặng tính theo ngưỡng tương đối so với đỉnh và nền, để clip thu nhỏ hoặc có nền ồn vẫn đo đúng.
    quiet = ~vslib.voiced_mask(fdb)
    voiced = np.flatnonzero(~quiet)
    lead = voiced[0] * 0.02 if len(voiced) else info["duration"]
    trail = (len(fdb) - 1 - voiced[-1]) * 0.02 if len(voiced) else 0.0
    longest, run = 0, 0
    for q in quiet[voiced[0]:voiced[-1]] if len(voiced) else []:
        run = run + 1 if q else 0
        longest = max(longest, run)
    # Nền ồn: quãng 100 ms yên nhất trong clip (chỗ ngắt hơi hoặc phần đệm hai đầu).
    noise = vslib.noise_floor(fdb)
    speech = float(np.percentile(fdb, 95))
    m = {
        "file": str(path), **info,
        "peak_db": round(peak, 1),
        "lufs": round(float(pyloudnorm.Meter(SR).integrated_loudness(y)), 1) if len(y) > SR * 0.4 else None,
        "clipped": int((np.abs(y) >= 0.999).sum()),
        "lead_s": round(float(lead), 2), "trail_s": round(float(trail), 2),
        "pause_s": round(longest * 0.02, 2),
        "noise_db": round(noise, 1), "snr_db": round(speech - noise, 1),
        **vslib.dnsmos(vslib.load_audio(path, 16000)),
    }
    m["issues"] = judge(m)
    m["verdict"] = "LỖI" if any(i.startswith("LỖI") for i in m["issues"]) else ("XEM LẠI" if m["issues"] else "ĐẠT")
    return m


def judge(m: dict) -> list[str]:
    """Ngưỡng độ dài, định dạng và mức âm lấy từ hướng dẫn. Ngưỡng nhiễu và DNSMOS là ước lượng."""
    out = []
    d = m["duration"]
    if d > 20:
        out.append("LỖI: dài hơn 20 giây, VoiceStudio sẽ cắt hoặc từ chối")
    elif d > 10:
        out.append("dài hơn 10 giây, nên cắt còn 6–10 giây")
    elif d < 3:
        out.append("LỖI: ngắn hơn 3 giây")
    elif d < 6:
        out.append("ngắn hơn 6 giây, vẫn dùng được nhưng 6–10 giây tốt hơn")
    if m["clipped"]:
        out.append(f"LỖI: vỡ tiếng ({m['clipped']} mẫu chạm 0 dBFS), phải thu lại")
    elif m["peak_db"] > -3:
        out.append(f"đỉnh {m['peak_db']} dBFS quá sát 0, nên giảm gain")
    if m["peak_db"] < -20:
        out.append(f"đỉnh {m['peak_db']} dBFS quá nhỏ, nên tăng gain hoặc lại gần mic")
    if m["sample_rate"] < 24000:
        out.append(f"LỖI: tần số mẫu {m['sample_rate']} Hz thấp hơn 24 kHz")
    if m["codec"] in {"mp3", "aac", "vorbis", "opus"}:
        out.append(f"định dạng nén mất dữ liệu ({m['codec']}), nên thu WAV hoặc lossless")
    if m["channels"] != 1:
        out.append("không phải mono, chạy prep-clip.py để gộp kênh")
    if m["lead_s"] > 0.3 or m["trail_s"] > 0.3:
        out.append(f"khoảng lặng đầu {m['lead_s']}s, cuối {m['trail_s']}s, chạy prep-clip.py để cắt")
    if m["pause_s"] > 1.0:
        out.append(f"có khoảng lặng {m['pause_s']}s giữa clip")
    if m["noise_db"] > -50:
        out.append(f"nền ồn {m['noise_db']} dBFS, tiếng nói chỉ hơn nền {m['snr_db']} dB (ước lượng): "
                   "kiểm tra quạt, máy lạnh, hoặc clip không có chỗ ngắt hơi nào để đo")
    if m["bak"] < 3.5:
        out.append(f"DNSMOS nền {m['bak']} thấp: có ồn hoặc vang")
    if m["sig"] < 3.0:
        out.append(f"DNSMOS giọng {m['sig']} thấp: giọng bị méo, xa mic hoặc vang")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", help="file audio hoặc thư mục")
    ap.add_argument("--asr", action="store_true", help="chép lời bằng Whisper của VoiceStudio")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    files = vslib.audio_files(a.paths)
    if not files:
        vslib.die("không có file audio nào")
    c = vslib.client() if a.asr else None
    rows = []
    for f in files:
        m = measure(f)
        if c:
            try:
                m["heard"] = vslib.transcribe(c, f)
            except RuntimeError as e:
                m["heard"] = f"(chưa chép lời được: {e})"
        rows.append(m)

    # Xếp hạng: clip đạt trước, rồi theo điểm DNSMOS tổng thể.
    order = {"ĐẠT": 0, "XEM LẠI": 1, "LỖI": 2}
    rows.sort(key=lambda m: (order[m["verdict"]], -m["ovrl"]))

    if a.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        for m in rows:
            print(f"\n{m['verdict']:8} {m['file']}")
            print(f"  {m['duration']:.1f}s  {m['codec']} {m['sample_rate']}Hz {m['channels']}ch"
                  f"  đỉnh {m['peak_db']} dBFS  {m['lufs']} LUFS  nền {m['noise_db']} dBFS"
                  f"  DNSMOS giọng {m['sig']} / nền {m['bak']} / tổng {m['ovrl']}")
            for i in m["issues"]:
                print(f"  - {i}")
            if "heard" in m:
                print(f"  nghe được: {m['heard']}")
    sys.exit(1 if any(m["verdict"] == "LỖI" for m in rows) else 0)


if __name__ == "__main__":
    main()
