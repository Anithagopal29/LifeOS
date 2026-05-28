from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from decimal import Decimal
from datetime import date, timedelta

from .forms import RegisterForm, LoginForm, ProfileForm
from routines.models import RoutineTask
from expenses.models import Transaction


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.full_name = form.cleaned_data['full_name']
            user.email = form.cleaned_data['email']
            user.save()
            login(request, user)
            messages.success(request, 'Welcome to LifeOS!')
            return redirect('dashboard:home')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


@login_required
def profile_view(request):
    user = request.user
    today = date.today()
    month_start = today.replace(day=1)

    # Stats
    completed_tasks = RoutineTask.objects.filter(user=user, is_completed=True).count()
    total_tasks = RoutineTask.objects.filter(user=user).count() or 1
    routine_percent = round((completed_tasks / total_tasks) * 100)

    from django.db.models import Sum
    month_expenses = Transaction.objects.filter(
        user=user, transaction_type='expense', date__gte=month_start
    ).aggregate(t=Sum('amount'))['t'] or Decimal('0')

    # Streak: count consecutive days with any completed task
    streak = _compute_streak(user)

    # Consistency rating out of 5 (based on routine %)
    consistency = round((routine_percent / 100) * 5, 1)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=user)

    return render(request, 'accounts/profile.html', {
        'form': form,
        'routine_percent': routine_percent,
        'month_expenses': month_expenses,
        'streak': streak,
        'consistency': consistency,
    })


def _compute_streak(user):
    streak = 0
    cur = date.today()
    while True:
        if RoutineTask.objects.filter(user=user, date=cur, is_completed=True).exists():
            streak += 1
            cur -= timedelta(days=1)
        else:
            break
        if streak > 365:
            break
    return streak


@login_required
@require_POST
def toggle_dark_mode(request):
    user = request.user
    user.dark_mode = not user.dark_mode
    user.save(update_fields=['dark_mode'])
    return JsonResponse({'dark_mode': user.dark_mode})
