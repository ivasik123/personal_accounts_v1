from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.user_logout, name='logout'),
    path('courses/', views.subscribe_to_course, name='subscribe'),
    path('courses/', views.unsubscribe_from_course, name='unsubscribe'),
    path('register/', views.student_register, name='student_register'),
]