from django.core.management.base import BaseCommand
from django.utils import timezone
from personal_accounts.accounts.models import UserProfile
from datetime import timedelta


class Command(BaseCommand):
    help = 'Удаляет неактивных пользователей после предупреждения'

    def handle(self, *args, **options):
        one_year_30days_ago = timezone.now() - timedelta(days=395)  # Год + 30 дней

        inactive_users = UserProfile.objects.filter(
            last_activity__lte=one_year_30days_ago,
            is_active=True
        )

        count = inactive_users.count()
        inactive_users.delete()

        self.stdout.write(f"Удалено неактивных пользователей: {count}")