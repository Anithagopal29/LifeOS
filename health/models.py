from django.db import models
from django.conf import settings
from django.utils import timezone


class BodyMeasurement(models.Model):
    """Weight + waist tracking."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='measurements')
    date = models.DateField(default=timezone.now)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    waist_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    notes = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user.username} - {self.date}"


class WaterLog(models.Model):
    """Individual water intake entry (each cup/glass) - sum for daily."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='water_logs')
    date = models.DateField(default=timezone.now)
    amount_liters = models.DecimalField(max_digits=4, decimal_places=2)  # liters added
    logged_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-logged_at']

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.amount_liters}L"


class Meal(models.Model):
    """Meal log - breakfast/lunch/dinner/snack."""
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='meals')
    date = models.DateField(default=timezone.now)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    description = models.CharField(max_length=200, blank=True)
    calories = models.IntegerField(null=True, blank=True)
    logged_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date', 'meal_type']

    def __str__(self):
        return f"{self.get_meal_type_display()} - {self.date}"


class SleepLog(models.Model):
    """Sleep tracking."""
    CONSISTENCY_CHOICES = [
        ('low', 'Low Consistency'),
        ('medium', 'Medium Consistency'),
        ('high', 'High Consistency'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sleep_logs')
    date = models.DateField(default=timezone.now)
    hours = models.DecimalField(max_digits=4, decimal_places=2)
    quality = models.IntegerField(default=3, help_text='1-5 scale')
    consistency = models.CharField(max_length=10, choices=CONSISTENCY_CHOICES, default='high')
    notes = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.hours}h"

    @property
    def display_time(self):
        """Returns hours and minutes display like '7h 20m'."""
        h = int(self.hours)
        m = int((float(self.hours) - h) * 60)
        return f"{h}h {m:02d}m"


class Workout(models.Model):
    """Workout entries."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='workouts')
    date = models.DateField(default=timezone.now)
    duration_minutes = models.IntegerField(default=0)
    activity = models.CharField(max_length=100, default='General workout')
    intensity = models.CharField(max_length=20, default='moderate')
    calories_burned = models.IntegerField(null=True, blank=True)
    notes = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.activity} - {self.duration_minutes}m on {self.date}"
