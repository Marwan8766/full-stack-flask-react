from flask_mail import Mail
from flask_mail import Message
from flask import current_app

mail = Mail()


def send_email(subject, recipient, text_body, html_body):
    print('sending email...')
    try:
        print('sending email...')
        msg = Message(subject, sender=current_app.config.get('EMAIL_USERNAME'), recipients=[recipient])
        msg.body = text_body
        msg.html = html_body
        print('will be sent')
        mail.send(msg)
        print('Mail sent to', recipient)
    except Exception as e:
        print('An error occurred while sending email:', str(e))