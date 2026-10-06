#!/usr/bin/env bash
# So sánh cùng một câu tiếng Việt qua nhiều engine và số bước (num_step) với seed cố định,
# gọi API của VoiceStudio đang chạy trên máy. Kết quả lưu vào outputs/ (không vào Git).
#
# Dùng:
#   scripts/ab-test.sh <profile_id> "<câu tiếng Việt>" [engines] [steps] [seed]
# Ví dụ:
#   scripts/ab-test.sh demo0001 "Xin chào, đây là giọng của tôi." "omnivoice voxcpm2" "16 32" 42
#   TRANSCRIBE=1 scripts/ab-test.sh demo0001 "Xin chào."   # chép lời lại để soát từ bị nuốt
#
# Xem danh sách profile:  curl -s http://127.0.0.1:3900/profiles
set -euo pipefail

api="${VOICESTUDIO_API:-http://127.0.0.1:3900}"
profile="${1:?Thiếu profile_id (xem: curl -s $api/profiles)}"
text="${2:?Thiếu câu cần đọc}"
engines="${3:-omnivoice}"
steps="${4:-16 32}"
seed="${5:-42}"

curl -sf "$api/health" >/dev/null || { echo "VoiceStudio chưa chạy ở $api (mở app: cd ~/workspace/VoiceStudio && bun run dev)"; exit 1; }

out="$(cd "$(dirname "$0")/.." && pwd)/outputs/ab-$(date +%y%m%d-%H%M%S)"
mkdir -p "$out"
printf '%s\n' "$text" > "$out/text.txt"
printf 'engine\tsteps\tseed\tgen_s\taudio_s\tfile\n' > "$out/results.tsv"

header() { tr -d '\r' < "$1" | awk -F': ' -v k="$2" 'tolower($1)==k {print $2}'; }

for engine in $engines; do
  for n in $steps; do
    wav="$out/${engine}-steps${n}-seed${seed}.wav"
    hdr="$out/.headers"
    code=$(curl -sS -o "$wav" -D "$hdr" -w '%{http_code}' -X POST "$api/generate" \
      -F "text=$text" -F "language=Vietnamese" -F "engine=$engine" \
      -F "num_step=$n" -F "seed=$seed" -F "profile_id=$profile")
    if [ "$code" != "200" ]; then
      echo "$engine steps=$n: lỗi HTTP $code: $(head -c 300 "$wav")"
      rm -f "$wav"
      continue
    fi
    gen=$(header "$hdr" x-gen-time); dur=$(header "$hdr" x-audio-duration)
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$engine" "$n" "$seed" "$gen" "$dur" "$(basename "$wav")" >> "$out/results.tsv"
    echo "$engine steps=$n: tạo ${gen}s cho ${dur}s âm thanh"
    if [ "${TRANSCRIBE:-0}" = "1" ]; then
      txt="${wav%.wav}.txt"
      code=$(curl -sS -o "$txt" -w '%{http_code}' -X POST "$api/v1/audio/transcriptions" \
        -F "file=@$wav" -F "language=vi" -F "response_format=text")
      if [ "$code" = "200" ]; then
        echo "  nghe được: $(cat "$txt")"
      else
        echo "  chưa chép lời được (HTTP $code). Cần tải Whisper large-v3 (MLX) trong Model Catalogue."
        rm -f "$txt"
      fi
    fi
  done
done
rm -f "$out/.headers"
echo "Đã lưu vào $out"
