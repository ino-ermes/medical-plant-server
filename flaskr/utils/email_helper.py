from flask_mail import Mail, Message


class EmailSender:
    __instance = None

    @staticmethod
    def get_instance():
        if EmailSender.__instance is None:
            EmailSender()
        return EmailSender.__instance

    def __init__(self):
        if EmailSender.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.__mail = Mail()
            self.__app = None
            EmailSender.__instance = self

    def init_app(self, app):
        self.__app = app
        self.__mail.init_app(app)

    def send_email(self, subject, recipients, sender, body):
        with self.__app.app_context():
            email = Message(
                subject=subject, recipients=recipients, sender=sender, body=body
            )
            self.__mail.send(email)
