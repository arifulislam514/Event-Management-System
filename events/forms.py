from django import forms
from django.forms import TimeInput
from events.models import Event, Category, Location
from django.contrib.auth.models import User


class StyledFormMixin:
    """ Mixing to apply style to form field"""

    def __init__(self, *arg, **kwarg):
        super().__init__(*arg, **kwarg)
        self.apply_styled_widgets()

    default_classes = "border-2 border-gray-300 w-full p-3 rounded-lg shadow-sm focus:outline-none focus:border-rose-500 focus:ring-rose-500"

    def apply_styled_widgets(self):
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({
                    'class': self.default_classes,
                    'placeholder': f"Enter {field.label.lower()}"
                })
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    'class': f"{self.default_classes} resize-none",
                    'placeholder':  f"Enter {field.label.lower()}",
                    'rows': 5
                })
            elif isinstance(field.widget, forms.SelectDateWidget):
                print("Inside Date")
                field.widget.attrs.update({
                    "class": "border-2 border-gray-300 p-3 rounded-lg shadow-sm focus:outline-none focus:border-rose-500 focus:ring-rose-500"
                })
            elif isinstance(field.widget, forms.CheckboxSelectMultiple):
                print("Inside checkbox")
                field.widget.attrs.update({
                    'class': "space-y-2"
                })
            else:
                print("Inside else")
                field.widget.attrs.update({
                    'class': self.default_classes
                })



class EventModelForm(StyledFormMixin,forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'category', 'date', 'time', 'description']
        widgets = {
            'date': forms.SelectDateWidget,
            'time': TimeInput(format='%H:%M', attrs={'type': 'time'}),
        }
        
    """ Widget using mixins """

    def __init__(self, *arg, **kwarg):
        super().__init__(*arg, **kwarg)
        self.apply_styled_widgets()
        
        
# class ParticipantModelForm(StyledFormMixin,forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ['name', 'email']
        
#     def __init__(self, *arg, **kwarg):
#         super().__init__(*arg, **kwarg)
#         self.apply_styled_widgets()
        
        
class CategoryModelForm(StyledFormMixin,forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        
    """ Widget using mixins """

    def __init__(self, *arg, **kwarg):
        super().__init__(*arg, **kwarg)
        self.apply_styled_widgets()


class LocationModelForm(StyledFormMixin,forms.ModelForm):
    class Meta:
        model = Location
        fields = ['country', 'city']

    def __init__(self, *args, **kwargs):
        super(LocationModelForm, self).__init__(*args, **kwargs)
        self.apply_styled_widgets()
        self.fields['country'].required = False          
        self.fields['city'].required = False  
    