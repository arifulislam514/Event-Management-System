from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, logout
from users.forms import CustomRegistrationForm, AssignRoleForm, CreateGroupForm
from django.contrib import messages
from django.contrib import messages
from users.forms import LoginForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Prefetch, Count, Q
from datetime import time, datetime
from events.views import Event, Category
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import FormView, UpdateView, CreateView, ListView
from django.views import View
from django.utils.decorators import method_decorator



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
        user.save()
        
        messages.success(self.request, 'A Confirmation mail sent. Please check your email')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        return super().form_invalid(form)


# def sign_up(request):
#     form = CustomRegistrationForm()
#     if request.method == 'POST':
#         form = CustomRegistrationForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.set_password(form.cleaned_data.get('password'))
#             user.is_active = False
#             user.save()
#             messages.success(
#                 request, 'A Confirmation mail sent. Please check your email')
#             return redirect('sign-up')

#         else:
#             print("Form is not valid")
#     return render(request, 'login/sign_up.html', {"form": form})


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'login/login.html'
    
    def get_success_url(self):
        next_page = self.request.GET.get('next')
        return next_page if next_page else super().get_success_url()


# def sign_in(request):
#     form = LoginForm()
#     if request.method == 'POST':
#         form = LoginForm(data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             login(request, user)
#             return redirect('home')
#     return render(request, 'login/login.html', {'form': form})

# @login_required
# def sign_out(request):
#     if request.method == 'POST':
#         logout(request)
#         return redirect('home')


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


# @user_passes_test(is_admin, login_url='no-permission')
# def admin_dashboard(request):
#     type = request.GET.get('type','today')
#     current_date = datetime.now().date()
#     current_time = datetime.now().time()

#     user_counts = Event.objects.aggregate(
#         total_user = Count('participants', distinct=True)
#     )
    
#     counts = Event.objects.aggregate(
#         total=Count('id'),
#         past_events=Count('id', filter=Q(date__lt=current_date) | Q(date=current_date, time__lt=current_time)),
#         upcoming_events=Count('id', filter=Q(date__gt=current_date)  | Q(date=current_date, time__gte=current_time)),
#     )

#     base_query = Event.objects
    
#     if type == 'past_event':
#         events = base_query.filter(date__lt=current_date) | base_query.filter(date=current_date, time__lt=current_time)
#         event_type = "Past Events"
#     elif type == 'upcoming_event':
#         events = base_query.filter(date__gt=current_date)  | base_query.filter(date=current_date, time__gte=current_time)
#         event_type = "Upcoming Events"
#     elif type == 'today':
#         events = base_query.filter(date=current_date, time__gte=current_time)
#         event_type = "Today Events"
#     elif type == 'all':
#         events = base_query.all()
#         event_type = "All Events"
        
#     all_user = User.objects.filter(events__isnull=False).distinct()
#     cetagory = Category.objects.all()
#     context = {
#         "events": events,
#         "counts": counts,
#         "event_type": event_type,
#         "users" : all_user,
#         "cetagory": cetagory,
#         "participant_counts": user_counts
#     }
#     return render(request, "admin/admin_cart.html", context)


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
    
    

# @user_passes_test(is_admin, login_url='no-permission')
# def assign_role(request, user_id):
#     user = User.objects.get(id=user_id)
#     form = AssignRoleForm()

#     if request.method == 'POST':
#         form = AssignRoleForm(request.POST)
#         if form.is_valid():
#             role = form.cleaned_data.get('role')
#             user.groups.clear()  # Remove old roles
#             user.groups.add(role)
#             messages.success(request, f"User {user.username} has been assigned to the {role.name} role")
#             return redirect('admin-dashboard')

#     return render(request, 'admin/assign_role.html', {"form": form})


# @user_passes_test(is_admin, login_url='no-permission')
# def create_group(request):
#     group_form = CreateGroupForm()
#     if request.method == 'POST':
#         group_form = CreateGroupForm(request.POST)

#         if group_form.is_valid():
#             group = group_form.save()
#             messages.success(request, f"Group {group.name} has been created successfully")
#             return redirect('group-list')
#     return render(request, 'admin/create_group.html', {'group_form': group_form})

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

    return render(request, 'admin/create_group.html', {'group_form': group_form})


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


# @user_passes_test(is_admin, login_url='no-permission')
# def group_list(request):
#     groups = Group.objects.prefetch_related('permissions').all()
#     return render(request, 'admin/group_list.html', {'groups': groups})

@method_decorator(user_passes_test(is_admin, login_url='no-permission'), name='dispatch')
class GroupList(ListView):
    template_name = "admin/group_list.html"
    context_object_name = 'groups'
    queryset = Group.objects.prefetch_related('permissions').all()

def no_permission(request):
    return render(request,'login/no_permission.html')