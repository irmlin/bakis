import smtplib
import ssl
from email.message import EmailMessage
from email.mime.text import MIMEText
from typing import List

from ..settings import EMAIL_SECRET
from ..models import Recipient
import asyncio
import aiosmtplib


class EmailManager:
    def __init__(self):
        self.__sender = 'bakalaurotestinis@gmail.com'
        self.__email_secret = EMAIL_SECRET

    async def send(self, recipients: List[Recipient], subject: str, body: str):
        server = aiosmtplib.SMTP(hostname='smtp.gmail.com', port=465, start_tls=False, use_tls=True)
        await server.connect()
        await server.login(self.__sender, self.__email_secret)
        for recipient in recipients:
            em = MIMEText(body, 'html')
            em['From'] = self.__sender
            em['To'] = recipient.email
            em['Subject'] = subject
            await server.sendmail(self.__sender, recipient.email, em.as_string())
        await server.quit()

        # context = ssl.create_default_context()
        # with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
        #     server.login(self.__sender, self.__email_secret)
        #     for recipient in recipients:
        #         # em = EmailMessage()
        #         em = MIMEText(body, 'html')
        #         em['From'] = self.__sender
        #         em['To'] = recipient.email
        #         em['Subject'] = subject
        #         # em.set_content(body)
        #         server.sendmail(self.__sender, recipient.email, em.as_string())
