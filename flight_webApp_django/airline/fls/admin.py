from django.contrib import admin
from .models import Fl, Airport, Passenger

# Register your models here.
#settings for admin interface
class FlAdmin(admin.ModelAdmin):
    list_display = ('id', 'origin', 'destination', 'duration')

class PassengerAdmin(admin.ModelAdmin):
    filter_horizontal = ('fls', )

admin.site.register(Airport)
#use FlAdmin config for admin interface
admin.site.register(Fl, FlAdmin)
admin.site.register(Passenger, PassengerAdmin)
