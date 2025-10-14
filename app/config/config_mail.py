from fastapi_mail import ConnectionConfig
from pydantic import EmailStr
import os
from dotenv import load_dotenv
load_dotenv()

def get_mail_config():
    return ConnectionConfig(
        MAIL_USERNAME=os.getenv("SMTP_USERNAME", "your_email@gmail.com"),
        MAIL_PASSWORD=os.getenv("SMTP_PASSWORD", "your_password"),
        MAIL_FROM=os.getenv("SMTP_FROM", "your_email@gmail.com"),
        MAIL_PORT=587,
        MAIL_SERVER="smtp.gmail.com",
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False, 
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
        TEMPLATE_FOLDER="app/templates/email",  # путь к шаблонам писем
    )