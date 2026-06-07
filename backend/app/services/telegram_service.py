# Module: app.services.telegram_service
# Description: Service for Telegram Bot API integration with verification token mapping.

import httpx
import logging
import uuid
from typing import Dict, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class TelegramBotService:
    # In-memory dictionary mapping verification tokens to user_ids for connection flow
    # token -> user_uuid
    _connection_tokens: Dict[str, uuid.UUID] = {}

    @classmethod
    def generate_connection_token(cls, user_id: uuid.UUID) -> str:
        """Generates a one-time UUID token to connect user's Telegram."""
        token = str(uuid.uuid4())
        cls._connection_tokens[token] = user_id
        return token

    @classmethod
    def verify_token(cls, token: str, chat_id: str) -> Optional[uuid.UUID]:
        """Validates token and returns user_id if matched."""
        if token in cls._connection_tokens:
            user_id = cls._connection_tokens.pop(token)
            logger.info(f"Verified Telegram token for user {user_id} with chat_id {chat_id}")
            return user_id
        return None

    @staticmethod
    def send(chat_id: str, message_text: str, parse_mode: str = "Markdown") -> bool:
        """
        Sends message to Telegram chat. Fallback to logger if TELEGRAM_BOT_TOKEN is missing.
        """
        if not settings.TELEGRAM_BOT_TOKEN:
            logger.info(f"[TELEGRAM MOCK SEND] ChatID: {chat_id} | Message: {message_text}")
            return True

        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message_text,
            "parse_mode": parse_mode
        }
        try:
            response = httpx.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                logger.info(f"Telegram message sent successfully to {chat_id}")
                return True
            else:
                logger.error(f"Telegram API failed with code {response.status_code}: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Failed to connect to Telegram API: {e}")
            return False
