# MyTracker - is a personal task tracker controlling by telegram bot. This repository contains code for bot app.

- [Install](#install)
- [Quickstart](#quickstart)
- [Usage](#usage)
- [Peculiarities](#peculiarities)
- [Stack](#stack)

---
## Install
To start container env must contain next variables:
* CELERY_WORKERS - **core's count that celery worker can use**
* CELERY_BROKER_URL - **the same REDIS_URL**
* REDIS_PASSWORD
* REDIS_URL
* BOT_TOKEN - **must be got by BotFather**
* BOT_QUEUE - **name for celery worker's queue**
* TIMEZONE_DB_API_KEY
* BASE_API_URL - **http://backend_container_name:8000/api**

Bot uses this [api](https://timezonedb.com/) for providing easy way to customize user time zone. Follow the link, register and get API token that will be send as `TIMEZONE_DB_API_KEY` value.

When env setup and backend(repository [MyTracker_api](https://github.com/TheAppleKingy/MyTracker_api)) was runned you can build and run containers by executing
```
docker compose up --build
```
---
## Quickstart
To start send /start command to the bot. After registration you will have access to the main bot's interface. It is quite intuitive.
___
## Usage
You can create tasks, show info about current and passed tasks, set reminders. Also if task is not actually for you or task was complete and is no longer needed in the task list you can delete it. 
___
## Peculiarities
* Tasks have tree-like structure. It means you can create subtasks for tasks. And create subtasks for subtasks. In current version depth not limited.
* After registration bot will offer set time zone. It is mandatory. If you will not set time zone, when you will want show task info and any of other cases bot will ask you set time zone anyway. It is important because all info related with time must be localized for user.
---
## Stack

* aiogram
* redis
* celery
* pycountry
