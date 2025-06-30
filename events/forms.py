from django import forms
from events.models import Event, Category, Participant


class EventModelForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'category', 'participants', 'date', 'time']
        
    


