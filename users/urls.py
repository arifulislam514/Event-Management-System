from django.urls import path
from users.views import sign_up, sign_in, activate_user, create_group, sign_out, group_list, update_group, admin_dashboard, no_permission

urlpatterns = [
    # path('create_event/', create_event, name="create_event"),
    path('sign-up/', sign_up, name="sign-up"),
    path('login/', sign_in, name="login"),
    path('logout/', sign_out, name="logout"),
    path('activate/<int:user_id>/<str:token>/', activate_user),
    path('create-group/', create_group, name="create-group"),
    path('update-group/<int:id>/', update_group, name="update-group"),
    path('group-list/', group_list, name="group-list"),
    path('admin-dashboard/', admin_dashboard, name="admin-dashboard"),
    path('no-permission/', no_permission, name="no-permission"),
]