from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Sum
from django.utils import timezone
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO
import base64
import os
from django.conf import settings

from .models import Habit
from .forms import HabitForm, CustomUserCreationForm


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def log_habit(request):
    if request.method == 'POST':
        form = HabitForm(request.POST)
        if form.is_valid():
            habit = form.save(commit=False)
            habit.user = request.user
            try:
                habit.save()
                messages.success(request, 'Habit logged successfully!')
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, 'A habit entry for this date already exists. Please update the existing entry.')
    else:
        form = HabitForm()
    return render(request, 'habits/log_habit.html', {'form': form})


@login_required
def dashboard(request):
    # Get user's habits
    habits = Habit.objects.filter(user=request.user).order_by('-date')
    
    # Calculate summary statistics
    if habits.exists():
        # Overall averages
        avg_sleep = habits.aggregate(Avg('sleep_hours'))['sleep_hours__avg']
        avg_water = habits.aggregate(Avg('water_intake'))['water_intake__avg']
        avg_steps = habits.aggregate(Avg('steps'))['steps__avg']
        avg_exercise = habits.aggregate(Avg('exercise_minutes'))['exercise_minutes__avg']
        
        # This week's data
        week_ago = timezone.now().date() - timedelta(days=7)
        this_week_habits = habits.filter(date__gte=week_ago)
        
        total_steps_week = this_week_habits.aggregate(Sum('steps'))['steps__sum'] or 0
        total_exercise_week = this_week_habits.aggregate(Sum('exercise_minutes'))['exercise_minutes__sum'] or 0
        
        # Generate matplotlib chart
        chart_url = generate_sleep_chart(habits)
        
        context = {
            'habits': habits[:10],  # Show last 10 entries
            'avg_sleep': round(avg_sleep, 1) if avg_sleep else 0,
            'avg_water': round(avg_water, 1) if avg_water else 0,
            'avg_steps': round(avg_steps, 0) if avg_steps else 0,
            'avg_exercise': round(avg_exercise, 1) if avg_exercise else 0,
            'total_steps_week': total_steps_week,
            'total_exercise_week': total_exercise_week,
            'chart_url': chart_url,
        }
    else:
        context = {
            'habits': habits,
            'avg_sleep': 0,
            'avg_water': 0,
            'avg_steps': 0,
            'avg_exercise': 0,
            'total_steps_week': 0,
            'total_exercise_week': 0,
            'chart_url': None,
        }
    
    return render(request, 'habits/dashboard.html', context)


def generate_sleep_chart(habits):
    """Generate a matplotlib chart showing sleep trends over time"""
    if not habits.exists():
        return None
    
    # Get last 14 days of data
    recent_habits = habits[:14]
    dates = [habit.date for habit in reversed(recent_habits)]
    sleep_hours = [habit.sleep_hours for habit in reversed(recent_habits)]
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(dates, sleep_hours, marker='o', linewidth=2, markersize=6)
    plt.title('Sleep Hours Trend (Last 14 Days)', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Sleep Hours', fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Format x-axis
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=2))
    plt.xticks(rotation=45)
    
    # Set y-axis limits
    plt.ylim(0, max(sleep_hours) + 1 if sleep_hours else 10)
    
    # Tight layout to prevent label cutoff
    plt.tight_layout()
    
    # Save to BytesIO
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    
    # Encode to base64
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()  # Important: close the figure to free memory
    
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    
    return graphic


def home(request):
    """Home page view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'habits/home.html')
