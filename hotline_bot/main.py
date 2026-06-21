"""
HOTLINE Bot — автоматический постинг в сеть Telegram-каналов.

Логика:
- Каждые 2 часа — пост в один из тематических каналов (по очереди)
- Каждые 2 часа (в промежутках) — пост в основной канал на ту же тему
- В 20:00 — дайджест дня в основной канал
"""

import asyncio
import logging
import random
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import CHANNELS, CHANNEL_META, DIGEST_HOUR
from generator import generate_thematic_post, generate_main_post, generate_digest
from sender import send_post

# ─── Логирование ──────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("hotline_bot.log", encoding="utf-8"),
    ]
)
logger = logging.getLogger(__name__)

# ─── Порядок тематических каналов ─────────────────────────
CHANNEL_ORDER = ["auto", "stream", "tiktok", "politics", "tech", "gaming"]
_channel_index = 0          # какой канал сейчас на очереди
_daily_posts: list[dict] = []  # копим посты для дайджеста


def _next_channel() -> str:
    """Возвращает следующий тематический канал по кругу."""
    global _channel_index
    ch = CHANNEL_ORDER[_channel_index % len(CHANNEL_ORDER)]
    _channel_index += 1
    return ch


# ─── Задачи ───────────────────────────────────────────────

async def job_thematic():
    """Публикация в тематический канал."""
    ch_key = _next_channel()
    logger.info(f"▶ Генерирую пост для тематического канала: {ch_key}")
    try:
        post = generate_thematic_post(ch_key)
        ok   = await send_post(ch_key, post, is_main=False)
        if ok:
            _daily_posts.append(post)
        logger.info(f"{'✅' if ok else '❌'} Тематический пост [{ch_key}]")
    except Exception as e:
        logger.error(f"Ошибка в job_thematic ({ch_key}): {e}")


async def job_main():
    """Публикация в основной канал (на случайную тему из тематических)."""
    ch_key = random.choice(CHANNEL_ORDER)
    logger.info(f"▶ Генерирую пост для основного канала (тема: {ch_key})")
    try:
        post = generate_main_post(ch_key)
        ok   = await send_post(ch_key, post, is_main=True)
        logger.info(f"{'✅' if ok else '❌'} Основной пост (тема: {ch_key})")
    except Exception as e:
        logger.error(f"Ошибка в job_main: {e}")


async def job_digest():
    """Публикация вечернего дайджеста в основной канал."""
    logger.info("▶ Генерирую дайджест дня")
    try:
        posts_to_use = _daily_posts.copy()
        if not posts_to_use:
            # Если постов не накопилось — берём рандомные темы
            posts_to_use = [{"channel_key": k, "text": CHANNEL_META[k]["name"]} for k in CHANNEL_ORDER]

        digest = generate_digest(posts_to_use)
        ok     = await send_post("main", digest, is_main=True)
        logger.info(f"{'✅' if ok else '❌'} Дайджест отправлен")

        # Сбрасываем накопленные посты после дайджеста
        _daily_posts.clear()
    except Exception as e:
        logger.error(f"Ошибка в job_digest: {e}")


# ─── Тест при запуске ─────────────────────────────────────

async def test_run():
    """Запускаем один тестовый пост перед стартом планировщика."""
    logger.info("🧪 Тестовый запуск — проверяем генерацию и отправку...")
    try:
        post = generate_thematic_post("tech")
        logger.info(f"Сгенерированный пост:\n{post['text'][:300]}...")
        logger.info("✅ Генерация работает. Пропускаем реальную отправку при тесте.")
    except Exception as e:
        logger.error(f"Тест провалился: {e}")


# ─── Планировщик ──────────────────────────────────────────

async def main():
    logger.info("🚀 HOTLINE Bot запускается...")
    await test_run()

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

    # Тематические каналы — каждые 2 часа начиная с 8:00
    for hour in [8, 10, 12, 14, 16, 18, 22]:
        scheduler.add_job(
            job_thematic,
            CronTrigger(hour=hour, minute=0),
            id=f"thematic_{hour}",
        )

    # Основной канал — каждые 2 часа в нечётные часы
    for hour in [9, 11, 13, 15, 17, 21]:
        scheduler.add_job(
            job_main,
            CronTrigger(hour=hour, minute=0),
            id=f"main_{hour}",
        )

    # Дайджест в 20:00
    scheduler.add_job(
        job_digest,
        CronTrigger(hour=DIGEST_HOUR, minute=0),
        id="digest_20",
    )

    scheduler.start()

    logger.info("✅ Планировщик запущен. Расписание:")
    logger.info("   Тематические каналы: 8, 10, 12, 14, 16, 18, 22")
    logger.info("   Основной канал: 9, 11, 13, 15, 17, 21")
    logger.info(f"   Дайджест: {DIGEST_HOUR}:00")

    # Держим бота живым
    try:
        while True:
            await asyncio.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("👋 Бот остановлен.")
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
