from django.urls import path
from events.views import create_event, create_category, update_event, delete_event,update_category,delete_category
from events import views

urlpatterns = [
    path('create_event/', create_event, name="create_event"),
    path('delete_event/<int:id>', delete_event, name="delete_event"),
    path('update_event/<int:id>/', update_event, name="update_event"),
    path('create_category/', create_category, name="create_category"),
    path('update_category/<int:id>/', update_category, name="update_category"),
    path('delete_category/<int:id>', delete_category, name="delete_category"),
    # path('add_participant/', views.add_participant, name="add_participant"),
    # path('update_participant/<int:id>', views.update_participant, name="update_participant"),
    path('delete_participant/<int:id>', views.delete_participant, name="delete_participant"),
    path('home/', views.home, name="home"),
    path('events/', views.events, name="events"),
    path('event_detaile/<int:id>', views.event_detaile, name="event_detaile"),
    path('dashboard', views.dashboard, name="dashboard"),
    path('manager_dashboard/', views.manager_dashboard, name="manager_dashboard"),
    path('user-dashboard/', views.user_dashboard, name="user-dashboard"),
    path('rsvp-event/<int:id>/', views.rsvp_event, name="rsvp-event"),
]