"""
Генерирует картинки из data/frames.csv через Flux.1-schnell (бесплатно).

Ожидаемые колонки в frames.csv (как в таблице из чата):
    #,TC_IN,VO_CHUNK,FAM,REG,NANO_BANANA_2_PROMPT

Провайдер настраивается в config.yaml -> images.provider:
    "huggingface" — нужен HUGGINGFACE_TOKEN в .env (бесплатный токен)
    "fal"         — нужен FAL_KEY в .env (бесплатные кредиты при регистрации)

Запуск:
    python scripts/generate_images.py
"""

import os
import sys

import pandas as pd
import yaml
from dotenv import load_dotenv
from tqdm import tqdm

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT, ".env"))


def load_config():
    with open(os.path.join(ROOT, "config.yaml"), "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def generate_huggingface(prompt: str, model: str, out_path: str):
    from huggingface_hub import InferenceClient

    token = os.environ.get("HUGGINGFACE_TOKEN")
    if not token:
        print("Не задан HUGGINGFACE_TOKEN в .env")
        sys.exit(1)

    client = InferenceClient(model=model, token=token)
    image = client.text_to_image(prompt)
    image.save(out_path)


def generate_fal(prompt: str, model: str, out_path: str):
    import fal_client
    import requests

    key = os.environ.get("FAL_KEY")
    if not key:
        print("Не задан FAL_KEY в .env")
        sys.exit(1)

    result = fal_client.subscribe(
        model,
        arguments={"prompt": prompt, "image_size": "landscape_16_9"},
    )
    image_url = result["images"][0]["url"]
    img_data = requests.get(image_url).content
    with open(out_path, "wb") as f:
        f.write(img_data)


def main():
    cfg = load_config()
    img_cfg = cfg["images"]

    frames_path = os.path.join(ROOT, cfg["paths"]["frames_csv"])
    if not os.path.exists(frames_path):
        print(f"Не найден файл кадров: {frames_path}")
        print("Положи туда CSV с колонками #,TC_IN,VO_CHUNK,FAM,REG,NANO_BANANA_2_PROMPT")
        sys.exit(1)

    df = pd.read_csv(frames_path)
    out_dir = os.path.join(ROOT, img_cfg["output_dir"])
    os.makedirs(out_dir, exist_ok=True)

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Генерация кадров"):
        frame_num = int(row["#"])
        out_path = os.path.join(out_dir, f"{frame_num:04d}.png")

        if os.path.exists(out_path):
            continue  # уже сгенерирован — пропускаем (можно докачивать после сбоя)

        prompt = row["NANO_BANANA_2_PROMPT"]

        if img_cfg["provider"] == "huggingface":
            generate_huggingface(prompt, img_cfg["huggingface_model"], out_path)
        elif img_cfg["provider"] == "fal":
            generate_fal(prompt, img_cfg["fal_model"], out_path)
        else:
            print(f"Неизвестный провайдер: {img_cfg['provider']}")
            sys.exit(1)

    print(f"[images] Готово: {out_dir}")


if __name__ == "__main__":
    main()
