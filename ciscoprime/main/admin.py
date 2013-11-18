from django.contrib import admin

from .models import DisabledClient, ClientCount

admin.site.register(ClientCount)
admin.site.register(DisabledClient)
