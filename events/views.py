from django.shortcuts import render, redirect
from django.http import HttpResponse
from events.models import Event, Category, Participant
from events.forms import EventModelForm, CategoryModelForm, LocationModelForm
from django.contrib import messages
from django.db.models import Q, Count, Max, Min, Avg


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
    return render(request, "event_form.html", context)
            


""" Update Event """
def update_event(request, id):
    event = Event.objects.get(id=id)
    event_form = EventModelForm(instance=event)
    
    if event.location:
        event_location_form = LocationModelForm(instance=event.location)
        
    if request.method == "POST":
        event_form = EventModelForm(request.POST, instance=event)
        event_location_form = LocationModelForm(request.POST, instance=event.location)
        
        if event_form.is_valid() and event_location_form.is_valid():
            event = event_form.save()
            event_location = event_location_form.save(commit=False)
            event_location.event = event
            event_location.save()
            
            messages.success(request,"Event Updated Successfully")
            return redirect('update_event',id=id)
        # else: 
        #     messages.error(request,"Somthing wrong")
        #     return redirect('update_event',id=id)
            
        
    context = {"event_form": event_form, "event_location_form":event_location_form}
    return render(request, "event_form.html", context)


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
    return render(request,"show_event.html", {"category": category})


""" view Event List """
def view_event_list(request):
    events = Event.objects.all().order_by('-date')
    return render(request, "manager_dashboard.html", {"events": events})


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
    return render(request, "category_form.html", context)


""" Delete Category """
def delete_category(request):
    if request.method == 'POST':
        category = Category.objects.get(id=id)
        category.delete()
        
        messages.success(request, "Category Deleted Successfully")
        return redirect('delete_category')
    else:
        messages.error(request, "Something Wrong")
        return redirect('delete_category')


def manager_dashboard(request):
    return render(request, "manager_dashboard.html")