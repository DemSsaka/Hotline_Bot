import requests
import random
from config import UNSPLASH_KEY


FALLBACK_PHOTOS = {
    "авто":        "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=800",
    "стриминг":    "https://images.unsplash.com/photo-1593305841991-05c297ba4575?w=800",
    "tiktok":      "https://images.unsplash.com/photo-1611162616475-46b635cb6868?w=800",
    "политика":    "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=800",
    "технологии":  "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800",
    "игры":        "https://images.unsplash.com/photo-1593305841991-05c297ba4575?w=800",
    "default":     "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800",
}


def get_photo_url(query: str) -> str:
    """Ищет фото на Unsplash по запросу. Возвращает URL."""
    if not UNSPLASH_KEY or UNSPLASH_KEY == "your_unsplash_key_here":
        return _fallback(query)

    try:
        url = "https://api.unsplash.com/photos/random"
        params = {
            "query":       query,
            "orientation": "landscape",
            "content_filter": "high",
        }
        headers = {"Authorization": f"Client-ID {UNSPLASH_KEY}"}
        r = requests.get(url, params=params, headers=headers, timeout=8)
        if r.status_code == 200:
            data = r.json()
            return data["urls"]["regular"]
    except Exception:
        pass

    return _fallback(query)


def _fallback(query: str) -> str:
    """Выбираем fallback фото по ключевым словам."""
    q = query.lower()
    for key, url in FALLBACK_PHOTOS.items():
        if key in q:
            return url
    return FALLBACK_PHOTOS["default"]


def download_photo(url: str) -> bytes | None:
    """Скачивает фото и возвращает bytes."""
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            return r.content
    except Exception:
        pass
    return None
