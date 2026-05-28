from django.db import models
from django.conf import settings
from django.utils import timezone


class Category(models.Model):
    """Routine task category - Personal, Health, Work, Study, Home, Reading, etc."""
    CATEGORY_COLORS = [
        ('beige', 'Beige'),
        ('green', 'Green'),
        ('brown', 'Brown'),
        ('cream', 'Cream'),
        ('sage', 'Sage'),
    ]
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=20, choices=CATEGORY_COLORS, default='beige')

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class RoutineTask(models.Model):
    """A timeline item / routine task."""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='routine_tasks')
    title = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(default=timezone.now)
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    is_completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.title} @ {self.start_time}"

    @property
    def time_range(self):
        if self.start_time and self.end_time:
            start = self.start_time.strftime("%I:%M %p")
            end = self.end_time.strftime("%I:%M %p")
            return f"{start} - {end}"

        elif self.start_time:
            return self.start_time.strftime("%I:%M %p")

        return "No Time Set"


class MoodLog(models.Model):
    """Daily mood + energy log."""
    MOOD_CHOICES = [
        ('calm', '😌 Calm'),
        ('happy', '😊 Happy'),
        ('focused', '🧠 Focused'),
        ('tired', '😪 Tired'),
    ]
    ENERGY_CHOICES = [
        ('low', 'Low'),
        ('mid', 'Mid'),
        ('high', 'High'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mood_logs')
    date = models.DateField(default=timezone.now)
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES, default='happy')
    energy = models.CharField(max_length=10, choices=ENERGY_CHOICES, default='mid')
    note = models.CharField(max_length=200, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.mood}"
