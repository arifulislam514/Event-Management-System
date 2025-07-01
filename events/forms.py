from django import forms
from events.models import Event, Category, Participant, Location


class EventModelForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'category', 'date', 'time', 'description']
        
        
class CategoryModelForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        
        
class LocationModelForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['country', 'city']
    

