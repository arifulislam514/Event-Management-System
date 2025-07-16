from django.urls import path
from users.views import sign_up, login

urlpatterns = [
    # path('create_event/', create_event, name="create_event"),
    path('sign-up/', sign_up, name="sign-up"),
    path('login/', login, name="login"),
    
]