from django.urls import path
from . import views

app_name = 'health'

# Health now lives inside the Dashboard. These routes only handle *logging*
# of health data; the standalone tracker and analytics pages were removed.
urlpatterns = [
    path('measurement/add/', views.measurement_create, name='measurement_create'),
    path('water/add/', views.water_add, name='water_add'),
    path('water/log/', views.water_log_form, name='water_log_form'),
    path('meal/add/', views.meal_create, name='meal_create'),
    path('sleep/add/', views.sleep_create, name='sleep_create'),
]
