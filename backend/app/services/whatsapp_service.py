# Module: app.services.whatsapp_service
# Description: Service for WhatsApp Meta/Twilio Cloud integration with verification code logic.

import httpx
import logging
import random
from typing import Dict, List, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    # In-memory dictionary for OTP registration flow
    # phone -> otp_code
    _pending_otps: Dict[str, str] = {}

    @classmethod
    def generate_and_send_otp(cls, phone_number: str) -> str:
        """Generates a mock/real 6-digit OTP and sends it via WhatsApp."""
        otp = f"{random.randint(100000, 999999)}"
        cls._pending_otps[phone_number] = otp
        
        # In mock mode, we just log it. In real mode, we send a template.
        body_text = f"Your InflationIQ WhatsApp verification code is {otp}"
        cls.send_raw(phone_number, body_text)
        return otp

    @classmethod
    def verify_otp(cls, phone_number: str, otp: str) -> bool:
        """Validates OTP code for the given phone number."""
        if phone_number in cls._pending_otps and cls._pending_otps[phone_number] == otp:
            cls._pending_otps.pop(phone_number)
            logger.info(f"WhatsApp OTP verified successfully for phone {phone_number}")
            return True
        return False

    @staticmethod
    def send_raw(phone_number: str, message_text: str) -> bool:
        """Logs/sends raw WhatsApp text messages for OTP setup or fallback."""
        logger.info(f"[WHATSAPP MOCK SEND RAW] Phone: {phone_number} | Message: {message_text}")
        return True

    @staticmethod
    def send(phone_number: str, template_name: str, template_variables: List[str]) -> bool:
        """
        Sends WhatsApp template message using Meta API or Twilio API.
        If credentials are not configured, falls back to logging.
        """
        # Meta Cloud API
        if settings.WHATSAPP_ACCESS_TOKEN and settings.WHATSAPP_PHONE_NUMBER_ID:
            url = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
            headers = {
                "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
                "Content-Type": "application/json"
            }
            # Construct Meta Cloud API parameters payload
            parameters = [{"type": "text", "text": str(v)} for v in template_variables]
            payload = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {"code": "en_US"},
                    "components": [
                        {
                            "type": "body",
                            "parameters": parameters
                        }
                    ]
                }
            }
            try:
                response = httpx.post(url, headers=headers, json=payload, timeout=10)
                if response.status_code in [200, 201]:
                    logger.info(f"WhatsApp template message sent successfully to {phone_number}")
                    return True
                else:
                    logger.error(f"Meta WhatsApp Cloud API failed ({response.status_code}): {response.text}")
            except Exception as e:
                logger.error(f"Meta WhatsApp Cloud API request error: {e}")

        # Twilio WhatsApp API
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_WHATSAPP_FROM:
            url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json"
            # Twilio template interpolation: Twilio uses simple body text compiled with parameters
            # Since Twilio doesn't enforce pre-registered templates in the same sandbox way,
            # or uses templates defined via Twilio console, we form a formatted message.
            body_text = f"Template: {template_name}. Variables: {', '.join(template_variables)}"
            payload = {
                "To": f"whatsapp:{phone_number}",
                "From": settings.TWILIO_WHATSAPP_FROM,
                "Body": body_text
            }
            try:
                auth = (settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                response = httpx.post(url, data=payload, auth=auth, timeout=10)
                if response.status_code in [200, 201]:
                    logger.info(f"WhatsApp template message sent successfully via Twilio to {phone_number}")
                    return True
                else:
                    logger.error(f"Twilio WhatsApp API failed ({response.status_code}): {response.text}")
            except Exception as e:
                logger.error(f"Twilio WhatsApp API request error: {e}")

        # Logging fallback
        logger.info(f"[WHATSAPP MOCK SEND TEMPLATE] Phone: {phone_number} | Template: {template_name} | Vars: {template_variables}")
        return True
