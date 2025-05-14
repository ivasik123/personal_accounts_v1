from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from personal_accounts.accounts.models import UserProfile
from datetime import timedelta


class Command(BaseCommand):
    help = 'Проверяет неактивных пользователей'

    def handle(self, *args, **options):
        one_year_ago = timezone.now() - timedelta(days=365)

        # Пользователи без общей активности
        inactive_users = UserProfile.objects.filter(
            last_activity__lte=one_year_ago,
            is_active=True
        )

        # Пользователи без входа в админку (для staff)
        inactive_admin_users = UserProfile.objects.filter(
            is_staff=True,
            last_admin_access__lte=one_year_ago,
            is_active=True
        )

        for user in inactive_users:
            self.send_warning_email(user, 'аккаунта')

        for user in inactive_admin_users:
            self.send_warning_email(user, 'админ-доступа')

        self.stdout.write(f"Отправлено уведомлений: {inactive_users.count() + inactive_admin_users.count()}")

def send_warning_email(self, user, account_type):
        subject = f'Ваш {account_type} будет деактивирован'
        message = f'''
        Уважаемый {user.username},

        Вы не использовали ваш {account_type} более года.
        Последняя активность: {user.last_activity}
        '''
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )