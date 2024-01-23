from django.shortcuts import render
from .models import Fl, Passenger
from django.http import HttpResponseRedirect
from django.urls import reverse 

# Create your views here.
def index(request):
    return render(request, "fls/index.html", {
        "fls": Fl.objects.all()
    })

def fl(request, fl_id):
    fl = Fl.objects.get(pk=fl_id)
    return render(request, 'fls/fl.html', {
        'fl': fl,
        'passengers': fl.passengers.all(),
        'non_passengers': Passenger.objects.exclude(fls=fl).all()
    })

def book(request, fl_id):
    if request.method == 'POST': # If the form has been submitted...
        #flihgt to book
        fl = Fl.objects.get(pk = fl_id)
        #get if of passenger to be booked
        passenger = Passenger.objects.get(pk=int(request.POST['passenger']))
        #add flight
        passenger.fls.add(fl)
        #redirect user
        return HttpResponseRedirect(reverse("fl", args=(fl.id,)))