from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Rider)
admin.site.register(Driver)
admin.site.register(RideRequest)