from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import UserProfileViewSet, CourseViewSet, SubscriptionViewSet

router = DefaultRouter()
router.register(r'users', UserProfileViewSet, basename='user')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')

urlpatterns = [
    # HTML views
    path('login/', views.user_login, name='login'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.student_register, name='student_register'),

    # API views
    path('api/', include(router.urls)),
    path('api/login/', views.UserProfileViewSet.as_view({'post': 'login'}), name='api-login'),
    path('api/me/', views.UserProfileViewSet.as_view({'get': 'me'}), name='userprofile-me'),
    path('api/courses/<int:pk>/subscribe/', views.CourseViewSet.as_view({'post': 'subscribe'}), name='course-subscribe'),
    path('api/courses/<int:pk>/unsubscribe/', views.CourseViewSet.as_view({'post': 'unsubscribe'}), name='course-unsubscribe'),

    # Admin reports
    path('admin/user-activity/', views.user_activity_report, name='user_activity_report'),

    *router.urls,
]