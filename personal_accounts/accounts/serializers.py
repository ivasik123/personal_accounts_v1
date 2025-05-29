from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import UserProfile, Course, Subscription


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'email', 'username', 'contacts', 'notifications',
                  'role', 'last_activity', 'is_active', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True},
            'last_activity': {'read_only': True},
            'date_joined': {'read_only': True},
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        return super().create(validated_data)


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