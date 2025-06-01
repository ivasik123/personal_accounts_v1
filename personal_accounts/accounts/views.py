from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from .forms import StudentRegistrationForm
from .models import Course, Subscription, UserProfile


@csrf_protect
def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')
        else:
            messages.error(request, 'Неверный email или пароль.')
    return render(request, 'accounts/login.html')

def profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/profile.html', {'user_profile': request.user})

def user_logout(request):
    logout(request)
    return redirect('login')

def subscribe_to_course(request, course_id):
    course = Course.objects.get(id=course_id)
    Subscription.objects.get_or_create(
        student=request.user,
        course=course,
        defaults={'is_active': True}
    )
    return redirect('profile')

def unsubscribe_from_course(request, course_id):
    Subscription.objects.filter(
        student=request.user,
        course_id=course_id
    ).delete()
    return redirect('profile')

from django.contrib.auth.decorators import user_passes_test

@user_passes_test(lambda u: u.is_superuser)
def user_activity_report(request):
    users = UserProfile.objects.all().order_by('-last_activity')
    return render(request, 'admin/user_activity.html', {'users': users})


def student_register(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('profile')
        else:
            messages.error(request, 'Ошибка при регистрации. Пожалуйста, исправьте ошибки.')
    else:
        form = StudentRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .serializers import UserProfileSerializer, CourseSerializer, SubscriptionSerializer


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def get_permissions(self):
        if self.action in ['create', 'login']:
            permission_classes = [permissions.AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, email=email, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserProfileSerializer(user).data
            })
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'subscribe', 'unsubscribe']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk=None):
        course = self.get_object()
        subscription, created = Subscription.objects.get_or_create(
            student=request.user,
            course=course,
            defaults={'is_active': True}
        )
        return Response(
            {'status': 'subscribed'},
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def unsubscribe(self, request, pk=None):
        Subscription.objects.filter(
            student=request.user,
            course_id=pk
        ).delete()
        return Response({'status': 'unsubscribed'})


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'teacher':
            return Subscription.objects.filter(course__teachers=user)
        return Subscription.objects.filter(student=user)