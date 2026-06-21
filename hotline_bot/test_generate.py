"""
Тест: генерирует один пост для каждого канала и выводит в консоль.
НЕ отправляет в Telegram. Используй перед запуском бота.

Запуск: python test_generate.py
"""

import sys
from generator import generate_thematic_post, generate_main_post, generate_digest
from config import CHANNEL_ORDER, CHANNEL_META


def test_all():
    print("=" * 60)
    print("HOTLINE BOT — ТЕСТ ГЕНЕРАЦИИ")
    print("=" * 60)

    posts = []

    for ch_key in CHANNEL_ORDER:
        print(f"\n{'─' * 50}")
        print(f"📌 ТЕМАТИЧЕСКИЙ КАНАЛ: {CHANNEL_META[ch_key]['name']}")
        print(f"{'─' * 50}")
        try:
            post = generate_thematic_post(ch_key)
            print(post["text"])
            print(f"\n📷 Запрос для фото: {post['photo_query']}")
            posts.append(post)
        except Exception as e:
            print(f"❌ Ошибка: {e}")

    print(f"\n{'─' * 50}")
    print("📌 ОСНОВНОЙ КАНАЛ (пример)")
    print(f"{'─' * 50}")
    try:
        main_post = generate_main_post("tech")
        print(main_post["text"])
    except Exception as e:
        print(f"❌ Ошибка: {e}")

    print(f"\n{'─' * 50}")
    print("📌 ДАЙДЖЕСТ (20:00)")
    print(f"{'─' * 50}")
    try:
        digest = generate_digest(posts)
        print(digest["text"])
    except Exception as e:
        print(f"❌ Ошибка: {e}")

    print("\n" + "=" * 60)
    print("✅ ТЕСТ ЗАВЕРШЁН")
    print("=" * 60)


if __name__ == "__main__":
    test_all()
