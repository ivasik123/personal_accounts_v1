from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Подключение URL-адресов приложения accounts
    path('accounts/', include('accounts.urls')),
    
    # API Auth endpoints
    path('api/auth/', include('rest_framework.urls', namespace='rest_framework')),
]
