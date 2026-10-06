"""Phần dùng chung của các script: gọi API VoiceStudio, đọc audio, so chữ, đo độ giống giọng."""
from __future__ import annotations

import difflib
import json
import os
import re
import subprocess
import sys
import unicodedata
import urllib.request
from pathlib import Path

import httpx
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
API = os.environ.get("VOICESTUDIO_API", "http://127.0.0.1:3900")
SPEAKER_MODEL = ROOT / "models" / "wespeaker_en_voxceleb_resnet34_LM.onnx"
SPEAKER_MODEL_URL = (
    "https://github.com/k2-fsa/sherpa-onnx/releases/download/"
    "speaker-recongition-models/wespeaker_en_voxceleb_resnet34_LM.onnx"
)
AUDIO_EXT = {".wav", ".m4a", ".mp3", ".flac", ".aac", ".ogg", ".aiff", ".aif", ".caf"}

# Tag VoiceStudio hiểu: [pause 500ms], [laughter], [[phiên âm]]. Không tính là chữ cần đọc.
TAG_RE = re.compile(r"\[\[.*?\]\]|\[[^\[\]]*\]")


def die(msg: str) -> None:
    sys.exit(f"Lỗi: {msg}")


# ── Audio ────────────────────────────────────────────────────────────────────

def probe(path: Path) -> dict:
    """Thông số gốc của file (codec, tần số mẫu, số kênh, độ dài) lấy bằng ffprobe."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
         "stream=codec_name,sample_rate,channels,bits_per_raw_sample,bits_per_sample:format=duration",
         "-of", "json", str(path)],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        die(f"không đọc được {path}: {out.stderr.strip()}")
    data = json.loads(out.stdout)
    s = data["streams"][0]
    bits = int(s.get("bits_per_raw_sample") or s.get("bits_per_sample") or 0)
    return {
        "codec": s["codec_name"],
        "sample_rate": int(s["sample_rate"]),
        "channels": int(s["channels"]),
        "bits": bits,
        "duration": float(data["format"]["duration"]),
    }


def load_audio(path: Path, sr: int, start: float | None = None, end: float | None = None) -> np.ndarray:
    """Giải mã mọi định dạng thành float32 mono ở tần số `sr` bằng ffmpeg."""
    cmd = ["ffmpeg", "-v", "error"]
    if start is not None:
        cmd += ["-ss", str(start)]
    if end is not None:
        cmd += ["-to", str(end)]
    cmd += ["-i", str(path), "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"]
    out = subprocess.run(cmd, capture_output=True)
    if out.returncode != 0:
        die(f"ffmpeg không giải mã được {path}: {out.stderr.decode().strip()}")
    return np.frombuffer(out.stdout, dtype=np.float32).copy()


def db(x: float) -> float:
    return 20 * float(np.log10(max(x, 1e-9)))


def frame_db(y: np.ndarray, sr: int, ms: int = 20) -> np.ndarray:
    """Mức RMS (dBFS) của từng khung `ms` mili giây."""
    n = max(1, sr * ms // 1000)
    frames = y[: len(y) // n * n].reshape(-1, n)
    if len(frames) == 0:
        return np.array([db(0)])
    return 20 * np.log10(np.maximum(np.sqrt((frames ** 2).mean(axis=1)), 1e-9))


def noise_floor(fdb: np.ndarray) -> float:
    """Mức nền: quãng 100 ms yên nhất, không tính các khung im lặng số (dưới −100 dBFS)."""
    real = fdb[fdb > -100]
    if len(real) < 5:
        return float(fdb.min())
    return float(np.convolve(real, np.ones(5) / 5, mode="valid").min())


def voiced_mask(fdb: np.ndarray) -> np.ndarray:
    """Khung nào là tiếng nói. Ngưỡng là 40 dB dưới khung to nhất, nhưng luôn cao hơn nền 8 dB
    để bản thu có nền ồn (tiếng nói chỉ hơn nền 30–40 dB) vẫn tách được khoảng lặng."""
    top = float(fdb.max())
    return fdb >= min(max(top - 40, noise_floor(fdb) + 8), top - 20)


def trim_silence(y: np.ndarray, sr: int, pad: float = 0.08) -> np.ndarray:
    """Cắt khoảng lặng hai đầu, giữ lại `pad` giây để không cắt vào âm đầu, âm cuối."""
    fdb = frame_db(y, sr)
    voiced = np.flatnonzero(voiced_mask(fdb))
    n = max(1, sr * 20 // 1000)
    lo = max(0, voiced[0] * n - int(pad * sr))
    hi = min(len(y), (voiced[-1] + 1) * n + int(pad * sr))
    return y[lo:hi]


def audio_files(paths: list[str]) -> list[Path]:
    """Mở rộng thư mục thành danh sách file audio, giữ nguyên file được nêu thẳng."""
    files: list[Path] = []
    for p in map(Path, paths):
        if p.is_dir():
            files += sorted(f for f in p.iterdir() if f.suffix.lower() in AUDIO_EXT)
        elif p.exists():
            files.append(p)
        else:
            die(f"không thấy {p}")
    return files


# ── API VoiceStudio ──────────────────────────────────────────────────────────

def client() -> httpx.Client:
    c = httpx.Client(base_url=API, timeout=600)
    try:
        c.get("/health").raise_for_status()
    except httpx.HTTPError:
        die(f"VoiceStudio chưa chạy ở {API}. Mở app, hoặc chỉ bật backend: "
            "cd ~/workspace/VoiceStudio && bun run dev:api")
    return c


def api_error(r: httpx.Response) -> str:
    try:
        detail = r.json().get("detail", r.text)
    except ValueError:
        detail = r.text
    if isinstance(detail, dict):
        if detail.get("error") == "asr_model_missing":
            return "chưa có model chép lời, tải Whisper large-v3 (MLX) trong Model Catalogue"
        detail = detail.get("message", detail)
    return f"HTTP {r.status_code}: {str(detail)[:300]}"


def generate(c: httpx.Client, text: str, profile: str, *, engine: str = "omnivoice", steps: int = 32,
             seed: int = 42, cfg: float = 2.0, speed: float = 1.0, bits: int = 16) -> tuple[bytes, dict]:
    """Tạo một đoạn. Tắt chia đoạn của app (max_chunk_chars=0) vì script tự chia."""
    r = c.post("/generate", data={
        "text": text, "language": "Vietnamese", "engine": engine, "profile_id": profile,
        "num_step": steps, "seed": seed, "guidance_scale": cfg, "speed": speed,
        "wav_bits": str(bits), "max_chunk_chars": 0,
    })
    if r.status_code != 200:
        raise RuntimeError(api_error(r))
    return r.content, {"gen_s": float(r.headers.get("x-gen-time") or 0),
                       "audio_s": float(r.headers.get("x-audio-duration") or 0)}


def transcribe(c: httpx.Client, path: Path) -> str:
    with open(path, "rb") as f:
        r = c.post("/v1/audio/transcriptions", files={"file": (path.name, f)},
                   data={"language": "vi", "response_format": "text"})
    if r.status_code != 200:
        raise RuntimeError(api_error(r))
    return r.text.strip()


def profile_audio(c: httpx.Client, profile: str, dest: Path) -> Path:
    """Tải clip mẫu của một profile về `dest`."""
    r = c.get(f"/profiles/{profile}/audio")
    if r.status_code != 200:
        die(f"không lấy được clip mẫu của profile {profile}: {api_error(r)}")
    dest.write_bytes(r.content)
    return dest


# ── So chữ ───────────────────────────────────────────────────────────────────

def spoken(text: str) -> str:
    """Chữ model thật sự đọc: [[a|b]] thành b, [[a]] thành a, bỏ các tag như [pause 500ms]."""
    text = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", text)
    return " ".join(re.sub(r"\[[^\[\]]*\]", " ", text).split())


def words(text: str) -> list[str]:
    """Tách thành âm tiết để so sánh: bỏ tag, dấu câu, chữ hoa; chuẩn NFC. Phiên âm [[a|b]] tính là b."""
    text = unicodedata.normalize("NFC", spoken(text)).lower()
    return re.findall(r"\w+", text)


def compare(expected: str, heard: str) -> dict:
    """So văn bản gốc với lời chép lại. `missing` là các chữ có trong gốc mà không nghe thấy."""
    ref, hyp = words(expected), words(heard)
    missing, extra, changed = [], [], []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ref, hyp, autojunk=False).get_opcodes():
        if op == "delete":
            missing.append(" ".join(ref[i1:i2]))
        elif op == "insert":
            extra.append(" ".join(hyp[j1:j2]))
        elif op == "replace":
            changed.append(f"{' '.join(ref[i1:i2])} → {' '.join(hyp[j1:j2])}")
    errors = sum(len(s.split()) for s in missing + extra) + sum(
        max(len(a.split()), len(b.split())) for a, b in (s.split(" → ") for s in changed))
    return {"missing": missing, "extra": extra, "changed": changed,
            "wer": round(errors / max(len(ref), 1), 3)}


# ── Độ giống giọng ───────────────────────────────────────────────────────────

_extractor = None


def speaker_embedding(path: Path) -> np.ndarray:
    """Vector giọng nói đã chuẩn hóa. Model huấn luyện trên tiếng Anh: chỉ dùng để so tương đối."""
    global _extractor
    import sherpa_onnx

    if _extractor is None:
        if not SPEAKER_MODEL.exists():
            SPEAKER_MODEL.parent.mkdir(exist_ok=True)
            print(f"Tải model đo độ giống giọng (26MB) về {SPEAKER_MODEL} ...", file=sys.stderr)
            urllib.request.urlretrieve(SPEAKER_MODEL_URL, SPEAKER_MODEL)
        _extractor = sherpa_onnx.SpeakerEmbeddingExtractor(
            sherpa_onnx.SpeakerEmbeddingExtractorConfig(model=str(SPEAKER_MODEL), num_threads=2))
    stream = _extractor.create_stream()
    stream.accept_waveform(16000, load_audio(path, 16000))
    stream.input_finished()
    e = np.array(_extractor.compute(stream))
    return e / np.linalg.norm(e)


def similarity(a: np.ndarray, b: np.ndarray) -> float:
    return round(float(a @ b), 3)


def dnsmos(y16: np.ndarray) -> dict:
    """Điểm DNSMOS (1–5): SIG là giọng, BAK là nền, OVRL là tổng thể."""
    from speechmos import dnsmos as _dnsmos

    d = _dnsmos.run(y16 / max(float(np.abs(y16).max()), 1e-9), 16000)
    return {"sig": round(float(d["sig_mos"]), 2), "bak": round(float(d["bak_mos"]), 2),
            "ovrl": round(float(d["ovrl_mos"]), 2)}
