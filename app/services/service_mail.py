import aiosmtplib
from email.message import EmailMessage
from pydantic import EmailStr

import os
from dotenv import load_dotenv
load_dotenv()

from app.config import config_app
from app.utils.templates import render_template


class ServiceMail:

    @staticmethod
    async def send_mail_async(to_email: EmailStr, subject: str, template_name: str, context: dict):
        # Рендерим html с подстановкой данных
        html_content = render_template(template_name, context)

        message = EmailMessage()
        message["From"] = os.getenv("SMTP_FROM")
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(html_content, subtype="html")

        await aiosmtplib.send(
            message,
            hostname=os.getenv("SMTP_HOST"),
            port=int(os.getenv("SMTP_PORT")),
            start_tls=True,
            username=os.getenv("SMTP_USERNAME"),
            password=os.getenv("SMTP_PASSWORD"),
        )