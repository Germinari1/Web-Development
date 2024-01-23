from django.shortcuts import render
from datetime import *

# Create your views here.
def index(request):
    now = datetime.today()
    return render(request, "newyear/index.html", {
        "newyear": now.month == 1 and now.day ==1 
    })