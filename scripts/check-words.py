#!/usr/bin/env python3
"""Soát chữ bị rơi trong các câu đã tạo: chép lời lại bằng Whisper rồi so với chữ đã gửi đi.

Luật soát do bên giữ giọng định, để mọi bên dùng giọng soát giống nhau. Mỗi câu có một kết luận:
  ĐẠT       không thiếu chữ nào, tỉ lệ chữ khác không quá --max-wer (mặc định 0,15)
  XEM LẠI   không thiếu chữ, nhưng Whisper nghe ra nhiều chữ khác: cần người nghe
  RƠI CHỮ   có chữ trong văn bản mà Whisper không nghe thấy: tạo lại với seed khác

So có dấu thanh, bỏ dấu câu và chữ hoa. Để bớt báo oan, trước khi so: số Whisper viết bằng chữ
số được đổi thành chữ ("8 600" thành "tám ngàn sáu trăm"), "nghìn" coi như "ngàn", chữ viết
liền hay rời coi như nhau ("man ga" và "manga"), và với [[EPUB|i-pắp]] thì nghe ra "epub" hay
"i pắp" đều tính là đúng. Phiên âm viết thẳng vào chữ (không dùng [[...]]) vẫn bị báo "khác".

Whisper cũng nghe sai tiếng Việt, và tự sửa thanh điệu theo ngữ cảnh: lệnh này không bắt được
lỗi sai thanh, và XEM LẠI thường là lỗi chép lời. File không rời máy.

Dùng:
  uv run scripts/check-words.py cau.wav --text "Chữ đã gửi đi."
  uv run scripts/check-words.py --manifest cau.json [--json] [-o soat.json]
      # cau.json: [{"file": "001.wav", "text": "..."}, ...]; đường dẫn tính từ thư mục chứa cau.json

Mã thoát: 0 khi mọi câu ĐẠT, 1 khi có câu XEM LẠI, 2 khi có câu RƠI CHỮ.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import vslib

ALT_RE = re.compile(r"\[\[([^\]|]+)\|([^\]]+)\]\]")
_norm = None


def plain(text: str) -> str:
    """Đưa chữ về một cách viết: số thành chữ, "nghìn" thành "ngàn"."""
    global _norm
    if any(ch.isdigit() for ch in text):
        if _norm is None:
            from sea_g2p import Normalizer
            _norm = Normalizer(lang="vi")
        text = re.sub(r"</?en>", "", _norm.normalize(text))
    return re.sub(r"\bnghìn\b", "ngàn", text.lower())


def check(text: str, heard: str, max_wer: float) -> dict:
    alts = {"".join(vslib.words(b)): "".join(vslib.words(a)) for a, b in ALT_RE.findall(text)}
    cmp = vslib.compare(plain(vslib.spoken(text)), plain(heard))
    changed = []
    for pair in cmp["changed"]:
        want, got = ("".join(x.split()) for x in pair.split(" → "))
        if want != got and alts.get(want) != got:
            changed.append(pair)
    n = len(vslib.words(vslib.spoken(text)))
    errors = sum(len(x.split()) for x in cmp["missing"] + cmp["extra"]) + sum(
        max(len(x.split()), len(y.split())) for x, y in (p.split(" → ") for p in changed))
    wer = round(errors / max(n, 1), 3)
    verdict = "RƠI CHỮ" if cmp["missing"] else ("XEM LẠI" if wer > max_wer else "ĐẠT")
    return {"verdict": verdict, "ok": verdict == "ĐẠT", "missing": cmp["missing"], "changed": changed,
            "extra": cmp["extra"], "wer": wer}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", type=Path, nargs="?", help="file audio của một câu")
    ap.add_argument("--manifest", type=Path, help="JSON liệt kê nhiều câu: [{\"file\", \"text\"}]")
    ap.add_argument("--text", help="chữ đã gửi đi để tạo câu này")
    ap.add_argument("--max-wer", type=float, default=0.15, help="tỉ lệ chữ khác tối đa được coi là đạt")
    ap.add_argument("--json", action="store_true", help="in JSON thay vì bảng")
    ap.add_argument("-o", "--out", type=Path, help="ghi JSON ra file")
    a = ap.parse_args()

    if a.manifest:
        jobs = [(a.manifest.parent / i["file"], i["text"]) for i in json.loads(a.manifest.read_text(encoding="utf-8"))]
    elif a.path and a.text:
        jobs = [(a.path, a.text)]
    else:
        vslib.die("cần một file kèm --text, hoặc --manifest")

    c = vslib.client()
    results = []
    for path, text in jobs:
        try:
            heard = vslib.transcribe(c, path)
        except RuntimeError as e:
            vslib.die(f"không chép lời được {path.name}: {e}")
        results.append({"file": path.name, **check(text, heard, a.max_wer), "heard": heard})

    data = json.dumps(results, ensure_ascii=False, indent=2)
    if a.out:
        a.out.write_text(data + "\n", encoding="utf-8")
    if a.json:
        print(data)
    else:
        for r in results:
            print(f"{r['file']:<32} {r['verdict']:<8} khác {r['wer']:.2f}")
            for label, key in (("thiếu", "missing"), ("khác", "changed"), ("thừa", "extra")):
                if r[key]:
                    print(f"    {label}: {'; '.join(r[key])}")
    verdicts = {r["verdict"] for r in results}
    sys.exit(2 if "RƠI CHỮ" in verdicts else 1 if "XEM LẠI" in verdicts else 0)


if __name__ == "__main__":
    main()
