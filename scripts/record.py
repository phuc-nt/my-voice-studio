#!/usr/bin/env python3
"""Buổi thu clip mẫu: hiện từng câu trong kịch bản, thu, cắt khoảng lặng, lưu đúng tên và đo ngay.

Câu lấy từ docs/recording-script-vietnamese.md. File lưu vào recordings/<phong-cach>-<so-cau>-take<lan>.wav.

Dùng:
  uv run scripts/record.py --devices                 # liệt kê mic
  uv run scripts/record.py --test                    # thu thử để chỉnh gain và đo nền phòng
  uv run scripts/record.py                           # thu câu 1–5 (trò chuyện, kể chuyện), mỗi câu 3 take
  uv run scripts/record.py --sentences 6-7 --takes 2
  uv run scripts/record.py --list                    # in kịch bản

Thu bằng iPhone (Voice Memos, Lossless) rồi tách thành các take:
  uv run scripts/record.py --from-file cau-1.m4a --sentences 1        # mọi lần đọc trong file là take của câu 1
  uv run scripts/record.py --from-file buoi-thu.m4a --sentences 1-5   # đọc theo thứ tự, mỗi câu đúng 3 lần
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import textwrap
import threading
from pathlib import Path

import numpy as np
import soundfile as sf

import vslib

SR = 48000
REC = vslib.ROOT / "recordings"
SCRIPT = vslib.ROOT / "docs" / "recording-script-vietnamese.md"
SLUGS = {"A": "tro-chuyen", "B": "ke-chuyen", "C": "doc-tin", "D": "nang-dong", "E": "cam-xuc", "F": "nhe-nhang"}
EDGE = 0.3  # bỏ 0,3 giây đầu và cuối bản thu trực tiếp để loại tiếng gõ phím Enter


def check_clip():
    spec = importlib.util.spec_from_file_location("check_clip", Path(__file__).with_name("check-clip.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_sentences() -> list[dict]:
    """Đọc các câu đánh số dưới từng tiêu đề "## Nhóm X." của kịch bản ghi âm."""
    out, group, hint = [], None, ""
    for line in SCRIPT.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("## "):
            m = re.match(r"## Nhóm ([A-F])\. (.+)", line)
            group, hint = ((m.group(1), m.group(2)), "") if m else (None, "")
        elif group and (m := re.match(r"(\d+)\. (.+)", line)):
            out.append({"n": int(m.group(1)), "slug": SLUGS[group[0]], "group": group[1],
                        "hint": hint, "text": m.group(2)})
        elif group and line and not hint:
            hint = line
    if not out:
        vslib.die(f"không đọc được câu nào từ {SCRIPT}")
    return out


def select(sentences: list[dict], spec: str) -> list[dict]:
    want: set[int] = set()
    for part in spec.split(","):
        lo, _, hi = part.partition("-")
        try:
            want.update(range(int(lo), int(hi or lo) + 1))
        except ValueError:
            vslib.die(f"--sentences không hợp lệ: {spec} (ví dụ đúng: 1-5 hoặc 1,4,12)")
    sel = [s for s in sentences if s["n"] in want]
    if not sel:
        vslib.die(f"kịch bản không có câu {spec}")
    return sel


def takes_of(s: dict) -> list[Path]:
    return sorted(REC.glob(f"{s['slug']}-{s['n']:02d}-take*.wav"))


def save_take(y: np.ndarray, sr: int, s: dict) -> Path:
    """Cắt khoảng lặng hai đầu rồi lưu thành take kế tiếp của câu, không ghi đè file cũ."""
    REC.mkdir(parents=True, exist_ok=True)
    k = 1
    while (path := REC / f"{s['slug']}-{s['n']:02d}-take{k}.wav").exists():
        k += 1
    sf.write(path, vslib.trim_silence(y, sr), sr, subtype="PCM_24")
    return path


def report(cc, path: Path) -> None:
    m = cc.measure(path)
    print(f"  {m['verdict']}  {path}  {m['duration']:.1f}s  đỉnh {m['peak_db']} dBFS"
          f"  nền {m['noise_db']} dBFS  DNSMOS tổng {m['ovrl']}")
    for i in m["issues"]:
        print(f"    - {i}")


def show(s: dict, pos: int, total: int) -> None:
    print(f"\n{'─' * 72}\nCâu {s['n']} ({pos}/{total}) · {s['group']} · đã có {len(takes_of(s))} take")
    print(f"  {s['hint']}\n")
    print(textwrap.fill(s["text"], 68, initial_indent="    ", subsequent_indent="    "), "\n")


# ── Thu trực tiếp ────────────────────────────────────────────────────────────

def open_device(device):
    """Trả về (thiết bị, tần số mẫu). Dùng 48 kHz nếu mic hỗ trợ, nếu không thì tần số mặc định của mic."""
    import sounddevice as sd

    if device is None and sd.default.device[0] < 0:
        vslib.die("máy không có mic nào. Mac mini không có mic tích hợp: cắm mic USB hoặc tai nghe có mic, "
                  "hoặc thu bằng iPhone rồi dùng --from-file")
    try:
        info = sd.query_devices(device, "input")
    except (ValueError, sd.PortAudioError) as e:
        vslib.die(f"không mở được mic {device}: {e}. Xem danh sách: uv run scripts/record.py --devices")
    try:
        sd.check_input_settings(device=device, samplerate=SR, channels=1)
        sr = SR
    except sd.PortAudioError:
        sr = int(info["default_samplerate"])
        print(f"Lưu ý: mic không thu được ở 48 kHz, dùng {sr} Hz.")
    print(f"Mic: {info['name']} · {sr} Hz mono")
    return device, sr


def capture(device, sr: int) -> np.ndarray:
    """Thu cho đến khi bấm Enter, hiện mức tín hiệu trong lúc thu."""
    import sounddevice as sd

    chunks: list[np.ndarray] = []
    level = [0.0, 0.0]  # mức hiện tại, đỉnh của cả take

    def on_audio(indata, frames, time, status):
        chunks.append(indata[:, 0].copy())
        level[0] = float(np.abs(indata).max())
        level[1] = max(level[1], level[0])

    stop = threading.Event()

    def meter():
        while not stop.wait(0.1):
            cur, peak = vslib.db(level[0]), vslib.db(level[1])
            bar = "█" * int(max(0.0, min(1.0, (cur + 60) / 60)) * 30)
            print(f"\r  ● đang thu  {bar:<30} {cur:6.1f} dBFS  đỉnh {peak:6.1f}  (Enter để dừng) ", end="", flush=True)

    with sd.InputStream(samplerate=sr, channels=1, dtype="float32", device=device, callback=on_audio):
        t = threading.Thread(target=meter, daemon=True)
        t.start()
        input()
        stop.set()
        t.join()
    y = np.concatenate(chunks) if chunks else np.zeros(0, np.float32)
    cut = int(EDGE * sr)
    return y[cut:-cut] if len(y) > 3 * cut else y[:0]


def silent(y: np.ndarray) -> bool:
    if len(y) and vslib.db(float(np.abs(y).max())) > -70:
        return False
    print("  Không thu được tín hiệu. Kiểm tra mic đã chọn đúng chưa, và cấp quyền Microphone cho ứng dụng "
          "terminal trong System Settings → Privacy & Security → Microphone.")
    return True


def level_test(device, sr: int) -> None:
    print("\nThu thử: bấm Enter, im lặng 3 giây, đọc một câu với giọng bình thường, rồi bấm Enter.")
    input("Enter để bắt đầu > ")
    y = capture(device, sr)
    if silent(y):
        return
    fdb = vslib.frame_db(y, sr)
    peak = vslib.db(float(np.abs(y).max()))
    noise = vslib.noise_floor(fdb)
    print(f"\n  Đỉnh {peak:.1f} dBFS (mục tiêu −12 đến −6) · nền phòng {noise:.1f} dBFS (ước lượng, nên dưới −50)")
    if peak > -3:
        print("  - Quá to: giảm Input volume trong System Settings → Sound → Input, hoặc lùi xa mic.")
    elif peak > -6:
        print("  - Hơi to: giảm gain một chút.")
    elif peak < -20:
        print("  - Quá nhỏ: tăng Input volume hoặc lại gần mic hơn (10–15 cm).")
    elif peak < -12:
        print("  - Hơi nhỏ: tăng gain một chút.")
    if noise > -50:
        print("  - Nền ồn: tắt quạt, máy lạnh, đóng cửa. Nếu bạn không im lặng lúc đầu thì thu thử lại.")
    if -12 <= peak <= -6 and noise <= -50:
        print("  Mức ổn. Giữ nguyên gain và khoảng cách cho cả buổi.")


def live(sel: list[dict], takes: int, device, sr: int) -> None:
    cc = check_clip()
    print("\nBấm Enter, chờ một nhịp rồi đọc. Đọc xong chờ một nhịp rồi bấm Enter.")
    for pos, s in enumerate(sel, 1):
        if len(takes_of(s)) >= takes:
            print(f"\nCâu {s['n']} đã đủ {takes} take, bỏ qua. Muốn thu thêm thì tăng --takes.")
            continue
        while len(takes_of(s)) < takes:
            show(s, pos, len(sel))
            cmd = input("Enter: thu · n: câu tiếp · q: thoát > ").strip().lower()
            if cmd == "q":
                return
            if cmd == "n":
                break
            y = capture(device, sr)
            print()
            if silent(y):
                continue
            path = save_take(y, sr, s)
            report(cc, path)
            if input("Enter: giữ · x: xóa take này (đọc vấp, có tiếng động) > ").strip().lower() == "x":
                path.unlink()
                print("  Đã xóa.")


# ── Tách từ bản thu có sẵn ───────────────────────────────────────────────────

def split_takes(y: np.ndarray, sr: int, gap: float) -> list[tuple[float, float]]:
    """Các quãng có tiếng nói, cách nhau bằng khoảng lặng dài hơn `gap` giây. Bỏ quãng ngắn hơn 1 giây.

    Tiếng ngắn hơn 0,3 giây (hít hơi, tiếng chạm) không tính là tiếng nói, để nó không chia đôi khoảng lặng."""
    mask = vslib.voiced_mask(vslib.frame_db(y, sr))
    edges = np.flatnonzero(np.diff(np.concatenate(([0], mask.astype(np.int8), [0]))))
    for a, b in zip(edges[::2], edges[1::2]):
        if (b - a) * 0.02 < 0.3:
            mask[a:b] = False
    voiced = np.flatnonzero(mask)
    segs, start, last = [], None, None
    for i in voiced:
        if start is None:
            start = i
        elif (i - last) * 0.02 > gap:
            segs.append((start, last))
            start = i
        last = i
    if start is not None:
        segs.append((start, last))
    return [(a * 0.02, (b + 1) * 0.02) for a, b in segs if (b + 1 - a) * 0.02 >= 1.0]


def from_file(src: Path, sel: list[dict], takes: int, gap: float) -> None:
    if not src.exists():
        vslib.die(f"không thấy {src}")
    y = vslib.load_audio(src, SR)
    segs = split_takes(y, SR, gap)
    want = len(sel) * takes
    if len(sel) > 1 and len(segs) != want:
        print(f"Tìm thấy {len(segs)} lần đọc, cần {want} ({len(sel)} câu × {takes} take):")
        for i, (a, b) in enumerate(segs, 1):
            print(f"  {i:2}. {a:7.1f}s → {b:7.1f}s  ({b - a:.1f}s)")
        vslib.die("số lần đọc không khớp nên không biết lần nào là câu nào. Cắt tay từng lần bằng "
                  "prep-clip.py --start/--end theo bảng trên, hoặc thu mỗi câu một file rồi chạy với --sentences <số câu>")
    if not segs:
        vslib.die("không thấy lần đọc nào trong file")
    cc = check_clip()
    for i, (a, b) in enumerate(segs):
        s = sel[0] if len(sel) == 1 else sel[i // takes]
        pad = int(0.2 * SR)
        path = save_take(y[max(0, int(a * SR) - pad): int(b * SR) + pad], SR, s)
        print(f"\nCâu {s['n']} · {a:.1f}s → {b:.1f}s trong bản gốc")
        report(cc, path)


def main() -> None:
    global REC
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sentences", default="1-5", help="câu cần thu, ví dụ 1-5 hoặc 1,4,12 (mặc định 1-5)")
    ap.add_argument("--takes", type=int, default=3, help="số take mỗi câu (mặc định 3)")
    ap.add_argument("--device", help="tên hoặc số thứ tự mic (xem --devices)")
    ap.add_argument("--devices", action="store_true", help="liệt kê thiết bị âm thanh rồi thoát")
    ap.add_argument("--list", action="store_true", help="in kịch bản rồi thoát")
    ap.add_argument("--test", action="store_true", help="thu thử để chỉnh gain và đo nền phòng, không lưu file")
    ap.add_argument("--from-file", type=Path, help="tách các lần đọc từ một bản thu có sẵn thay vì thu trực tiếp")
    ap.add_argument("--out", type=Path, default=REC, help="thư mục lưu (mặc định recordings/)")
    ap.add_argument("--gap", type=float, default=1.5, help="với --from-file: khoảng lặng tối thiểu giữa hai lần đọc (giây)")
    a = ap.parse_args()

    if a.devices:
        import sounddevice as sd
        print(sd.query_devices())
        return
    sentences = load_sentences()
    if a.list:
        for s in sentences:
            print(f"{s['n']:2}. [{s['slug']}] {s['text']}")
        return
    sel = select(sentences, a.sentences)
    REC = a.out.resolve()

    if a.from_file:
        from_file(a.from_file, sel, a.takes, a.gap)
    else:
        device = int(a.device) if a.device and a.device.isdigit() else a.device
        device, sr = open_device(device)
        if a.test:
            level_test(device, sr)
            return
        live(sel, a.takes, device, sr)

    print(f"\nXong. Xếp hạng các take: uv run scripts/check-clip.py {a.out}")
    print("Nghe lại từng take bằng tai nghe trước khi chọn. Số đo không thay được tai bạn.")


if __name__ == "__main__":
    main()
