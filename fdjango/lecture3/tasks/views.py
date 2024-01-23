from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse

#create class for a form
class NewTaskForm(forms.Form):
    #add fields
    #(does autom. client side validation) 
    task = forms.CharField(label="new task")
    priority = forms.IntegerField(label="priority")


# Create your views here.
def index(request):
    #generate list of tasks per session (per user etc)
    if "tasks" not in request.session:
        request.session["tasks"]=[]

    return render(request, "tasks/index.html", {
        "tasks": request.session["tasks"]
    })
def add(request):
    #server side validation
    if request.method == 'POST':
        form = NewTaskForm(request.POST)
        #add to task list if is valid
        if form.is_valid():
            task = form.cleaned_data['task']
            request.session["tasks"] += [task]
            return HttpResponseRedirect(reverse("tasks:index"))
        #return form to use if not valid
        else:
            return render(request, "tasks/add.html",{
        "form": form
    })
    
    #if form was not sent using POST, present user a blank form
    return render(request, "tasks/add.html",{
        "form": NewTaskForm()
    })