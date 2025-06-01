from .models import Course, Subscription


from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'email', 'username', 'password', 'contacts', 'notifications',
                  'role', 'last_activity', 'is_active', 'date_joined']
        extra_kwargs = {
            'last_activity': {'read_only': True},
            'date_joined': {'read_only': True},
            'is_active': {'read_only': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = UserProfile.objects.create(
            **validated_data,
            password=make_password(password)
        )
        return user


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'start_date', 'end_date', 'is_active']


class SubscriptionSerializer(serializers.ModelSerializer):
    student = UserProfileSerializer(read_only=True)
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = ['id', 'student', 'course', 'date_subscribed', 'is_active']