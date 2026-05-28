"""
Health logging views.

The standalone Health Tracker page and the Analytics page have been removed.
Health data (water, sleep, meals, weight) is now surfaced directly on the Dashboard.
These views remain so the user can still *log* that data; after saving they return
to the Dashboard, which is the central life-overview page.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from decimal import Decimal

from .models import BodyMeasurement, WaterLog, Meal, SleepLog
from .forms import BodyMeasurementForm, WaterLogForm, MealForm, SleepLogForm


# ----- Body Measurement (weight / waist) -----

@login_required
def measurement_create(request):
    if request.method == 'POST':
        form = BodyMeasurementForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            existing = BodyMeasurement.objects.filter(user=request.user, date=obj.date).first()
            if existing:
                existing.weight_kg = obj.weight_kg
                existing.waist_cm = obj.waist_cm
                existing.notes = obj.notes
                existing.save()
            else:
                obj.save()
            messages.success(request, 'Measurement logged.')
            return redirect('dashboard:home')
    else:
        form = BodyMeasurementForm(initial={'date': timezone.now().date()})
    return render(request, 'health/measurement_form.html', {'form': form, 'title': 'Log Body Measurement'})


# ----- Water -----

@login_required
@require_POST
def water_add(request):
    """Quick add — adds a default cup OR custom amount. Returns JSON for the dashboard widget."""
    amount = request.POST.get('amount', '0.25')
    try:
        amount = Decimal(amount)
    except Exception:
        amount = Decimal('0.25')
    WaterLog.objects.create(user=request.user, amount_liters=amount)
    today = timezone.now().date()
    total = WaterLog.objects.filter(user=request.user, date=today).aggregate(t=Sum('amount_liters'))['t'] or Decimal('0.00')
    target = request.user.water_target_liters or Decimal('2.5')
    percent = min(int((total / target) * 100), 100) if target else 0
    return JsonResponse({'total': float(total), 'percent': percent})


@login_required
def water_log_form(request):
    if request.method == 'POST':
        form = WaterLogForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            messages.success(request, 'Water logged.')
            return redirect('dashboard:home')
    else:
        form = WaterLogForm()
    return render(request, 'health/water_form.html', {'form': form, 'title': 'Log Water'})


# ----- Meals -----

@login_required
def meal_create(request):
    if request.method == 'POST':
        form = MealForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            messages.success(request, 'Meal logged.')
            return redirect('dashboard:home')
    else:
        form = MealForm(initial={'date': timezone.now().date()})
    return render(request, 'health/meal_form.html', {'form': form, 'title': 'Log Meal'})


# ----- Sleep -----

@login_required
def sleep_create(request):
    if request.method == 'POST':
        form = SleepLogForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            existing = SleepLog.objects.filter(user=request.user, date=obj.date).first()
            if existing:
                existing.hours = obj.hours
                existing.quality = obj.quality
                existing.consistency = obj.consistency
                existing.notes = obj.notes
                existing.save()
            else:
                obj.save()
            messages.success(request, 'Sleep logged.')
            return redirect('dashboard:home')
    else:
        form = SleepLogForm(initial={'date': timezone.now().date()})
    return render(request, 'health/sleep_form.html', {'form': form, 'title': 'Log Sleep'})
