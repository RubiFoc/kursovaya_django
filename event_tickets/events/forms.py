from django import forms
from django.core.exceptions import ValidationError

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm

from events.models import User, Event, EventCreation


class AddEventForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cat'].empty_label = "Категория не выбрана"

        # Устанавливаем начальное значение для поля time_start при редактировании
        if 'instance' in kwargs and kwargs['instance'] is not None:
            instance = kwargs['instance']
            if hasattr(instance, 'time_start'):
                self.initial['time_start'] = instance.time_start.strftime('%Y-%m-%dT%H:%M')

        for field_name, field in self.fields.items():
            if not kwargs.get('instance'):
                field.required = True
            else:
                field.required = False

    class Meta:
        model = Event
        fields = ['title', 'slug', 'content', 'photo', 'cat', 'count_tickets', 'price', 'time_start']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'content': forms.Textarea(attrs={'cols': 60, 'rows': 10}),
            'time_start': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) > 200:
            raise ValidationError('Длина превышает 200 символов')
        return title


class PurchaseForm(forms.Form):
    quantity = forms.IntegerField(min_value=1)

