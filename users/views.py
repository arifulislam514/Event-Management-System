from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import Group
from django.contrib.auth import login, logout
from users.forms import CustomRegistrationForm, AssignRoleForm, CreateGroupForm, CustomPasswordResetForm, CustomPasswordResetConfirmForm
from django.contrib import messages
from django.contrib import messages
from users.forms import LoginForm, EditProfileForm, CustomPasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Prefetch, Count, Q
from datetime import time, datetime
from events.views import Event, Category
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.views.generic import TemplateView, FormView, UpdateView, CreateView, ListView
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
User = get_user_model()



def is_admin(user):
    return user.groups.filter(name='Admin').exists()


class CustomSignupView(FormView):
    template_name = "login/sign_up.html"
    form_class = CustomRegistrationForm
    success_url = reverse_lazy('sign-up')
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data.get('password'))
        user.is_active = False
        if self.request.FILES:
            user.profile_image = self.request.FILES.get('profile_image')
        user.save()
        
        messages.success(self.request, 'A Confirmation mail sent. Please check your email')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        return super().form_invalid(form)


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'login/login.html'
    
    def get_success_url(self):
        next_page = self.request.GET.get('next')
        return next_page if next_page else super().get_success_url()


class CustomLogoutView(LogoutView):
    template_name = 'dashboard/home.html'
    def get_success_url(self):
        next_page = self.request.GET.get('next')
        return next_page if next_page else super().get_success_url()


def activate_user(request, user_id, token):
    try:
        user = User.objects.get(id=user_id)
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return redirect('login')
        else:
            return HttpResponse('Invalid Id or token')

    except User.DoesNotExist:
        return HttpResponse('User not found')


@method_decorator(user_passes_test(is_admin, login_url='no-permission'), name='dispatch')
class AdminDashboardView(View):
    template_name = "admin/admin_cart.html"
    
    def get(self, request, *args, **kwargs):
        current_date = datetime.now().date()
        current_time = datetime.now().time()
        type = request.GET.get('type', 'today')
        
        # Participants count
        user_counts = Event.objects.aggregate(
            total_user=Count('participants', distinct=True)
        )
        
        # Event counts
        counts = Event.objects.aggregate(
            total=Count('id'),
            past_events=Count('id', filter=Q(date__lt=current_date) | Q(date=current_date, time__lt=current_time)),
            upcoming_events=Count('id', filter=Q(date__gt=current_date) | Q(date=current_date, time__gte=current_time)),
        )
        
        base_query = Event.objects
        event_type = ""
        events = base_query.none()
        
        if type == 'past_event':
            events = base_query.filter(date__lt=current_date) | base_query.filter(date=current_date, time__lt=current_time)
            event_type = "Past Events"
        elif type == 'upcoming_event':
            events = base_query.filter(date__gt=current_date)  | base_query.filter(date=current_date, time__gte=current_time)
            event_type = "Upcoming Events"
        elif type == 'today':
            events = base_query.filter(date=current_date, time__gte=current_time)
            event_type = "Today Events"
        elif type == 'all':
            events = base_query.all()
            event_type = "All Events"
            
        all_user = User.objects.filter(events__isnull=False).distinct()
        cetagory = Category.objects.all()
        context = {
            "events": events,
            "counts": counts,
            "event_type": event_type,
            "users" : all_user,
            "cetagory": cetagory,
            "participant_counts": user_counts
        }
        return render(request, self.template_name, context)


@user_passes_test(is_admin, login_url='no-permission')
def user_list(request):
    users = User.objects.prefetch_related(
        Prefetch('groups', queryset=Group.objects.all(), to_attr='all_groups')
    ).all()

    for user in users:
        if user.all_groups:
            user.group_name = user.all_groups[0].name
        else:
            user.group_name = 'No Group Assigned'
    return render(request, 'login/user_list.html', {"users": users})

@method_decorator(user_passes_test(is_admin, login_url='no-permission'), name='dispatch')
class CustomAssignRole(UpdateView):
    template_name = "admin/assign_role.html"
    
    def get(self, request, user_id, *args, **kwargs):
        user = User.objects.get(id=user_id)
        form = AssignRoleForm()
        return render(request, self.template_name, {"form": form})
    
    def post(self, request, user_id, *args, **kwargs):
        user = User.objects.get(id=user_id)
        form = AssignRoleForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data.get('role')
            user.groups.clear()  # Remove old roles
            user.groups.add(role)
            messages.success(request, f"User {user.username} has been assigned to the {role.name} role")
            return redirect('admin-dashboard')
        return render(request, self.template_name, {"form": form})


@method_decorator(user_passes_test(is_admin, login_url='no-permission'), name='dispatch')
class CustomCreateGroupView(CreateView):
    model = Group
    form_class = CreateGroupForm
    template_name = "admin/create_group.html"
    success_url = reverse_lazy('group-list')
    
    def form_valid(self, form):
        messages.success(self.request, f"Group {form.instance.name} has been created successfully")
        return super().form_valid(form)
    

@user_passes_test(is_admin, login_url='no-permission')
def update_group(request, id):
    group = Group.objects.get(id=id)
    group_form = CreateGroupForm(instance=group)
    if request.method == 'POST':
        group_form = CreateGroupForm(request.POST, instance=group)

        if group_form.is_valid():
            group = group_form.save()
            messages.success(request, f"Group {group.name} has been updated successfully")
            return redirect('group-list')

    return render(request, 'admin/create_group.html', {'form': group_form})


@user_passes_test(is_admin, login_url='no-permission')
def delete_group(request, id):
    if request.method == 'POST':
        group = Group.objects.get(id=id)
        group.delete()
        
        messages.success(request, f"Group {group.name} has been deleted successfully")
        return redirect('group-list')
    else:
        messages.error(request,"Somthing wrong")
        return redirect(request, 'group-list')


@method_decorator(user_passes_test(is_admin, login_url='no-permission'), name='dispatch')
class GroupList(ListView):
    template_name = "admin/group_list.html"
    context_object_name = 'groups'
    queryset = Group.objects.prefetch_related('permissions').all()

class ProfileView(TemplateView):
    template_name = 'profile/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        group = user.groups.first()
        context['username'] = user.username
        context['email'] = user.email
        context['name'] = user.get_full_name()
        context['bio'] = user.bio
        context['profile_image'] = user.profile_image
        context['member_since'] = user.date_joined
        context['last_login'] = user.last_login
        context['group_name'] = group.name if group else "No Role"
        return context
    
    
class EditProfileView(UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = 'profile/update_profile.html'
    context_object_name = 'form'

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        form.save()
        return redirect('profile')


class ChangePassword(PasswordChangeView):
    template_name = 'profile/password_change.html'
    success_url = reverse_lazy("password_change")
    form_class = CustomPasswordChangeForm
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Your password was changed successfully.")
        return response

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'login/reset_password.html'
    success_url = reverse_lazy('login')
    html_email_template_name = 'login/reset_email.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['protocol'] = 'https' if self.request.is_secure() else 'http'
        context['domain'] = self.request.get_host()
        print(context)
        return context

    def form_valid(self, form):
        messages.success(
            self.request, 'A Reset email sent. Please check your email')
        return super().form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomPasswordResetConfirmForm
    template_name = 'login/reset_password.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(
            self.request, 'Password reset successfully')
        return super().form_valid(form)


def no_permission(request):
    return render(request,'login/no_permission.html')