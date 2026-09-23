"""
Собирает финальное видео из картинок (output/images/) и озвучки (output/audio/narration.mp3)
через ffmpeg. Каждый кадр показывается frame_duration_sec секунд, порядок — по номеру файла.

Требует установленный ffmpeg в системе (ffmpeg.org или `brew install ffmpeg` / `apt install ffmpeg`).

Запуск:
    python scripts/assemble_video.py
"""

import glob
import os
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_config():
    with open(os.path.join(ROOT, "config.yaml"), "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    cfg = load_config()
    video_cfg = cfg["video"]
    img_dir = os.path.join(ROOT, cfg["images"]["output_dir"])
    audio_path = os.path.join(ROOT, cfg["audio"]["output_file"])
    out_path = os.path.join(ROOT, video_cfg["output_file"])

    images = sorted(glob.glob(os.path.join(img_dir, "*.png")))
    if not images:
        print(f"Не найдены картинки в {img_dir}. Сначала запусти generate_images.py")
        sys.exit(1)

    if not os.path.exists(audio_path):
        print(f"Не найдена озвучка {audio_path}. Сначала запусти generate_audio.py")
        sys.exit(1)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    # Формируем concat-файл для ffmpeg
    concat_path = os.path.join(ROOT, "output", "concat_list.txt")
    duration = video_cfg["frame_duration_sec"]

    with open(concat_path, "w", encoding="utf-8") as f:
        for img in images:
            f.write(f"file '{img}'\n")
            f.write(f"duration {duration}\n")
        # ffmpeg concat-demuxer требует повторить последний файл без duration
        f.write(f"file '{images[-1]}'\n")

    silent_video = os.path.join(ROOT, "output", "video_no_audio.mp4")

    cmd_video = (
        f'ffmpeg -y -f concat -safe 0 -i "{concat_path}" '
        f'-vsync vfr -pix_fmt yuv420p '
        f'-s {video_cfg["width"]}x{video_cfg["height"]} '
        f'-r {video_cfg["fps"]} "{silent_video}"'
    )
    print("[video] Собираю видеоряд...")
    os.system(cmd_video)

    cmd_merge = (
        f'ffmpeg -y -i "{silent_video}" -i "{audio_path}" '
        f'-c:v copy -c:a aac -shortest "{out_path}"'
    )
    print("[video] Добавляю звук...")
    os.system(cmd_merge)

    print(f"[video] Готово: {out_path}")


if __name__ == "__main__":
    main()
