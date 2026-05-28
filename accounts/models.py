from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user that also stores per-user goals & preferences (Profile screen)."""
    full_name = models.CharField(max_length=120, blank=True)
    bio = models.CharField(max_length=200, blank=True, default="Living intentionally, one day at a time.")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    # Personal goals (Profile screen)
    monthly_budget = models.DecimalField(max_digits=10, decimal_places=2, default=2500)
    sleep_target_hours = models.DecimalField(max_digits=4, decimal_places=2, default=8.0)
    water_target_liters = models.DecimalField(max_digits=4, decimal_places=2, default=2.5)
    routine_target_percent = models.PositiveIntegerField(default=90)
    health_status = models.CharField(max_length=20, default='Active')
    daily_intention = models.CharField(
        max_length=200,
        default='The secret of your future is hidden in your daily routine.'
    )

    # Preferences
    dark_mode = models.BooleanField(default=False)
    notifications_enabled = models.BooleanField(default=True)
    reminders_enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.full_name or self.username

    @property
    def display_name(self):
        return self.full_name.split(' ')[0] if self.full_name else self.username
