from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def index(request):
    #user object is automatically associated with the request by djnago design
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    return render(request, 'users/user.html')
    
def login_view(request):
    #get credentials
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        #authenticate user
        user = authenticate(request, username=username, password=password)
        #if authentication succeded, login and redirect user
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'users/login.html',{
                'message': 'Invalid credentials'
            })
            

    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    return render(request, 'users/login.html', {
        'message': 'Logged out'
    })