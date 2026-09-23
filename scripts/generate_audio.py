"""
Генерирует озвучку из data/script_segments.json через Edge TTS (бесплатно, без ключа).

Формат script_segments.json:
[
  {"id": "SEG01", "text": "In July two thousand two, a catamaran left..."},
  {"id": "SEG02", "text": "..."}
]

Запуск:
    python scripts/generate_audio.py
"""

import asyncio
import json
import os
import sys

import edge_tts
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_config():
    with open(os.path.join(ROOT, "config.yaml"), "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_segments(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


async def synthesize_segment(text: str, voice: str, rate: str, out_path: str):
    communicate = edge_tts.Communicate(text, voice=voice, rate=rate)
    await communicate.save(out_path)


async def main():
    cfg = load_config()
    audio_cfg = cfg["audio"]

    segments_path = os.path.join(ROOT, cfg["paths"]["script_json"])
    if not os.path.exists(segments_path):
        print(f"Не найден файл сегментов: {segments_path}")
        print("Создай data/script_segments.json по образцу из README.")
        sys.exit(1)

    segments = load_segments(segments_path)

    tmp_dir = os.path.join(ROOT, "output", "audio", "segments")
    os.makedirs(tmp_dir, exist_ok=True)

    segment_files = []
    for seg in segments:
        out_file = os.path.join(tmp_dir, f"{seg['id']}.mp3")
        print(f"[audio] Генерирую {seg['id']}...")
        await synthesize_segment(
            seg["text"], audio_cfg["voice"], audio_cfg["rate"], out_file
        )
        segment_files.append(out_file)

    # Склеиваем сегменты в один файл через ffmpeg (простая конкатенация mp3)
    final_out = os.path.join(ROOT, audio_cfg["output_file"])
    os.makedirs(os.path.dirname(final_out), exist_ok=True)

    concat_list_path = os.path.join(tmp_dir, "concat_list.txt")
    with open(concat_list_path, "w", encoding="utf-8") as f:
        for path in segment_files:
            f.write(f"file '{path}'\n")

    os.system(
        f'ffmpeg -y -f concat -safe 0 -i "{concat_list_path}" '
        f'-c copy "{final_out}"'
    )

    print(f"[audio] Готово: {final_out}")


if __name__ == "__main__":
    asyncio.run(main())
