from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Habit


class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ['date', 'sleep_hours', 'water_intake', 'steps', 'exercise_minutes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'sleep_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '24'}),
            'water_intake': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'steps': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'exercise_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }
        labels = {
            'sleep_hours': 'Sleep Hours',
            'water_intake': 'Water Intake (glasses)',
            'steps': 'Steps Walked',
            'exercise_minutes': 'Exercise Minutes',
        }


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user