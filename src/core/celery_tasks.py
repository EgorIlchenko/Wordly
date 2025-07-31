from email.message import EmailMessage

from celery import Celery
from smtplib import SMTP

from core.settings import get_settings

settings = get_settings()

celery = Celery(
    'Wordly',
    backend='rpc://',
    broker=f'amqp://{settings.rabbitmq.user}:{settings.rabbitmq.password}@rabbitmq:5672//'
)


@celery.task(name='tasks.send_verification_email', bind=True, max_retries=3)
def send_verification_email(self, email: str, code: str):
    msg = EmailMessage()
    msg["Subject"] = "Подтверждение регистрации на Wordloop"
    msg["From"] = settings.smtp.from_
    msg["To"] = email
    msg.set_content(f"""\
        Здравствуйте!

        Вы зарегистрировались на платформе Wordloop.
        Ваш код подтверждения: {code}

        С уважением,
        Команда Wordloop
        """)

    try:
        with SMTP(settings.smtp.host, settings.smtp.port) as server:
            server.starttls()
            server.login(settings.smtp.user, settings.smtp.password)
            server.send_message(msg=msg)
    except Exception as e:
        raise self.retry(exc=e, countdown=60)
