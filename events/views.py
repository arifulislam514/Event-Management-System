from django.shortcuts import render, redirect
from django.http import HttpResponse
from events.models import Event, Category
from events.forms import EventModelForm, CategoryModelForm, LocationModelForm
from django.contrib import messages
from django.db.models import Q, Count, Max, Min, Avg
from datetime import time, datetime
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import user_passes_test, login_required, permission_required
from users.views import is_admin
from django.core.mail import send_mail
from django.conf import settings


def is_manager(user):
    return user.groups.filter(name='Manager').exists()

def is_Participant(user):
    return user.groups.filter(name='Participant').exists()

""" Create Event """
@login_required
@permission_required("events.add_event", login_url="no-permission")
def create_event(request):
    event_form = EventModelForm()
    location_form = LocationModelForm()
    
    if request.method == "POST":
        event_form = EventModelForm(request.POST, request.FILES)
        location_form = LocationModelForm(request.POST)
        
        if event_form.is_valid() and location_form.is_valid():
            event = event_form.save()
            location = location_form.save(commit=False)
            location.event = event
            location.save()
            
            messages.success(request,"Event Created Successfully")
            return redirect('create_event')
        
    context = {"event_form": event_form, "location_form":location_form}
    return render(request, "dashboard/event_form.html", context)
            


""" Update Event """
@login_required
@permission_required("events.change_event", login_url="no-permission")
def update_event(request, id):
    event = Event.objects.get(id=id)
    event_form = EventModelForm(instance=event)
    location_form = LocationModelForm(instance=event.location)if event.location else LocationModelForm()

    if request.method == "POST":
        event_form = EventModelForm(request.POST, instance=event)
        location_form = LocationModelForm(request.POST, instance=event.location)if event.location else LocationModelForm(request.POST)

        if event_form.is_valid() and location_form.is_valid():
            event = event_form.save()
            event_location = location_form.save(commit=False)
            event_location.event = event
            event_location.save()

            messages.success(request, "Event Updated Successfully")
            return redirect('update_event', id=id)
        else:
            print(event_form.errors)
            print(location_form.errors)
            messages.error(request, "Error updating the event.")

    context = {
        "event_form": event_form,
        "location_form": location_form
    }
    return render(request, "dashboard/event_form.html", context)




""" Delete Event """
@login_required
@permission_required("events.delete_event", login_url="no-permission")
def delete_event(request, id):
    if request.method == 'POST':
        event = Event.objects.get(id=id)
        event.delete()
        
        messages.success(request, "Event Deleted Successfully")
        return redirect('manager_dashboard')
    else:
        messages.error(request, "Something Wrong")
        return redirect('manager_dashboard')



""" view Event count by Category """
@login_required
def view_event_count(request):
    category = Category.objects.annotate(
        num_event = Count('event')).order_by('num_event')
    return render(request,"dashboard/show_event.html", {"category": category})


""" view Event List """
@login_required
def view_event_list(request):
    events = Event.objects.all().order_by('-date')
    return render(request, "dashboard/manager_dashboard.html", {"events": events})


""" Create Category """
@login_required
@permission_required("events.add_category", login_url="no-permission")
def create_category(request):
    category_form = CategoryModelForm()
    
    if request.method == "POST":
        category_form = CategoryModelForm(request.POST)
        
        if category_form.is_valid():
            category_form.save()
            
            messages.success(request,"Category Created Successfully")
            return redirect('create_category')
        
    context = {"category_form": category_form}
    return render(request, "dashboard/category_form.html", context)


""" Update Category """
@login_required
@permission_required("events.change_category", login_url="no-permission")
def update_category(request, id):
    category = Category.objects.get(id=id)
    category_form = CategoryModelForm(instance=category)
    if request.method == "POST":
        category_form = CategoryModelForm(request.POST, instance=category)

        if category_form.is_valid():
            category = category_form.save()

            messages.success(request, "Category Updated Successfully")
            return redirect('update_category', id=id)
        else:
            print(category_form.errors)
            messages.error(request, "Error updating the category.")
            
    context = {
        "category_form": category_form
    }
    return render(request,"dashboard/category_form.html", context)


""" Delete Category """
@login_required
@permission_required("events.delete_category", login_url="no-permission")
def delete_category(request, id):
    if request.method == 'POST':
        category = Category.objects.get(id=id)
        category.delete()
        
        messages.success(request, "Category Deleted Successfully")
        return redirect('manager_dashboard')
    else:
        messages.error(request, "Something Wrong")
        return redirect('manager_dashboard')

""" view Category List """
@login_required
def view_category_list(request):
    category = Category.objects.all()
    return render(request, "dashboard/manager_dashboard.html", {"category": category})


""" Delete Participant """
@login_required
def delete_participant(request, id):
    if request.method == 'POST':
        participant = User.objects.get(id=id)
        participant.delete()
        
        messages.success(request, "Participant Deleted Successfully")
        return redirect('admin_dashboard')
    else:
        messages.error(request, "Something Wrong")
        return redirect('admin_dashboard')


@user_passes_test(is_manager, login_url='no-permission')
def manager_dashboard(request):
    type = request.GET.get('type','today')
    current_date = datetime.now().date()
    current_time = datetime.now().time()

    user_counts = Event.objects.aggregate(
        total_user = Count('participants', distinct=True)
    )
    
    counts = Event.objects.aggregate(
        total=Count('id'),
        past_events=Count('id', filter=Q(date__lt=current_date) | Q(date=current_date, time__lt=current_time)),
        upcoming_events=Count('id', filter=Q(date__gt=current_date)  | Q(date=current_date, time__gte=current_time)),
    )

    base_query = Event.objects
    
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
    return render(request, "dashboard/manager_dashboard.html", context)


@user_passes_test(is_Participant, login_url='no-permission')
def user_dashboard(request):
    user = request.user
    events = Event.objects.filter(participants=user)
    contex = {
        "user":user,
        "events":events
    }
    return render(request,'dashboard/user_dashboard.html',contex)


def home(request):
    return render(request, "dashboard/home.html")

@login_required
def event_detaile(request, id):
    events = Event.objects.select_related('location', 'category').prefetch_related('participants').get(id=id)
    print(events)

    context = {
        "events": events,
    }
    return render(request, "dashboard/event_detaile.html", context)


@login_required
def events(request):
    input = request.GET.get('q')
    events = Event.objects.select_related('location','category').prefetch_related('participants').annotate(participant_count=Count('participants')).all()
    if input:
        events = events.filter(
            Q(name__icontains=input) | Q(location__city__icontains=input) | Q(location__country__icontains=input)
        )
    context = {
        "events": events,
        "search_result": input
    }
    return render(request, "dashboard/events.html", context)

@login_required
def dashboard(request):
    if is_admin(request.user):
        return redirect('admin-dashboard')
    elif is_manager(request.user):
        return redirect('manager_dashboard')
    elif is_Participant(request.user):
        return redirect('user-dashboard')
    
    return redirect('no-permission')

@login_required
@user_passes_test(is_Participant, login_url='no-permission')
def rsvp_event(request, id):
    event = Event.objects.get(id=id)
    user = request.user
    
    if user in event.participants.all():
        messages.info(request, "You already booked this event")
        return redirect('events')
    else:
        event.participants.add(user)
        messages.success(request, "Booked Successfull")
        return redirect('events')

