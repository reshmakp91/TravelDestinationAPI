from django.contrib import admin
from .models import CustomUser, Country, State, District, Destination

class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'username', 'password', 'country', 'state', 'district')

class CountryAdmin(admin.ModelAdmin):
    list_display = ('name',)


class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')


class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'state')

class DestinationAdmin(admin.ModelAdmin):
    list_display = ('place_name','weather','state','district','google_map_link','description','created_by')

admin.site.register(CustomUser, UserAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(District, DistrictAdmin)
admin.site.register(Destination,DestinationAdmin)

