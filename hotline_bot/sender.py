import os
import logging
import asyncio
from io import BytesIO
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError
from config import BOT_TOKEN, CHANNELS, DIGEST_PHOTO_PATH
from photo import get_photo_url, download_photo

logger = logging.getLogger(__name__)


async def send_post(channel_key: str, post: dict, is_main: bool = False) -> bool:
    """
    Отправляет пост в нужный канал.
    channel_key: ключ из CHANNELS ('auto', 'main', и т.д.)
    post: dict с полями text, photo_query, parse_mode
    is_main: если True — шлём в main канал
    """
    bot = Bot(token=BOT_TOKEN)
    target = CHANNELS["main"] if is_main else CHANNELS[channel_key]

    text = post.get("text", "")
    is_digest = post.get("is_digest", False)

    # ─── Дайджест — фото загружаем своё ───────────────────
    if is_digest:
        photo_bytes = _load_digest_photo()
        if photo_bytes:
            return await _send_with_bytes(bot, target, text, photo_bytes, post.get("parse_mode", "HTML"))
        else:
            return await _send_text(bot, target, text, post.get("parse_mode", "HTML"))

    # ─── Обычный пост — ищем фото по запросу ──────────────
    photo_url   = get_photo_url(post.get("photo_query", "news"))
    photo_bytes = download_photo(photo_url)

    if photo_bytes:
        return await _send_with_bytes(bot, target, text, photo_bytes, post.get("parse_mode", "HTML"))
    else:
        # Если фото не загрузилось — шлём без него
        return await _send_text(bot, target, text, post.get("parse_mode", "HTML"))


async def _send_with_bytes(bot: Bot, chat_id: str, caption: str, photo_bytes: bytes, parse_mode: str) -> bool:
    """Отправляет фото с подписью."""
    try:
        # Telegram ограничивает caption до 1024 символов
        if len(caption) > 1024:
            caption = caption[:1020] + "..."
        await bot.send_photo(
            chat_id=chat_id,
            photo=BytesIO(photo_bytes),
            caption=caption,
            parse_mode=parse_mode,
        )
        logger.info(f"✅ Фото-пост отправлен в {chat_id}")
        return True
    except TelegramError as e:
        logger.error(f"❌ Ошибка отправки фото в {chat_id}: {e}")
        # Пробуем без фото
        return await _send_text(bot, chat_id, caption, parse_mode)


async def _send_text(bot: Bot, chat_id: str, text: str, parse_mode: str) -> bool:
    """Отправляет текстовый пост."""
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode,
            disable_web_page_preview=False,
        )
        logger.info(f"✅ Текст-пост отправлен в {chat_id}")
        return True
    except TelegramError as e:
        logger.error(f"❌ Ошибка отправки текста в {chat_id}: {e}")
        return False


def _load_digest_photo() -> bytes | None:
    """Загружает фото дайджеста из локального файла."""
    if os.path.exists(DIGEST_PHOTO_PATH):
        try:
            with open(DIGEST_PHOTO_PATH, "rb") as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Не могу прочитать дайджест-фото: {e}")
    return None
