from django.utils import timezone
from django.urls import reverse
from .models import UserProfile
import logging

logger = logging.getLogger(__name__)

class UserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            UserProfile.objects.filter(pk=request.user.pk).update(
                last_activity=timezone.now()
            )

        return response


class AdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if (request.user.is_authenticated and
                request.path.startswith(reverse('admin:index')) and
                request.method == 'GET'):
            UserProfile.objects.filter(pk=request.user.pk).update(
                last_admin_access=timezone.now()
            )
            logger.info(f"User {request.user} accessed admin at {timezone.now()}")

        return response