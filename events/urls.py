from django.urls import path
from events.views import create_event, create_category, update_event, delete_event,add_participant
from events import views

urlpatterns = [
    path('create_event/', create_event, name="create_event"),
    path('delete_event/<int:id>', delete_event, name="delete_event"),
    path('update_event/<int:id>/', update_event, name="update_event"),
    path('create_category/', create_category, name="create_category"),
    path('add_participant/', add_participant, name="add_participant"),
    path('manager_dashboard/', views.manager_dashboard, name="manager_dashboard"),
    path('home/', views.home, name="home"),
    path('events/', views.events, name="events"),
    path('event_detaile/<int:id>', views.event_detaile, name="event_detaile"),
]