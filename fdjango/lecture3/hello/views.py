from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    #render html file instead of simply returning http response with text
    return render(request, "hello/index.html")
def lucas(request):
    return HttpResponse("Hello, Lucas!")
def test(request):
    return HttpResponse("test test! Working?")
#{}=> context, providing information to the page
def greet(request, name):
    return render(request, "hello/greet.html", {
        "name": name.capitalize()
    })