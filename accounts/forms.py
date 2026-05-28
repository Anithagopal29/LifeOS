from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class RegisterForm(UserCreationForm):
    full_name = forms.CharField(max_length=120, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'full_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, f in self.fields.items():
            f.widget.attrs['class'] = 'form-control form-control-lg'
            f.widget.attrs['placeholder'] = f.label


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, f in self.fields.items():
            f.widget.attrs['class'] = 'form-control form-control-lg'
            f.widget.attrs['placeholder'] = f.label


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'full_name', 'bio', 'avatar',
            'monthly_budget', 'sleep_target_hours', 'water_target_liters',
            'routine_target_percent', 'health_status', 'daily_intention',
            'notifications_enabled', 'reminders_enabled',
        )
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.TextInput(attrs={'class': 'form-control'}),
            'monthly_budget': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'sleep_target_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'water_target_liters': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'routine_target_percent': forms.NumberInput(attrs={'class': 'form-control'}),
            'health_status': forms.TextInput(attrs={'class': 'form-control'}),
            'daily_intention': forms.TextInput(attrs={'class': 'form-control'}),
        }
