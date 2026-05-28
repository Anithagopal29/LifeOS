from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta, datetime, time
from decimal import Decimal
from calendar import monthrange

from routines.models import RoutineTask
from expenses.models import Transaction
from health.models import WaterLog, Meal, SleepLog, BodyMeasurement


@login_required
def home(request):
    """Dashboard - Image 1."""
    user = request.user
    profile = user  # custom User holds all goals/prefs
    today = timezone.now().date()
    now = timezone.now().time()
    greeting = compute_greeting()

    # Today's tasks (routine tasks)
    today_tasks = RoutineTask.objects.filter(user=user, date=today)
    total_tasks = today_tasks.count()
    completed_tasks = today_tasks.filter(is_completed=True).count()
    task_percent = int((completed_tasks / total_tasks) * 100) if total_tasks else 0
    remaining_tasks = total_tasks - completed_tasks

    # Study time today (sum of routine tasks with category=Study)
    study_minutes = 0
    study_tasks = today_tasks.filter(category__name__iexact='Study', is_completed=True)
    for t in study_tasks:
        if t.end_time:
            start = datetime.combine(today, t.start_time)
            end = datetime.combine(today, t.end_time)
            study_minutes += int((end - start).total_seconds() / 60)
    study_hours = round(study_minutes / 60, 1)

    # Compare to yesterday
    yesterday = today - timedelta(days=1)
    y_study_minutes = 0
    for t in RoutineTask.objects.filter(user=user, date=yesterday, category__name__iexact='Study', is_completed=True):
        if t.end_time:
            start = datetime.combine(yesterday, t.start_time)
            end = datetime.combine(yesterday, t.end_time)
            y_study_minutes += int((end - start).total_seconds() / 60)
    study_change_percent = 0
    if y_study_minutes > 0:
        study_change_percent = int(((study_minutes - y_study_minutes) / y_study_minutes) * 100)

    # Spending today (sum of expense transactions for today)
    today_spending = Transaction.objects.filter(
        user=user, transaction_type='expense', date=today
    ).aggregate(t=Sum('amount'))['t'] or Decimal('0.00')

    # Calculate daily spending budget = monthly / days in month
    days_in_month = monthrange(today.year, today.month)[1]
    daily_budget = (profile.monthly_budget or Decimal('0')) / days_in_month
    within_budget = today_spending <= daily_budget

    # Sleep last night
    sleep_log = SleepLog.objects.filter(user=user, date=today).first()
    if not sleep_log:
        sleep_log = SleepLog.objects.filter(user=user, date=yesterday).first()

    # Meals today
    meals_today = Meal.objects.filter(user=user, date=today).count()
    meals_goal = 3

    # Water intake today
    todays_water = WaterLog.objects.filter(user=user, date=today).aggregate(t=Sum('amount_liters'))['t'] or Decimal('0.00')
    water_target = profile.water_target_liters or Decimal('2.5')
    water_percent = min(int((todays_water / water_target) * 100), 100) if water_target else 0

    # Weight summary (latest measurement + change vs previous)
    latest_measurement = BodyMeasurement.objects.filter(user=user, weight_kg__isnull=False).first()
    prev_measurement = (BodyMeasurement.objects
                        .filter(user=user, weight_kg__isnull=False)
                        .exclude(pk=latest_measurement.pk if latest_measurement else 0)
                        .first())
    weight_change = None
    if latest_measurement and prev_measurement:
        weight_change = latest_measurement.weight_kg - prev_measurement.weight_kg

    # Weekly focus chart - completion % per day (last 7 days)
    weekly_focus = []
    day_initials = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
    monday = today - timedelta(days=today.weekday())
    for i in range(7):
        d = monday + timedelta(days=i)
        day_tasks = RoutineTask.objects.filter(user=user, date=d)
        if day_tasks.exists():
            done = day_tasks.filter(is_completed=True).count()
            total = day_tasks.count()
            pct = int((done / total) * 100)
        else:
            pct = 0
        weekly_focus.append({'day': day_initials[i], 'date': d, 'percent': pct, 'is_today': d == today})

    # Peak focus time
    peak_focus_label = "10:00 AM"

    # Upcoming today (next routine items)
    upcoming = today_tasks.filter(is_completed=False, start_time__gte=now).order_by('start_time')[:5]
    if not upcoming.exists():
        # Show next 2 days of future tasks
        upcoming = RoutineTask.objects.filter(user=user, date__gte=today, is_completed=False).order_by('date', 'start_time')[:5]

    context = {
        'greeting': greeting,
        'profile': profile,
        # Today's tasks card
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'task_percent': task_percent,
        'remaining_tasks': remaining_tasks,
        # Study + spending
        'study_hours': study_hours,
        'study_change_percent': study_change_percent,
        'today_spending': today_spending,
        'within_budget': within_budget,
        'daily_budget': daily_budget,
        # Wellness
        'sleep_log': sleep_log,
        'meals_today': meals_today,
        'meals_goal': meals_goal,
        'todays_water': todays_water,
        'water_target': water_target,
        'water_percent': water_percent,
        # Weight summary
        'latest_measurement': latest_measurement,
        'weight_change': weight_change,
        # Targets for widget labels
        'sleep_target': profile.sleep_target_hours,
        # Weekly focus
        'weekly_focus': weekly_focus,
        'peak_focus_label': peak_focus_label,
        # Upcoming
        'upcoming': upcoming,
    }
    return render(request, 'dashboard/home.html', context)


def compute_greeting():
    """Returns Good morning / afternoon / evening based on server time."""
    hour = timezone.localtime().hour
    if hour < 12:
        return "Good morning"
    elif hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"
