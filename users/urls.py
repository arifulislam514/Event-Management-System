from django.urls import path
from users.views import activate_user, update_group, no_permission, delete_group, user_list
from users.views import CustomLoginView, CustomLogoutView, CustomSignupView, AdminDashboardView, CustomPasswordResetView, CustomPasswordResetConfirmView, ChangePassword, CustomAssignRole, CustomCreateGroupView, GroupList, ProfileView, EditProfileView


urlpatterns = [
    # path('create_event/', create_event, name="create_event"),
    path('sign-up/', CustomSignupView.as_view(), name="sign-up"),
    path('login/', CustomLoginView.as_view(), name="login"),
    path('logout/', CustomLogoutView.as_view(), name="logout"),
    path('activate/<int:user_id>/<str:token>/', activate_user),
    path('assign-role/<int:user_id>/', CustomAssignRole.as_view(), name="assign-role"),
    path('create-group/', CustomCreateGroupView.as_view(), name="create-group"),
    path('update-group/<int:id>/', update_group, name="update-group"),
    path('delete-group/<int:id>/', delete_group, name="delete-group"),
    path('group-list/', GroupList.as_view(), name="group-list"),
    path('user-list/', user_list, name="user-list"),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('edit_profile/', EditProfileView.as_view(), name='edit_profile'),
    path('password_change/', ChangePassword.as_view(), name='password_change'),
    path('reset_password/', CustomPasswordResetView.as_view(), name='reset_password'),
    path('password_reset_confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('admin-dashboard/', AdminDashboardView.as_view(), name="admin-dashboard"),
    path('no-permission/', no_permission, name="no-permission"),
]
