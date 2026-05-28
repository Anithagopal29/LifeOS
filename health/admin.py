from django.contrib import admin
from .models import BodyMeasurement, WaterLog, Meal, SleepLog, Workout


admin.site.register(BodyMeasurement)
admin.site.register(WaterLog)
admin.site.register(Meal)
admin.site.register(SleepLog)
admin.site.register(Workout)
