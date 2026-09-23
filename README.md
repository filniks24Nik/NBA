# AI Video Pipeline — озвучка + картинки + сборка

Полностью бесплатный пайплайн: текст → озвучка (Edge TTS) → картинки (Flux.1-schnell) →
готовый mp4. Загрузка на YouTube — вручную, тобой, через обычный интерфейс.

Работает с любого компьютера: клонируешь репозиторий, ставишь зависимости, запускаешь.

## Установка (один раз на каждом ПК)

1. Установи Python 3.10+ и [ffmpeg](https://ffmpeg.org/download.html)
   (Windows: скачать и добавить в PATH; Mac: `brew install ffmpeg`; Linux: `apt install ffmpeg`)

2. Клонируй репозиторий:
   ```
   git clone <ссылка-на-твой-репозиторий>
   cd <папка-репозитория>
   ```

3. Установи зависимости:
   ```
   pip install -r requirements.txt
   ```

4. Скопируй `.env.example` в `.env` и впиши свой бесплатный токен:
   - Для Hugging Face (по умолчанию): https://huggingface.co/settings/tokens
   - Или для fal.ai (альтернатива): https://fal.ai — есть бесплатные кредиты при регистрации

## Подготовка данных

1. Открой `data/script_segments.json` и замени примерный текст на свою озвучку,
   разбитую на сегменты — так же, как это делалось на этапе ElevenLabs.

2. Открой `data/frames.csv` и вставь свою таблицу кадров с промтами
   (та самая таблица `#,TC_IN,VO_CHUNK,FAM,REG,NANO_BANANA_2_PROMPT`).
   Проще всего — экспортировать её как CSV и просто заменить файл целиком.

3. При желании поменяй настройки в `config.yaml`:
   - голос озвучки (`audio.voice`) — список голосов Edge TTS: `edge-tts --list-voices`
   - длительность кадра (`video.frame_duration_sec`)
   - провайдера картинок (`images.provider`: huggingface или fal)

## Запуск

Всё сразу:
```
python scripts/run_pipeline.py
```

Или по шагам (удобно, если что-то упало и хочешь перезапустить только один этап):
```
python scripts/generate_audio.py
python scripts/generate_images.py
python scripts/assemble_video.py
```

Готовое видео появится в `output/final_video.mp4`.

Если генерация картинок оборвалась на середине — просто запусти `generate_images.py`
ещё раз, уже готовые файлы он не будет перегенерировать.

## Загрузка на YouTube

Скрипт видео не загружает — по твоей просьбе это делается вручную.
При загрузке через YouTube Studio не забудь:
- отметить видео как содержащее AI/synthetic content (поле "Altered content" / "AI Use"
  в деталях видео) — это сейчас обязательно для контента с синтетическим голосом
  и реалистичными AI-изображениями, изображающими реальных людей и события;
- если сюжет строится на непроверенных данных — указать это в описании.

## Структура проекта

```
.
├── config.yaml              настройки пайплайна
├── requirements.txt
├── .env.example              шаблон для ключей API
├── data/
│   ├── script_segments.json  текст озвучки по сегментам
│   └── frames.csv             таблица кадров с промтами
├── scripts/
│   ├── generate_audio.py
│   ├── generate_images.py
│   ├── assemble_video.py
│   └── run_pipeline.py
└── output/                    сюда пишутся результаты (в git не попадает)
```

## Смена провайдера картинок

По умолчанию используется Hugging Face Inference API (бесплатно, но с лимитами
по скорости — генерация 360 кадров может занять время). Если нужно быстрее —
переключи `images.provider` на `fal` в `config.yaml` и впиши `FAL_KEY` в `.env`.
fal.ai даёт бесплатные кредиты при регистрации, дальше — по факту использования.
