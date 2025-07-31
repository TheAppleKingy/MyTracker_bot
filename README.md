# MyTracker - is a personal task controlling by telegram bot. This repository contain code for bot app.

- [Quickstart](#quickstart)
- [Usage](#usage)
- [Peculiarities](#peculiarities)
- [Stack](#stack)

---
## Quickstart
To start container enc must contain next variables:
* CELERY_WORKERS
* CELERY_BROKER_URL
* REDIS_PASSWORD
* REDIS_URL
* BOT_TOKEN
* BOT_QUEUE
* TIMEZONE_DB_API_KEY
* BASE_API_URL

Bot uses this [api](https://timezonedb.com/) for providing easy way to customize user time zone. Follow the link, register and get API token that will be send as `TIMEZONE_DB_API_KEY` value.

When env setup and backend(repository [MyTracker_api](https://github.com/TheAppleKingy/MyTracker_api)) was runned you can build and run containers by executing
```
docker compose up --build
```
---
## Usage
This bot provid
