from celery import shared_task
from personal_accounts.accounts.management.commands.check_inactive_users import Command

@shared_task
def check_inactive_users():
    Command().handle()