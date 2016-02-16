import re

from django.core.mail import get_connection
from django.core.mail.backends.base import BaseEmailBackend

from .conf import settings
from .models import Email
searchString = 'ALERT'

class EmailBackend(BaseEmailBackend):

    """Wrapper email backend that records all emails in a database model"""

    def __init__(self, **kwargs):
        super(EmailBackend, self).__init__(**kwargs)
        self.connection = get_connection(settings.EMAIL_LOG_BACKEND, **kwargs)

    def send_messages(self, email_messages):
        num_sent = 0
        for message in email_messages:
            recipients = '; '.join(message.to)
            if re.search(searchString, message.subject, flags=0):
                #log outgoing messages only for matched string
                email = Email.objects.create(
                    from_email=message.from_email,
                    recipients=recipients,
                    subject=message.subject,
                    body=message.body,
                )
            else:
                pass
            message.connection = self.connection
            num_sent += message.send()
            if num_sent > 0 and re.search(searchString, message.subject, flags=0):
                #log outgoing messages only for matched string
                email.ok = True
                email.save()
        return num_sent
