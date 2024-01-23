from django.urls import path
#import views
from . import views

#define urls: (url, which view to render, optional name)
urlpatterns = [
    #"" to indicate default route
    path("", views.index, name="index"),
    #if this route is accessed, a new view function (lucas() => views.lucas) is called and a different http respose returned
    path("lucas", views.lucas, name="lucas"),
    path("test", views.test, name="test"),
    #<str:name> to indicate that can be any string => "name" is passed as parameter to the greet function
    path("<str:name>", views.greet, name="greet")
]