from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile


class StudentRegistrationForm(UserCreationForm):
    full_name = forms.CharField(
        label='ФИО',
        max_length=150,
        required=True
    )
    contacts = forms.CharField(
        label='Контактные данные',
        widget=forms.Textarea,
        required=False
    )


    class Meta:
        model = UserProfile
        fields = ('email', 'full_name', 'contacts', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['full_name']
        user.contacts = self.cleaned_data['contacts']
        user.role = 'student'

        if commit:
            user.save()
        return user