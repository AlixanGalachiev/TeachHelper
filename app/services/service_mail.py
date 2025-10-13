from pydantic import EmailStr
from fastapi_mail import FastMail, MessageSchema, MessageType

from app import settings
from app.config.config_mail import get_mail_config

class ServiceMail:
    def __init__(self):
        self.mail = FastMail(get_mail_config())

    async def send_reset_password(self, email: EmailStr, name: str, token: str):
        reset_link = f"{settings.FRONT_URL}/reset-password?token={token}"
        
        message = MessageSchema(
            subject="Сброс пароля",
            recipients=[email],
            template_body={"name": name, "reset_link": reset_link},
            subtype=MessageType.html,
        )
        await self.mail.send_message(message, template_name="reset_password.html")