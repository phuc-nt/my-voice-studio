#!/usr/bin/env python3
"""Đọc một văn bản bằng giọng đã clone, từng đoạn ngắn, có soát chữ bị nuốt và tự tạo lại.

Cách làm:
  1. Chia văn bản: mỗi dòng là một đoạn văn, đoạn dài được chia tiếp theo câu (--max-chars).
  2. Tạo từng đoạn qua API /generate với Language Vietnamese.
  3. Cho Whisper của VoiceStudio chép lại lời, so với văn bản. Đoạn thiếu chữ được tạo lại
     với seed khác (tối đa --retries lần), giữ bản ít lỗi nhất.
  4. Ghép các đoạn thành final.wav và ghi report.json.

Dùng:
  uv run scripts/speak.py <profile_id> "Câu cần đọc."
  uv run scripts/speak.py <profile_id> -f bai-viet.txt --engine voxcpm2
  uv run scripts/speak.py --redo outputs/speak-261004-201500 3 7      # tạo lại đoạn 3 và 7
  uv run scripts/speak.py --redo outputs/speak-261004-201500 3 --text "Câu đã viết lại."

Văn bản nên được viết số thành chữ trước (scripts/normalize-vi.py), nếu không phép so chữ sẽ báo sai.
"""
from __future__ import annotations

import argparse
import json
import re
import time
import unicodedata
from pathlib import Path

import numpy as np
import soundfile as sf

import vslib

SENTENCE_END = re.compile(r"(?<=[.!?…])\s+")
CLAUSE_END = re.compile(r"(?<=[,;:])\s+")


def pack(pieces: list[str], limit: int) -> list[str]:
    out, cur = [], ""
    for p in pieces:
        if cur and len(cur) + 1 + len(p) > limit:
            out.append(cur)
            cur = p
        else:
            cur = f"{cur} {p}".strip()
    return out + [cur] if cur else out


def chunk(text: str, limit: int) -> list[str]:
    """Mỗi dòng là một đoạn văn. Đoạn dài hơn `limit` ký tự được chia theo câu, rồi theo dấu phẩy."""
    chunks = []
    for line in unicodedata.normalize("NFC", text).splitlines():
        line = " ".join(line.split())
        if not line:
            continue
        if len(line) <= limit:
            chunks.append(line)
            continue
        sentences = []
        for s in SENTENCE_END.split(line):
            sentences += [s] if len(s) <= limit else pack(CLAUSE_END.split(s), limit)
        chunks += pack(sentences, limit)
    return chunks


def render(c, item: dict, cfg: dict, out: Path, verify: bool) -> bool:
    """Tạo một đoạn, thử lại với seed khác khi thiếu chữ. Trả về False nếu không chép lời được."""
    wav = out / f"chunk-{item['n']:03d}.wav"
    best = None
    seed = item["seed"]
    for attempt in range(1, cfg["retries"] + 2):
        audio, meta = vslib.generate(c, item["text"], cfg["profile"], engine=cfg["engine"], steps=cfg["steps"],
                                     seed=seed, cfg=cfg["cfg"], speed=cfg["speed"], bits=cfg["bits"])
        tmp = wav.with_suffix(".tmp.wav")
        tmp.write_bytes(audio)
        res = {"seed": seed, "tries": attempt, **meta}
        if verify:
            try:
                res["heard"] = vslib.transcribe(c, tmp)
            except RuntimeError as e:
                print(f"  Không chép lời được ({e}). Bỏ bước soát chữ.")
                verify = False
        if verify:
            res.update(vslib.compare(item["text"], res["heard"]))
            score = (sum(len(m.split()) for m in res["missing"]), res["wer"])
        else:
            score = (0, 0.0)
        if best is None or score < best[0]:
            best = (score, res)
            tmp.replace(wav)
        else:
            tmp.unlink()
        if not verify or (score[0] == 0 and score[1] <= cfg["max_wer"]):
            break
        seed += 1
    res = {**best[1], "tries": attempt}
    res["flag"] = bool(verify and (res["missing"] or res["wer"] > cfg["max_wer"]))
    for k in ("heard", "missing", "extra", "changed", "wer"):
        item.pop(k, None)
    item.update(res)
    mark = "CẦN XEM" if res["flag"] else ("ổn" if verify else "chưa soát")
    print(f"[{item['n']:03d}] {mark}, seed {res['seed']}, {res['tries']} lần, "
          f"{res['gen_s']:.1f}s tạo {res['audio_s']:.1f}s: {item['text'][:60]}")
    if res["flag"]:
        for label, key in (("thiếu", "missing"), ("thừa", "extra"), ("khác", "changed")):
            if res[key]:
                print(f"      {label}: {'; '.join(res[key])}")
    return verify


def stitch(out: Path, report: dict) -> None:
    parts, sr = [], None
    for item in report["chunks"]:
        y, this_sr = sf.read(out / f"chunk-{item['n']:03d}.wav", dtype="float32")
        sr = sr or this_sr
        if this_sr != sr:
            vslib.die("các đoạn khác tần số mẫu, không ghép được")
        parts += [y, np.zeros(int(sr * report["gap_ms"] / 1000), dtype=np.float32)]
    sf.write(out / "final.wav", np.concatenate(parts[:-1]), sr, subtype=f"PCM_{report['bits']}")
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("profile", nargs="?", help="profile_id (xem: curl -s http://127.0.0.1:3900/profiles)")
    ap.add_argument("text", nargs="?")
    ap.add_argument("-f", "--file", type=Path, help="đọc văn bản từ file")
    ap.add_argument("--redo", nargs="+", metavar=("DIR", "N"), help="tạo lại các đoạn N trong thư mục kết quả DIR")
    ap.add_argument("--text", dest="new_text", help="với --redo: văn bản thay cho đoạn được tạo lại")
    ap.add_argument("--engine", default="omnivoice")
    ap.add_argument("--steps", type=int, default=32)
    ap.add_argument("--cfg", type=float, default=2.0)
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--seed", type=int, help="mặc định 42; với --redo mặc định là seed cũ cộng 1")
    ap.add_argument("--retries", type=int, default=2, help="số lần tạo lại khi thiếu chữ")
    ap.add_argument("--max-wer", type=float, default=0.15, help="tỉ lệ chữ sai tối đa được coi là ổn")
    ap.add_argument("--max-chars", type=int, default=220, help="độ dài tối đa mỗi đoạn, khoảng 15 giây âm thanh")
    ap.add_argument("--gap-ms", type=int, default=300, help="khoảng lặng giữa các đoạn khi ghép")
    ap.add_argument("--bits", type=int, choices=(16, 24), default=16)
    ap.add_argument("--no-verify", action="store_true", help="không chép lời để soát chữ")
    a = ap.parse_args()
    c = vslib.client()

    if a.redo:
        out = Path(a.redo[0])
        report = json.loads((out / "report.json").read_text(encoding="utf-8"))
        todo = {int(n) for n in a.redo[1:]}
        if not todo or not todo <= {i["n"] for i in report["chunks"]}:
            vslib.die(f"nêu số đoạn cần tạo lại, từ 1 đến {len(report['chunks'])}")
        new_text = a.new_text
        if new_text and len(todo) != 1:
            vslib.die("--text chỉ dùng khi tạo lại đúng một đoạn")
        for item in report["chunks"]:
            if item["n"] in todo:
                if new_text:
                    item["text"] = " ".join(unicodedata.normalize("NFC", new_text).split())
                item["seed"] = a.seed if a.seed is not None else item["seed"] + 1
                render(c, item, report, out, not a.no_verify)
        stitch(out, report)
        print(f"Đã ghép lại {out / 'final.wav'}")
        return

    if not a.profile:
        vslib.die("thiếu profile_id")
    text = a.text if a.text is not None else (a.file.read_text(encoding="utf-8") if a.file else "")
    chunks = chunk(text, a.max_chars)
    if not chunks:
        vslib.die("thiếu văn bản cần đọc")
    if any(ch.isdigit() for ch in vslib.TAG_RE.sub("", text)):
        print("Lưu ý: văn bản còn chữ số. Model tự đọc số và phép so chữ có thể báo sai. "
              "Nên chạy scripts/normalize-vi.py trước.")

    out = vslib.ROOT / "outputs" / f"speak-{time.strftime('%y%m%d-%H%M%S')}"
    out.mkdir(parents=True)
    report = {"profile": a.profile, "engine": a.engine, "steps": a.steps, "cfg": a.cfg, "speed": a.speed,
              "bits": a.bits, "retries": a.retries, "max_wer": a.max_wer, "gap_ms": a.gap_ms,
              "chunks": [{"n": i, "text": t, "seed": a.seed if a.seed is not None else 42}
                         for i, t in enumerate(chunks, 1)]}
    verify = not a.no_verify
    for item in report["chunks"]:
        try:
            verify = render(c, item, report, out, verify)
        except RuntimeError as e:
            vslib.die(f"đoạn {item['n']}: {e}")
    stitch(out, report)

    flagged = [i["n"] for i in report["chunks"] if i.get("flag")]
    total = sum(i["audio_s"] for i in report["chunks"])
    print(f"\nĐã lưu {(out / 'final.wav').relative_to(vslib.ROOT)} ({total:.1f}s, {len(chunks)} đoạn)")
    if flagged:
        print(f"Đoạn cần nghe lại: {' '.join(map(str, flagged))}. "
              f"Tạo lại: uv run scripts/speak.py --redo {out.relative_to(vslib.ROOT)} {' '.join(map(str, flagged))}")
    elif not verify:
        print("Chưa soát chữ. Cần tải Whisper large-v3 (MLX) trong Model Catalogue.")


if __name__ == "__main__":
    main()
