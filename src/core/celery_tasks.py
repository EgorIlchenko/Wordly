from email.message import EmailMessage
from smtplib import SMTP

from celery import Celery

from core.msg_templates import html_content, plain_text_content
from core.settings import get_settings

settings = get_settings()

celery = Celery(
    "Wordly",
    backend="rpc://",
    broker=f"amqp://{settings.rabbitmq.user}:{settings.rabbitmq.password}@"
    f"{settings.rabbitmq.host}:{settings.rabbitmq.port}//",
)


@celery.task(name="tasks.send_verification_email", bind=True, max_retries=3)
def send_verification_email(self, email: str, code: str):
    msg = EmailMessage()
    msg["Subject"] = "Подтверждение регистрации на Wordloop"
    msg["From"] = settings.smtp.from_
    msg["To"] = email
    msg.set_content(
        f"""
        Здравствуйте!

        Вы зарегистрировались на платформе Wordloop.
        Ваш код подтверждения: {code}

        С уважением,
        Команда Wordloop
        """
    )

    try:
        with SMTP(settings.smtp.host, settings.smtp.port) as server:
            server.starttls()
            server.login(settings.smtp.user, settings.smtp.password)
            server.send_message(msg=msg)
    except Exception as e:
        raise self.retry(exc=e, countdown=60)


@celery.task(name="tasks.send_password_reset_email", bind=True, max_retries=3)
def send_password_reset_email(self, email: str, token: str):
    reset_link = f"http://localhost:8001/api/v1/auth/reset-password?token={token}"

    msg = EmailMessage()
    msg["Subject"] = "Восстановление пароля на Wordloop"
    msg["From"] = settings.smtp.from_
    msg["To"] = email
    msg.set_content(
        plain_text_content.format(reset_link=reset_link),
    )
    msg.add_alternative(
        html_content.format(reset_link=reset_link),
        subtype="html",
    )

    try:
        with SMTP(settings.smtp.host, settings.smtp.port) as server:
            server.starttls()
            server.login(settings.smtp.user, settings.smtp.password)
            server.send_message(msg=msg)
    except Exception as e:
        raise self.retry(exc=e, countdown=60)
