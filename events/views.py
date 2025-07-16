from django.shortcuts import render, redirect
from django.http import HttpResponse
from events.models import Event, Category
from events.forms import EventModelForm, CategoryModelForm, LocationModelForm
from django.contrib import messages
from django.db.models import Q, Count, Max, Min, Avg
from datetime import time, datetime


""" Create Event """
def create_event(request):
    event_form = EventModelForm()
    location_form = LocationModelForm()
    
    if request.method == "POST":
        event_form = EventModelForm(request.POST)
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
def update_event(request, id):
    event = Event.objects.get(id=id)
    event_form = EventModelForm(instance=event)
    event_location_form = LocationModelForm(instance=event.location)if event.location else LocationModelForm()

    if request.method == "POST":
        event_form = EventModelForm(request.POST, instance=event)
        event_location_form = LocationModelForm(request.POST, instance=event.location)if event.location else LocationModelForm(request.POST)

        if event_form.is_valid() and event_location_form.is_valid():
            event = event_form.save()
            event_location = event_location_form.save(commit=False)
            event_location.event = event
            event_location.save()

            messages.success(request, "Event Updated Successfully")
            return redirect('update_event', id=id)
        else:
            print(event_form.errors)
            print(event_location_form.errors)
            messages.error(request, "Error updating the event.")

    context = {
        "event_form": event_form,
        "event_location_form": event_location_form
    }
    return render(request, "dashboard/event_form.html", context)




""" Delete Event """
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
def view_event_count(request):
    category = Category.objects.annotate(
        num_event = Count('event')).order_by('num_event')
    return render(request,"dashboard/show_event.html", {"category": category})


""" view Event List """
def view_event_list(request):
    events = Event.objects.all().order_by('-date')
    return render(request, "dashboard/manager_dashboard.html", {"events": events})


""" Create Category """
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
def view_category_list(request):
    category = Category.objects.all()
    return render(request, "dashboard/manager_dashboard.html", {"category": category})


""" Add Participant """
def add_participant(request):
    participant_form = ParticipantModelForm()
    if request.method == "POST":
        participant_form = ParticipantModelForm(request.POST)
        
        if participant_form.is_valid():
            participant_form.save()
            
            messages.success(request,"Participant Added Successfully")
            return redirect('add_participant')
        
    context = {"participant_form": participant_form}
    return render(request, "dashboard/participant_form.html", context)


""" Update Participant """
def update_participant(request, id):
    participant = Participant.objects.get(id=id)
    participant_form = ParticipantModelForm(instance=participant)
    if request.method == "POST":
        participant_form = ParticipantModelForm(request.POST, instance=participant)

        if participant_form.is_valid():
            participant_form.save()

            messages.success(request, "Participant Updated Successfully")
            return redirect('update_participant', id=id)
        else:
            print(participant_form.errors)
            messages.error(request, "Error updating the Participant.")
            
    context = {
        "participant_form": participant_form
    }
    return render(request,"dashboard/participant_form.html", context)



""" Delete Participant """
def delete_participant(request, id):
    if request.method == 'POST':
        participant = Participant.objects.get(id=id)
        participant.delete()
        
        messages.success(request, "Participant Deleted Successfully")
        return redirect('manager_dashboard')
    else:
        messages.error(request, "Something Wrong")
        return redirect('manager_dashboard')
    

""" view Participant List """
# def view_participant_list(request):
    # participant_counts = Participant.objects.aggregate(
    #     total = Count('id')
    # )
    # participant = Participant.objects.all()
    # context = {
    #     "participant": participant,
    #     "participant_counts": participant_counts
    # }
    # return render(request, "dashboard/manager_dashboard.html", context)


def manager_dashboard(request):
    type = request.GET.get('type','today')
    current_date = datetime.now().date()
    current_time = datetime.now().time()

    participant_counts = Event.objects.aggregate(
        total_participant = Count('participants', distinct=True)
    )
    
    counts = Event.objects.aggregate(
        total=Count('id'),
        # total_participant = Count('participants', distinct=True),
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
        
    participant = Participant.objects.all()
    cetagory = Category.objects.all()
    context = {
        "events": events,
        "counts": counts,
        "event_type": event_type,
        "participant_counts": participant_counts,
        "participant" : participant,
        "cetagory": cetagory
    }
    return render(request, "dashboard/manager_dashboard.html", context)


def home(request):
    return render(request, "dashboard/home.html")

def event_detaile(request, id):
    events = Event.objects.select_related('location', 'category').prefetch_related('participants').get(id=id)
    print(events)

    context = {
        "events": events,
    }
    return render(request, "dashboard/event_detaile.html", context)


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