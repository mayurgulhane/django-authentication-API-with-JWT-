from django.core.mail import EmailMessage
import os

class Util:
    @staticmethod
    def send_email(data):
        print("*"*100)
        print(os.environ.get('EMAIL_FROM'),)
        email = EmailMessage(
            subject=data['subject'],
            body=data['body'],
            from_email = os.environ.get('EMAIL_FROM'),  # 'mayurkgulhane88@gmail.com'
            to = [data['to_email']]
        )
        email.send()
    