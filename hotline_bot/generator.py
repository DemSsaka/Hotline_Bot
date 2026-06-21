import re
import requests
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL, CHANNEL_META, CHANNELS

client = Groq(api_key=GROQ_API_KEY)


def fetch_news_topic(channel_key: str) -> str:
    """Получаем свежую тему через веб-поиск DuckDuckGo (бесплатно, без API)."""
    query = CHANNEL_META[channel_key]["search"]
    try:
        url = "https://api.duckduckgo.com/"
        params = {"q": query, "format": "json", "no_html": 1, "skip_disambig": 1}
        r = requests.get(url, params=params, timeout=8)
        data = r.json()
        # Берём AbstractText или первый RelatedTopic
        abstract = data.get("AbstractText", "")
        if abstract:
            return abstract[:500]
        topics = data.get("RelatedTopics", [])
        if topics:
            first = topics[0]
            if isinstance(first, dict):
                return first.get("Text", "")[:500]
    except Exception:
        pass
    return ""  # fallback — Groq сам придумает актуальную тему


def generate_thematic_post(channel_key: str) -> dict:
    """Генерирует пост для тематического канала."""
    meta    = CHANNEL_META[channel_key]
    ch_name = meta["name"]
    style   = meta["style"]
    tags    = meta["tags"]
    main_ch = CHANNELS["main"]

    hint = fetch_news_topic(channel_key)
    hint_block = f"\nКонтекст из новостей (используй как отправную точку):\n{hint}\n" if hint else ""

    prompt = f"""Ты редактор Telegram-канала {ch_name}.
Тематика: {style}
{hint_block}
Придумай ОДНУ свежую, горячую и обсуждаемую новость на эту тему.
Новость должна быть реалистичной, актуальной для {ch_name} в 2026 году.

СТИЛЬ HOTLINE — не СМИ и не блогер:
- Факт + крючок. Читатель должен захотеть дочитать.
- Короткие абзацы по 1-2 строки.
- Последняя строка — вопрос читателю ИЛИ провокационный вывод.
- Без вводных фраз ("сегодня стало известно", "по данным источников").
- Только русский язык.

СТРУКТУРА (строго соблюдай):
1. Хэштеги — 3-4 штуки, каждый с #
2. Пустая строка
3. Заголовок — цепляющий, 1 строка, можно эмодзи
4. Пустая строка
5. Тело — 3-5 коротких абзацев по 1-2 строки каждый
6. Пустая строка
7. Вопрос или вывод — 1 строка
8. Пустая строка
9. Последняя строка: HOTLINE_LINK (это placeholder, не трогай)

Выдай ТОЛЬКО готовый текст поста. Никакого предисловия.
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.85,
        max_tokens=600,
    )

    text = response.choices[0].message.content.strip()
    # Вставляем реальную гиперссылку вместо placeholder
    main_link = f'<a href="https://t.me/{main_ch.lstrip("@")}">HOTLINE</a>'
    text = text.replace("HOTLINE_LINK", main_link)

    # Извлекаем хэштеги для поиска фото
    hashtags = re.findall(r"#(\w+)", text)
    photo_query = " ".join(hashtags[:2]) if hashtags else meta["search"]

    return {
        "text":         text,
        "photo_query":  photo_query,
        "channel_key":  channel_key,
        "parse_mode":   "HTML",
    }


def generate_main_post(channel_key: str) -> dict:
    """Генерирует пост для основного канала со ссылкой на тематический."""
    meta     = CHANNEL_META[channel_key]
    ch_name  = meta["name"]
    ch_link  = CHANNELS[channel_key]
    style    = meta["style"]

    hint = fetch_news_topic(channel_key)
    hint_block = f"\nКонтекст:\n{hint}\n" if hint else ""

    prompt = f"""Ты редактор главного Telegram-канала HOTLINE.
Сейчас пишешь пост про тему: {style}
{hint_block}
Придумай ОДНУ горячую новость из этой темы.

СТИЛЬ HOTLINE:
- Факт + крючок. 
- Короткие абзацы 1-2 строки.
- В конце — отсылка к тематическому каналу.
- Только русский язык.

СТРУКТУРА:
1. Хэштеги 3-4 штуки
2. Пустая строка  
3. Заголовок с эмодзи
4. Пустая строка
5. Тело — 3-4 абзаца
6. Пустая строка
7. Вопрос или вывод
8. Пустая строка
9. Последняя строка: Больше → CHANNEL_LINK {meta['emoji']}

Где CHANNEL_LINK — это placeholder, не трогай.

Выдай ТОЛЬКО готовый текст. Без предисловия.
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.85,
        max_tokens=600,
    )

    text = response.choices[0].message.content.strip()
    ch_link_html = f'<a href="https://t.me/{ch_link.lstrip("@")}">{ch_name}</a>'
    text = text.replace("CHANNEL_LINK", ch_link_html)

    hashtags = re.findall(r"#(\w+)", text)
    photo_query = " ".join(hashtags[:2]) if hashtags else meta["search"]

    return {
        "text":        text,
        "photo_query": photo_query,
        "parse_mode":  "HTML",
    }


def generate_digest(daily_posts: list[dict]) -> dict:
    """Генерирует вечерний дайджест для основного канала."""

    # Формируем краткое описание постов дня
    summaries = []
    for p in daily_posts:
        emoji = CHANNEL_META[p["channel_key"]]["emoji"]
        name  = CHANNEL_META[p["channel_key"]]["name"].replace("HOTLINE | ", "")
        # Берём первую строку с буквами (заголовок)
        lines = [l.strip() for l in p["text"].split("\n") if l.strip() and not l.startswith("#")]
        headline = lines[0] if lines else "—"
        summaries.append(f"{emoji} {name.upper()}: {headline}")

    bullets = "\n".join(summaries) if summaries else "— новости дня"

    prompt = f"""Напиши вечерний дайджест для Telegram-канала HOTLINE.

Сегодняшние темы:
{bullets}

ФОРМАТ (строго):
📡 HOTLINE | ДАЙДЖЕСТ — что шумело сегодня

[перечисли каждую тему одной строкой в формате: эмодзи КАНАЛ: Краткий заголовок]

━━━━━━━━━━━━━━━
📡 Вся сеть каналов → см. описание

Какая тема зацепила тебя больше всего?

Только русский язык. Без предисловия. Только готовый текст."""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        max_tokens=400,
    )

    return {
        "text":       response.choices[0].message.content.strip(),
        "parse_mode": "HTML",
        "is_digest":  True,
    }
