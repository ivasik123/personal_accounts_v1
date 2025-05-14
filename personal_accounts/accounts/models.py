from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

from django.core.exceptions import ValidationError


class UserProfileManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')

        email = self.normalize_email(email)
        extra_fields.setdefault('role', 'student')
        user = self.model(email=email, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

    def update_activity(self):
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])


class UserProfile(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('student', 'Студент'),
        ('teacher', 'Преподаватель'),
        ('admin', 'Администратор'),
    ]

    email = models.EmailField(unique=True, verbose_name="Email")
    username = models.CharField(max_length=150, blank=True, verbose_name="Username")
    contacts = models.TextField(blank=True, verbose_name="Contacts")
    notifications = models.TextField(blank=True, verbose_name="Notifications")
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Date joined")
    last_login = models.DateTimeField(null=True, blank=True, verbose_name="Last login")
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student',
        verbose_name="Роль"
    )
    is_active = models.BooleanField(default=True, verbose_name="Active")
    is_staff = models.BooleanField(default=False, verbose_name="Staff status")
    last_activity = models.DateTimeField(
        verbose_name="Последняя активность",
        default=timezone.now
    )
    last_admin_access = models.DateTimeField(
        verbose_name="Последний вход в админку",
        null=True,
        blank=True
    )


    objects = UserProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "User profiles"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email

    def clean(self):
        super().clean()
        if self.role not in dict(self.ROLE_CHOICES).keys():
            raise ValidationError(
                f"Invalid role. Must be one of: {dict(self.ROLE_CHOICES)}"
            )

class SomeModel(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название курса")
    description = models.TextField(verbose_name="Описание")
    teachers = models.ManyToManyField(
        UserProfile,
        related_name='teaching_courses',
        verbose_name="Преподаватели"
    )
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    is_active = models.BooleanField(default=True, verbose_name="Активный курс")

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self):
        return self.title


class Subscription(models.Model):
    student = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name="Студент"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name="Курс"
    )
    date_subscribed = models.DateTimeField(auto_now_add=True, verbose_name="Дата подписки")
    is_active = models.BooleanField(default=True, verbose_name="Активная подписка")

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.email} - {self.course.title}"