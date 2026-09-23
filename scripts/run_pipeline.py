"""
Запускает весь пайплайн по очереди: озвучка -> картинки -> сборка видео.

Запуск:
    python scripts/run_pipeline.py
"""

import subprocess
import sys

STEPS = [
    ("Озвучка", "scripts/generate_audio.py"),
    ("Картинки", "scripts/generate_images.py"),
    ("Сборка видео", "scripts/assemble_video.py"),
]


def main():
    for name, script in STEPS:
        print(f"\n=== {name} ===")
        result = subprocess.run([sys.executable, script])
        if result.returncode != 0:
            print(f"Шаг '{name}' завершился с ошибкой. Останавливаюсь.")
            sys.exit(1)

    print("\nГотово. Видео лежит в output/final_video.mp4")
    print("Дальше — загружаешь его на YouTube вручную через студию, как обычно.")


if __name__ == "__main__":
    main()
