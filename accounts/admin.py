from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'full_name', 'email', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {'fields': ('full_name', 'bio', 'avatar', 'daily_intention')}),
        ('Goals', {'fields': ('monthly_budget', 'sleep_target_hours', 'water_target_liters',
                              'routine_target_percent', 'health_status')}),
        ('Preferences', {'fields': ('dark_mode', 'notifications_enabled', 'reminders_enabled')}),
    )
