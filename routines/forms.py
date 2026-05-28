from django import forms
from django.utils.html import format_html, mark_safe
from .models import RoutineTask, Category, MoodLog


class TimePickerWidget(forms.Widget):
    """Custom 12-hour AM/PM time picker widget - renders directly without template file."""
    
    def __init__(self, attrs=None):
        default_attrs = {'class': 'time-picker-input'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)
    
    def format_value(self, value):
        """Convert TimeField value to 12-hour format for display."""
        if not value:
            return {'hour': '12', 'minute': '00', 'period': 'AM'}
        
        if isinstance(value, str):
            # Parse "HH:MM" format
            time_parts = value.split(':')
            hour = int(time_parts[0])
            minute = time_parts[1]
        else:
            # TimeField object
            hour = value.hour
            minute = f"{value.minute:02d}"
        
        # Convert 24-hour to 12-hour format
        period = 'AM' if hour < 12 else 'PM'
        if hour == 0:
            hour_12 = 12
        elif hour > 12:
            hour_12 = hour - 12
        else:
            hour_12 = hour
        
        return {
            'hour': str(hour_12),
            'minute': str(minute),
            'period': period
        }
    
    def value_from_datadict(self, data, files, name):
        """Extract and convert 12-hour input to 24-hour format."""
        hour = data.get(f'{name}_hour', '12')
        minute = data.get(f'{name}_minute', '00')
        period = data.get(f'{name}_period', 'AM')
        
        try:
            hour_int = int(hour)
            minute_int = int(minute)
            
            # Convert 12-hour to 24-hour format
            if period == 'PM' and hour_int != 12:
                hour_int += 12
            elif period == 'AM' and hour_int == 12:
                hour_int = 0
            
            return f"{hour_int:02d}:{minute_int:02d}"
        except (ValueError, TypeError):
            return None
    
    def render(self, name, value, attrs=None, renderer=None):
        """Render the time picker HTML directly."""
        formatted_value = self.format_value(value)
        hour = formatted_value['hour']
        minute = formatted_value['minute']
        period = formatted_value['period']
        
        # Build hour options
        hour_options = ''.join([
            f'<option value="{h}" {"selected" if str(h) == hour else ""}>{h}</option>'
            for h in range(1, 13)
        ])
        
        # Build minute options (5-minute increments)
        minute_options = ''.join([
            f'<option value="{m}" {"selected" if str(m) == minute or f"{m:02d}" == minute else ""}>{m:02d}</option>'
            for m in range(0, 60, 5)
        ])
        
        # Build the HTML
        html = f'''
        <div class="time-picker-group">
            <select name="{name}_hour" class="time-picker-select time-picker-hour form-select form-control-lifeos" required>
                {hour_options}
            </select>
            
            <select name="{name}_minute" class="time-picker-select time-picker-minute form-select form-control-lifeos" required>
                {minute_options}
            </select>
            
            <div class="time-picker-period">
                <button type="button" class="period-btn am-btn {"active" if period == "AM" else ""}" 
                        data-period="AM" data-field="{name}">AM</button>
                <button type="button" class="period-btn pm-btn {"active" if period == "PM" else ""}" 
                        data-period="PM" data-field="{name}">PM</button>
                <input type="hidden" name="{name}_period" class="period-input" value="{period}">
            </div>
        </div>
        '''
        
        return mark_safe(html)


class RoutineTaskForm(forms.ModelForm):
    class Meta:
        model = RoutineTask
        fields = ['title', 'notes', 'category', 'date', 'start_time', 'end_time', 'priority', 'is_completed']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control form-control-lifeos', 'placeholder': 'e.g. Deep Work: Office'}),
            'notes': forms.Textarea(attrs={'class': 'form-control form-control-lifeos', 'rows': 2, 'placeholder': 'Optional notes...'}),
            'category': forms.Select(attrs={'class': 'form-select form-control-lifeos'}),
            'date': forms.DateInput(attrs={'class': 'form-control form-control-lifeos', 'type': 'date'}),
            'start_time': TimePickerWidget(attrs={'class': 'form-control-lifeos'}),
            'end_time': TimePickerWidget(attrs={'class': 'form-control-lifeos'}),
            'priority': forms.Select(attrs={'class': 'form-select form-control-lifeos'}),
            'is_completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class MoodLogForm(forms.ModelForm):
    class Meta:
        model = MoodLog
        fields = ['mood', 'energy', 'note']
        widgets = {
            'mood': forms.Select(attrs={'class': 'form-select form-control-lifeos'}),
            'energy': forms.Select(attrs={'class': 'form-select form-control-lifeos'}),
            'note': forms.TextInput(attrs={'class': 'form-control form-control-lifeos', 'placeholder': 'A short note...'}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-lifeos'}),
            'color': forms.Select(attrs={'class': 'form-select form-control-lifeos'}),
        }