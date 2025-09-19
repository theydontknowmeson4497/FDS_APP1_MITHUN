from django.contrib import admin
from .models import Habit

@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'sleep_hours', 'water_intake', 'steps', 'exercise_minutes']
    list_filter = ['date', 'user']
    search_fields = ['user__username']
    ordering = ['-date']
