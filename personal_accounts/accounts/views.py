from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from .forms import StudentRegistrationForm

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
# views.py
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