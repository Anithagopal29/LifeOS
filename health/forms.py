from django import forms
from .models import BodyMeasurement, WaterLog, Meal, SleepLog, Workout


class BodyMeasurementForm(forms.ModelForm):
    class Meta:
        model = BodyMeasurement
        fields = ['date', 'weight_kg', 'waist_cm', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control form-control-lifeos', 'type': 'date'}),
            'weight_kg': forms.NumberInput(attrs={'class': 'form-control form-control-lifeos', 'step': '0.1'}),
            'waist_cm': forms.NumberInput(attrs={'class': 'form-control form-control-lifeos', 'step': '0.1'}),
            'notes': forms.TextInput(attrs={'class': 'form-control form-control-lifeos'}),
        }


class WaterLogForm(forms.ModelForm):
    class Meta:
        model = WaterLog
        fields = ['amount_liters']
        widgets = {
            'amount_liters': forms.NumberInput(attrs={'class': 'form-control form-control-lifeos', 'step': '0.1', 'placeholder': 'Liters (e.g. 0.25)'}),
        }


class MealForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ['date', 'meal_type', 'description', 'calories']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control form-control-lifeos', 'type': 'date'}),
            'meal_type': forms.Select(attrs={'class': 'form-select form-control-lifeos'}),
            'description': forms.TextInput(attrs={'class': 'form-control form-control-lifeos'}),
            'calories': forms.NumberInput(attrs={'class': 'form-control form-control-lifeos'}),
        }


class SleepLogForm(forms.ModelForm):
    class Meta:
        model = SleepLog
        fields = ['date', 'hours', 'quality', 'consistency', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control form-control-lifeos', 'type': 'date'}),
            'hours': forms.NumberInput(attrs={'class': 'form-control form-control-lifeos', 'step': '0.25'}),
            'quality': forms.NumberInput(attrs={'class': 'form-control form-control-lifeos', 'min': 1, 'max': 5}),
            'consistency': forms.Select(attrs={'class': 'form-select form-control-lifeos'}),
            'notes': forms.TextInput(attrs={'class': 'form-control form-control-lifeos'}),
        }


class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ['date', 'activity', 'duration_minutes', 'intensity', 'calories_burned', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control form-control-lifeos', 'type': 'date'}),
            'activity': forms.TextInput(attrs={'class': 'form-control form-control-lifeos'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control form-control-lifeos'}),
            'intensity': forms.TextInput(attrs={'class': 'form-control form-control-lifeos'}),
            'calories_burned': forms.NumberInput(attrs={'class': 'form-control form-control-lifeos'}),
            'notes': forms.TextInput(attrs={'class': 'form-control form-control-lifeos'}),
        }
