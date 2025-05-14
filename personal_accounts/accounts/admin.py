from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from .models import UserProfile, Course, Subscription


class UserProfileAdmin(UserAdmin):
    list_display = ('email', 'username', 'role', 'is_staff', 'last_activity', 'last_admin_access')
    search_fields = ('email', 'username')
    list_filter = ('role', 'is_active', 'is_staff', 'last_activity')
    readonly_fields = ('last_activity', 'last_admin_access', 'date_joined')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'contacts', 'notifications')}),
        ('Activity', {'fields': ('last_activity', 'last_admin_access', 'date_joined')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'username', 'contacts', 'notifications'),
        }),
    )

    ordering = ('-last_activity',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(is_staff=False)


class SubscriptionInline(admin.TabularInline):
    model = Subscription
    extra = 1
    raw_id_fields = ('student',)
    autocomplete_fields = ['student']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'is_active', 'teacher_list')
    list_filter = ('is_active', 'start_date')
    filter_horizontal = ('teachers',)
    inlines = [SubscriptionInline]
    search_fields = ('title', 'teachers__email')

    def teacher_list(self, obj):
        return ", ".join([t.username for t in obj.teachers.all()])

    teacher_list.short_description = 'Teachers'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'date_subscribed', 'is_active')
    list_filter = ('is_active', 'course')
    search_fields = ('student__email', 'course__title')
    date_hierarchy = 'date_subscribed'
    list_select_related = ('student', 'course')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('student', 'course')


admin.site.register(UserProfile, UserProfileAdmin)


def deactivate_inactive_users(modeladmin, request, queryset):
    one_year_ago = timezone.now() - timezone.timedelta(days=365)
    queryset.filter(
        last_activity__lte=one_year_ago,
        is_active=True
    ).update(is_active=False)


deactivate_inactive_users.short_description = "Deactivate users inactive for 1 year"

UserProfileAdmin.actions = [deactivate_inactive_users]