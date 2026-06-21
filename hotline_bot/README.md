# 🔥 HOTLINE Bot

Автоматический бот для публикации новостей в сеть Telegram-каналов HOTLINE.
Генерирует посты с помощью **Groq AI** и публикует их по расписанию.

---

## 📁 Структура файлов

```
hotline_bot/
├── main.py            — запуск бота и планировщик
├── config.py          — настройки каналов и расписания
├── generator.py       — генерация постов через Groq
├── sender.py          — отправка в Telegram
├── photo.py           — поиск и загрузка фото (Unsplash)
├── test_generate.py   — тест генерации без отправки
├── requirements.txt   — зависимости
├── .env               — твои ключи (создать из .env.example)
├── .env.example       — шаблон
└── digest_photo.jpg   — фото для дайджеста (загрузи сам)
```

---

## 🚀 Установка и запуск

### Шаг 1 — Установить зависимости
```bash
pip install -r requirements.txt
```

### Шаг 2 — Создать бота в Telegram
1. Открой @BotFather в Telegram
2. Напиши `/newbot`
3. Придумай имя и юзернейм
4. Скопируй **токен**

### Шаг 3 — Добавить бота в каналы
- Зайди в каждый канал → Настройки → Администраторы
- Добавь своего бота
- Дай права: **Публикация сообщений**

### Шаг 4 — Получить Groq API Key
1. Зайди на [console.groq.com](https://console.groq.com)
2. Создай аккаунт (бесплатно)
3. API Keys → Create API Key
4. Скопируй ключ

### Шаг 5 — Получить Unsplash Key (необязательно)
1. Зайди на [unsplash.com/developers](https://unsplash.com/developers)
2. New Application
3. Скопируй **Access Key**
> Без этого ключа бот будет использовать стандартные фото

### Шаг 6 — Настроить .env
```bash
cp .env.example .env
```
Открой `.env` и заполни:
```
TELEGRAM_BOT_TOKEN=1234567890:ABC...
GROQ_API_KEY=gsk_...
UNSPLASH_ACCESS_KEY=...  # необязательно
CHANNEL_MAIN=@hotline_feed
CHANNEL_AUTO=@hotline_pedal
...
```

### Шаг 7 — Добавить фото для дайджеста
Положи файл `digest_photo.jpg` в папку бота.
Это фото будет отправляться каждый день в 20:00 с дайджестом.

### Шаг 8 — Тест генерации (без отправки)
```bash
python test_generate.py
```
Убедись что посты генерируются нормально.

### Шаг 9 — Запуск
```bash
python main.py
```

---

## ⏰ Расписание по умолчанию

| Время | Что происходит |
|-------|----------------|
| 08:00 | Тематический канал (авто) |
| 09:00 | Основной канал |
| 10:00 | Тематический канал (стриминг) |
| 11:00 | Основной канал |
| 12:00 | Тематический канал (тикток) |
| 13:00 | Основной канал |
| 14:00 | Тематический канал (политика) |
| 15:00 | Основной канал |
| 16:00 | Тематический канал (технологии) |
| 17:00 | Основной канал |
| 18:00 | Тематический канал (игры) |
| 20:00 | **Дайджест дня** (основной) |
| 21:00 | Основной канал |
| 22:00 | Тематический канал (следующий по кругу) |

---

## 🖥️ Запуск на сервере (24/7)

### Вариант 1 — systemd (Linux VPS)
```bash
sudo nano /etc/systemd/system/hotline-bot.service
```
```ini
[Unit]
Description=HOTLINE Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/hotline_bot
ExecStart=/usr/bin/python3 /home/ubuntu/hotline_bot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl enable hotline-bot
sudo systemctl start hotline-bot
sudo systemctl status hotline-bot
```

### Вариант 2 — screen (простой способ)
```bash
screen -S hotline
python main.py
# Ctrl+A, D — выйти не останавливая
screen -r hotline  # вернуться
```

### Вариант 3 — Railway / Render (бесплатный хостинг)
- Залей код на GitHub
- Подключи к Railway.app или Render.com
- Укажи переменные окружения в настройках
- Команда запуска: `python main.py`

---

## 🛠️ Изменить расписание

В файле `main.py` найди секцию `# Планировщик`:
```python
# Тематические каналы — каждые 2 часа начиная с 8:00
for hour in [8, 10, 12, 14, 16, 18, 22]:
```
Измени часы под себя.

---

## 📊 Логи

Все действия пишутся в `hotline_bot.log`:
```bash
tail -f hotline_bot.log
```

---

## ❓ Частые проблемы

**Бот не отправляет сообщения:**
- Проверь что бот добавлен как администратор канала
- Проверь токен в .env

**Ошибка Groq:**
- Проверь API ключ
- Проверь лимиты на console.groq.com (бесплатный план: 14400 запросов/день)

**Фото не загружается:**
- Бот отправит пост без фото — это нормально
- Проверь Unsplash ключ или оставь пустым
