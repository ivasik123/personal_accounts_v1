from django.test import Client
from django.urls import reverse
from .models import Course, Subscription, UserProfile
from .serializers import UserProfileSerializer, CourseSerializer
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.test import TestCase, RequestFactory
from .middleware import UserActivityMiddleware, AdminAccessMiddleware
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

#views
class AuthViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserProfile.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    def test_login_view(self):
        response = self.client.post(reverse('login'), {
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile'))

    def test_invalid_login(self):
        response = self.client.post(reverse('login'), {
            'email': 'wrong@example.com',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Неверный email или пароль.')

    def test_profile_view_unauthorized(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)

        login_url = reverse('login')
        self.assertTrue(response.url.startswith(login_url))

        if 'next=' in response.url:
            self.assertIn('next=', response.url)

    def test_logout_view(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))


class CourseSubscriptionTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserProfile.objects.create_user(
            email='student@example.com',
            password='testpass'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            start_date='2023-01-01',
            end_date='2023-12-31'
        )

    def test_subscribe_unsubscribe(self):
        self.client.login(email='student@example.com', password='testpass')

        subscribe_url = reverse('course-subscribe', args=[self.course.id])
        unsubscribe_url = reverse('course-unsubscribe', args=[self.course.id])

        # Subscribe
        response = self.client.post(subscribe_url)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Subscription.objects.filter(
                student=self.user,
                course=self.course
            ).exists()
        )

        # Unsubscribe
        response = self.client.post(unsubscribe_url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Subscription.objects.filter(
                student=self.user,
                course=self.course
            ).exists()
        )

#serializers
class UserProfileSerializerTest(TestCase):
    def test_create_user(self):
        data = {
            'email': 'new@example.com',
            'password': 'newpass123',
            'username': 'newuser'
        }
        serializer = UserProfileSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        user = serializer.save()

        self.assertEqual(user.email, 'new@example.com')
        self.assertEqual(user.username, 'newuser')

        self.assertTrue(user.check_password('newpass123'))

    def test_invalid_email(self):
        data = {
            'email': 'invalid',
            'password': 'testpass'
        }
        serializer = UserProfileSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class CourseSerializerTest(TestCase):
    def test_course_serialization(self):
        course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            start_date='2023-01-01',
            end_date='2023-12-31'
        )
        serializer = CourseSerializer(course)
        self.assertEqual(serializer.data['title'], 'Test Course')
        self.assertEqual(serializer.data['is_active'], True)

#models
class UserProfileModelTest(TestCase):
    def test_create_user(self):
        user = UserProfile.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertEqual(user.role, 'student')

    def test_create_superuser(self):
        admin_user = UserProfile.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertEqual(admin_user.email, 'admin@example.com')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertEqual(admin_user.role, 'admin')

    def test_role_validation(self):
        user = UserProfile(email='test@example.com', role='invalid')
        with self.assertRaises(ValidationError):
            user.full_clean()


class CourseModelTest(TestCase):
    def setUp(self):
        self.teacher = UserProfile.objects.create_user(
            email='teacher@example.com',
            password='testpass',
            role='teacher'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timezone.timedelta(days=30)).date()
        )
        self.course.teachers.add(self.teacher)

    def test_course_creation(self):
        self.assertEqual(str(self.course), 'Test Course')
        self.assertEqual(self.course.teachers.count(), 1)


class SubscriptionModelTest(TestCase):
    def setUp(self):
        self.student = UserProfile.objects.create_user(
            email='student@example.com',
            password='testpass'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timezone.timedelta(days=30)).date()
        )
        self.subscription = Subscription.objects.create(
            student=self.student,
            course=self.course
        )

    def test_subscription_creation(self):
        self.assertEqual(
            str(self.subscription),
            'student@example.com - Test Course'
        )
        self.assertTrue(self.subscription.is_active)

#midleware
class MiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = UserProfile.objects.create_user(
            email='test@example.com',
            password='testpass'
        )
        self.middleware = UserActivityMiddleware(lambda r: None)
        self.admin_middleware = AdminAccessMiddleware(lambda r: None)

    def test_user_activity_middleware(self):
        request = self.factory.get('/any-url/')
        request.user = self.user
        self.middleware(request)
        updated_user = UserProfile.objects.get(pk=self.user.pk)
        self.assertIsNotNone(updated_user.last_activity)

    def test_admin_access_middleware(self):
        request = self.factory.get('/admin/')
        request.user = self.user
        self.admin_middleware(request)
        updated_user = UserProfile.objects.get(pk=self.user.pk)
        self.assertIsNone(updated_user.last_admin_access)  # Not admin user

        admin_user = UserProfile.objects.create_superuser(
            email='admin@example.com',
            password='adminpass'
        )
        request.user = admin_user
        self.admin_middleware(request)
        updated_admin = UserProfile.objects.get(pk=admin_user.pk)
        self.assertIsNotNone(updated_admin.last_admin_access)

#api
class UserAPITest(APITestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)

    def test_user_login(self):
        url = reverse('api-login')
        response = self.client.post(url, {
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

    def test_get_current_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('userprofile-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], 'test@example.com')


class CourseAPITest(APITestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(
            email='student@example.com',
            password='testpass'
        )
        self.token = Token.objects.create(user=self.user)
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            start_date='2023-01-01',
            end_date='2023-12-31'
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_subscribe_to_course(self):
        url = reverse('course-subscribe', args=[self.course.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'subscribed')

    def test_unsubscribe_from_course(self):
        self.client.post(reverse('course-subscribe', args=[self.course.id]))

        url = reverse('course-unsubscribe', args=[self.course.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'unsubscribed')