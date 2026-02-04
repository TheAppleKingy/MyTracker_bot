import requests

from dishka.integrations.celery import FromDishka

from src.application.interfaces.storage import SyncStorageInterface
from src.infra.configs import BotConfig
from src.celery_app import celery_app
from src.logger import logger


@celery_app.task(bind=True)
def notify(
    self,
    text: str,
    chat_id: int,
    tg_name: str,
    task_id: int,
    storage: FromDishka[SyncStorageInterface],
    conf: FromDishka[BotConfig]
):
    try:
        response = requests.post(
            conf.bot_send_message_url,
            json={
                "chat_id": chat_id,
                "text": f"<b>{text}</b>",
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
                "reply_markup": {
                    "inline_keyboard": [[
                        {"text": "To task", "callback_data": f"get_task_{task_id}"}
                    ]]}
            }
        )
        response.raise_for_status()
    except Exception as e:
        logger.error(f"An error occured when trying to send reminder to user '{tg_name}': {e}")
    finally:
        storage.delete_reminders(tg_name, [self.request.id], task_id)
