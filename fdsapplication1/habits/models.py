from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    sleep_hours = models.FloatField(help_text="Hours of sleep")
    water_intake = models.IntegerField(help_text="Number of glasses of water")
    steps = models.IntegerField(help_text="Number of steps walked")
    exercise_minutes = models.IntegerField(help_text="Minutes of exercise")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.date}"
