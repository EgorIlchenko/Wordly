plain_text_content = """
Здравствуйте!

Чтобы восстановить пароль, пожалуйста, скопируйте и вставьте эту ссылку в ваш браузер:
{reset_link}

Если вы не запрашивали восстановление пароля, просто проигнорируйте это письмо.

С уважением,
Команда Wordloop
"""

html_content = """
<html>
<head></head>
<body>
    <div style="font-family: Arial, sans-serif; line-height: 1.6;">
        <h2>Здравствуйте!</h2>
        <p>Вы запросили восстановление пароля для вашего аккаунта на Wordloop.</p>
        <p>Пожалуйста, нажмите на кнопку ниже, чтобы установить новый пароль:</p>
        <a href="{reset_link}"
           style="display: inline-block; padding: 10px 20px; font-size: 16px;
           color: white; background-color: #7b2cbf; text-decoration: none;
           border-radius: 5px;">
           Сбросить пароль
        </a>
        <p>Ссылка будет действительна в течение одного часа.</p>
        <p>Если вы не запрашивали восстановление пароля, просто проигнорируйте это письмо.</p>
        <br>
        <p>С уважением,<br>Команда Wordloop</p>
    </div>
</body>
</html>
"""
