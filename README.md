# MyTracker Bot

**MyTracker Bot** is a Telegram interface for a personal task tracker.  
This repository contains the bot application that interacts with the [MyTracker backend](https://github.com/TheAppleKingy/MyTracker_api).

- [Install](#install)
- [Quickstart](#quickstart)
- [Usage](#usage)
- [Peculiarities](#peculiarities)
- [Stack](#stack)

---

## ⚙️ Install

Before running the bot, define the following environment variables:

| Variable              | Description                                                                  |
|-----------------------|------------------------------------------------------------------------------|
| `REDIS_PASSWORD`      | Redis password                                                               |
| `REDIS_HOST`      | Host for redis connection(just container hostname)                                                               |
| `SECRET`      | Secret to sign authentication tokens                                                              |
| `BOT_TOKEN`           | Token obtained from [@BotFather](https://t.me/BotFather)                     |
| `TIMEZONE_DB_API_KEY` | API key from [TimeZoneDB](https://timezonedb.com/) to support timezone setup |
| `TIMEZONE_DB_URL`      | API url of TimeZone service                                                              |
| `BASE_API_URL`        | URL of the backend API (e.g. `http://backend_container_name:8000/api`)       |
| `FLOWER_USER`        | Flower admin username       |
| `FLOWER_PASSSWORD`        | Flower admin password       |

📌 To get a `TIMEZONE_DB_API_KEY`, register at [timezonedb.com](https://timezonedb.com/), then set the key in your environment.

Once the environment is configured and the backend ([MyTracker_api](https://github.com/TheAppleKingy/MyTracker_api)) is running, you can start the bot with:

```bash
make tracker.bot.prod.build.start
```

---

## 🚀 Quickstart

1. Start the bot in Telegram using the `/start` command  
2. Complete the registration process  
3. Set your time zone when prompted  
4. You will now have access to the bot's main interface, which is intuitive and user-friendly

---

## 📦 Usage

The bot allows you to:

- ✅ Create tasks
- 🔍 View current and past tasks
- ⏰ Set reminders
- 🗑️ Delete tasks (when completed or no longer needed)

All interactions happen directly through the Telegram chat interface.

---

## 🌐 Peculiarities

- 🧩 **Tree-like Task Structure**:  
  Tasks can have subtasks, and subtasks can have their own subtasks — with no depth limitation in the current version.

- 🌍 **Time Zone Required**:  
  After registration, the bot will **require** you to set your time zone.  
  This ensures all time-related features (like reminders, due times, etc.) are correctly localized for your region.  
  If you skip this step, the bot will continue to prompt you until it’s configured.

---

## 🧰 Stack

- **aiogram** – Telegram bot framework  
- **Redis** – message broker  
- **Celery** – background task processing  
- **pycountry** – for country/timezone resolution

Feel free to contribute or open issues.
