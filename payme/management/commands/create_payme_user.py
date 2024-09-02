from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

user_model = get_user_model()


class Command(BaseCommand):
    help = "Create user for Payme"
    username = "Paycom"
    password = settings.PAYME_SETTINGS["SECRET_KEY"]
    username_key = user_model.USERNAME_FIELD

    def handle(self, *args, **options):
        try:
            user, _ = user_model.objects.update_or_create(
                **{self.username_key: self.username}
            )
            user.set_password(self.password)
            user.save()
            self.stdout.write(self.style.SUCCESS("Success"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
