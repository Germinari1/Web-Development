from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name='index'),
    path("<int:fl_id>", views.fl, name="fl"),
    path("<int:fl_id>/book", views.book, name='book')
]