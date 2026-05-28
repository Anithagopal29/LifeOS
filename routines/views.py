from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import datetime

from .models import RoutineTask, Category, MoodLog
from .forms import RoutineTaskForm, MoodLogForm, CategoryForm


@login_required
def routine_list(request):
    """Daily Routine - the timeline view (Image 3)."""
    date_str = request.GET.get('date')
    if date_str:
        try:
            current_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            current_date = timezone.now().date()
    else:
        current_date = timezone.now().date()

    tasks = RoutineTask.objects.filter(user=request.user, date=current_date).order_by('start_time')

    total = tasks.count()
    completed = tasks.filter(is_completed=True).count()
    progress_percent = int((completed / total) * 100) if total else 0

    # Today's mood log
    mood_log, _ = MoodLog.objects.get_or_create(
        user=request.user,
        date=current_date,
        defaults={'mood': 'happy', 'energy': 'mid'},
    )

    if progress_percent >= 90:
        status_label = 'Excellent'
    elif progress_percent >= 70:
        status_label = 'On track'
    elif progress_percent >= 40:
        status_label = 'Almost there'
    else:
        status_label = 'Just started'

    context = {
        'tasks': tasks,
        'current_date': current_date,
        'progress_percent': progress_percent,
        'completed': completed,
        'total': total,
        'status_label': status_label,
        'mood_log': mood_log,
        'mood_choices': MoodLog.MOOD_CHOICES,
        'energy_choices': MoodLog.ENERGY_CHOICES,
    }
    return render(request, 'routines/routine_list.html', context)


@login_required
def routine_create(request):
    if request.method == 'POST':
        form = RoutineTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, 'Routine task added.')
            return redirect('routines:list')
    else:
        initial = {'date': timezone.now().date()}
        form = RoutineTaskForm(initial=initial)
    return render(request, 'routines/routine_form.html', {'form': form, 'title': 'Add Routine Task'})


@login_required
def routine_edit(request, pk):
    task = get_object_or_404(RoutineTask, pk=pk, user=request.user)
    if request.method == 'POST':
        form = RoutineTaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Routine task updated.')
            return redirect('routines:list')
    else:
        form = RoutineTaskForm(instance=task)
    return render(request, 'routines/routine_form.html', {'form': form, 'title': 'Edit Routine Task'})


@login_required
def routine_delete(request, pk):
    task = get_object_or_404(RoutineTask, pk=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Routine task deleted.')
        return redirect('routines:list')
    return render(request, 'routines/routine_confirm_delete.html', {'task': task})


@login_required
@require_POST
def toggle_complete(request, pk):
    """AJAX toggle of completion status."""
    task = get_object_or_404(RoutineTask, pk=pk, user=request.user)
    task.is_completed = not task.is_completed
    task.save(update_fields=['is_completed'])
    return JsonResponse({'is_completed': task.is_completed})


@login_required
@require_POST
def update_mood(request):
    """AJAX update for today's mood/energy."""
    today = timezone.now().date()
    mood_log, _ = MoodLog.objects.get_or_create(user=request.user, date=today)
    mood = request.POST.get('mood')
    energy = request.POST.get('energy')
    if mood:
        mood_log.mood = mood
    if energy:
        mood_log.energy = energy
    mood_log.save()
    return JsonResponse({'mood': mood_log.mood, 'energy': mood_log.energy})


@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'routines/category_list.html', {'categories': categories})


@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added.')
            return redirect('routines:categories')
    else:
        form = CategoryForm()
    return render(request, 'routines/category_form.html', {'form': form})
