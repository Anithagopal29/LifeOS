from django.contrib import admin
from .models import RoutineTask, Category, MoodLog


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')


@admin.register(RoutineTask)
class RoutineTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'date', 'start_time', 'category', 'priority', 'is_completed')
    list_filter = ('is_completed', 'priority', 'category', 'date')
    search_fields = ('title', 'notes')


@admin.register(MoodLog)
class MoodLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'mood', 'energy')
    list_filter = ('mood', 'energy')
