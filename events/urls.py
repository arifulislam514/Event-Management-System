from django.urls import path
from events.views import create_event, create_category

urlpatterns = [
    path('create_event/', create_event, name="create_event"),
    path('create_category/', create_category, name="create_category")
]