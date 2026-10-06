#!/usr/bin/env python3
"""Mốc thời gian từng từ của một câu đã tạo, gióng theo chữ đã biết (forced alignment).

Không nhận dạng lại lời: script lấy đúng chữ bạn đưa vào rồi dùng Whisper large-v3 để tìm
mỗi từ nằm ở đâu trong audio. Vì vậy số từ trả về luôn bằng số từ trong chữ, kể cả khi
model đọc sai hoặc nuốt một từ; khi đó mốc của từ ấy không đáng tin. Mỗi file nên là một câu,
dài dưới 30 giây.

Mốc tính bằng giây, từ đầu file. Kết quả là JSON in ra stdout:
  {"file", "duration", "speech_start", "speech_end", "words": [{"word", "start", "end"}]}

Dùng:
  uv run scripts/word-times.py cau.wav --text "Chữ đã gửi đi."
  uv run scripts/word-times.py cau.wav --text-file cau.txt -o cau.words.json
  uv run scripts/word-times.py outputs/speak-<thời gian>      # mọi chunk, chữ lấy từ report.json
  uv run scripts/word-times.py --manifest cau.json -o words.json
      # cau.json: [{"file": "001.wav", "text": "..."}, ...]; đường dẫn tính từ thư mục chứa cau.json

Gọi từ repo khác:
  uv run --project ~/workspace/my-voice-studio ~/workspace/my-voice-studio/scripts/word-times.py ...
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

import vslib

MODEL = "mlx-community/whisper-large-v3-mlx"
SR = 16000
FRAME = 0.02
SILENCE = 0.12
GAP = 0.25  # chỗ ngắt giữa hai câu; dài hơn mọi phụ âm tắc
LOUD = 30  # dB dưới khung to nhất; tiếng lấy hơi nằm dưới mức này
PAD = 0.1  # giây giữ lại quanh tiếng nói; khoảng lặng dài ở đầu làm Whisper đặt từ đầu quá sớm


def tighten(mask: np.ndarray, s: float, e: float) -> tuple[float, float]:
    """Đẩy mốc ra khỏi khoảng lặng: Whisper gán chỗ ngắt hơi vào từ đứng cạnh nó.

    Chỉ cắt quãng lặng từ SILENCE giây trở lên, để không cắt nhầm phụ âm tắc ở đầu và cuối từ.
    """
    a, b = int(s / FRAME), int(np.ceil(e / FRAME))
    voiced = np.flatnonzero(mask[a:b])
    if not len(voiced):
        return s, e
    if voiced[0] * FRAME >= SILENCE:
        s = (a + voiced[0]) * FRAME
    if (b - a - 1 - voiced[-1]) * FRAME >= SILENCE:
        e = (a + voiced[-1] + 1) * FRAME
    return s, e


def skip_gap(loud: np.ndarray, s: float, e: float) -> tuple[float, float | None]:
    """Chỗ ngắt giữa hai câu nằm lọt trong khoảng của một từ: Whisper đặt mốc đầu của từ ấy vào
    đuôi của từ trước. Dời mốc đầu tới chỗ tiếng nói bắt đầu lại, và trả kèm chỗ tiếng nói dừng
    trước chỗ ngắt để kéo mốc cuối của từ trước tới đó.

    `loud` dùng ngưỡng cao hơn `voiced_mask` để tiếng lấy hơi trong chỗ ngắt không bị tính là lời.
    """
    a, b = int(s / FRAME), int(np.ceil(e / FRAME))
    on = np.flatnonzero(loud[a:b])
    if len(on) < 2:
        return s, None
    gaps = np.diff(on) - 1
    k = int(gaps.argmax())
    if gaps[k] * FRAME < GAP or len(on) - (k + 1) < 2:
        return s, None
    return (a + on[k + 1]) * FRAME, (a + on[k] + 1) * FRAME


def align(model, tokenizer, path: Path, text: str) -> dict:
    from mlx_whisper import audio, timing

    y = vslib.load_audio(path, SR)
    duration = len(y) / SR
    if duration > 30:
        vslib.die(f"{path.name} dài {duration:.1f}s; mỗi file chỉ nên là một câu dưới 30 giây")
    fdb = vslib.frame_db(y, SR)
    mask, loud = vslib.voiced_mask(fdb), fdb >= fdb.max() - LOUD
    voiced = np.flatnonzero(mask)
    if not len(voiced):
        vslib.die(f"không thấy tiếng nói trong {path.name}")
    start, end = voiced[0] * FRAME, (voiced[-1] + 1) * FRAME
    offset = max(0.0, start - PAD)
    clip = y[int(offset * SR):int(min(duration, end + PAD) * SR)]

    words = vslib.spoken(text).split()
    if not words:
        vslib.die(f"không có chữ để gióng cho {path.name}")
    mel = audio.log_mel_spectrogram(clip, n_mels=model.dims.n_mels, padding=audio.N_SAMPLES)
    num_frames = mel.shape[0] - audio.N_FRAMES
    tokens = tokenizer.encode(" " + " ".join(words))
    found = timing.find_alignment(model, tokenizer, tokens, audio.pad_or_trim(mel, audio.N_FRAMES, axis=0), num_frames)
    pieces = [w for w in found if w.word.strip()]

    # Whisper tách dấu câu thành mẩu riêng; gộp các mẩu lại cho khớp từng từ của chữ gốc.
    out, i = [], 0
    for word in words:
        got, first = "", i
        while i < len(pieces) and got != word:
            got += pieces[i].word.strip()
            i += 1
        if got != word:
            vslib.die(f"{path.name}: không ghép được mốc cho từ '{word}'")
        s = min(max(pieces[first].start + offset, start), end)
        e = min(max(pieces[i - 1].end + offset, s), end)
        s, before = skip_gap(loud, s, e)
        if before is not None and out:
            out[-1]["end"] = round(max(out[-1]["end"], before), 3)
        s, e = tighten(mask, s, e)
        out.append({"word": word, "start": round(s, 3), "end": round(e, 3)})
    return {"file": path.name, "duration": round(duration, 3), "speech_start": round(start, 3),
            "speech_end": round(end, 3), "words": out}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", type=Path, nargs="?", help="file audio của một câu, hoặc thư mục outputs/speak-*")
    ap.add_argument("--manifest", type=Path, help="JSON liệt kê nhiều câu: [{\"file\", \"text\"}]")
    ap.add_argument("--text", help="chữ đã gửi đi để tạo câu này")
    ap.add_argument("--text-file", type=Path)
    ap.add_argument("-o", "--out", type=Path, help="ghi JSON ra file thay vì stdout")
    a = ap.parse_args()

    many = bool(a.manifest) or (a.path is not None and a.path.is_dir())
    if a.manifest:
        jobs = [(a.manifest.parent / i["file"], i["text"]) for i in json.loads(a.manifest.read_text(encoding="utf-8"))]
    elif a.path is None:
        vslib.die("cần một file, một thư mục outputs/speak-*, hoặc --manifest")
    elif a.path.is_dir():
        report = a.path / "report.json"
        if not report.exists():
            vslib.die(f"{a.path} không có report.json")
        jobs = [(a.path / f"chunk-{c['n']:03d}.wav", c["text"])
                for c in json.loads(report.read_text(encoding="utf-8"))["chunks"]]
    else:
        text = a.text_file.read_text(encoding="utf-8") if a.text_file else a.text
        if not text:
            vslib.die("cần --text hoặc --text-file")
        jobs = [(a.path, text)]

    try:
        from mlx_whisper import load_models, tokenizer as tk
        model = load_models.load_model(MODEL)
    except Exception as e:  # thiếu model trong cache, hoặc máy không phải Apple Silicon
        vslib.die(f"không nạp được {MODEL}: {e}")
    tokenizer = tk.get_tokenizer(True, num_languages=model.num_languages, language="vi", task="transcribe")

    results = [align(model, tokenizer, p, t) for p, t in jobs]
    data = json.dumps(results if many else results[0], ensure_ascii=False, indent=2)
    if a.out:
        a.out.write_text(data + "\n", encoding="utf-8")
        print(f"Đã ghi {a.out}", file=sys.stderr)
    else:
        print(data)


if __name__ == "__main__":
    main()
