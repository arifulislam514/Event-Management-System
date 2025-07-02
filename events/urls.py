from django.urls import path
from events.views import create_event, create_category, update_event, delete_event
from events import views

urlpatterns = [
    path('create_event/', create_event, name="create_event"),
    path('delete_event/<int:id>', delete_event, name="delete_event"),
    path('update_event/<int:id>/', update_event, name="update_event"),
    path('create_category/', create_category, name="create_category"),
    path('manager_dashboard/', views.view_event_list, name="manager_dashboard")
]