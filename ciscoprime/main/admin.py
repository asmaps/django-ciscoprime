from django.contrib import admin

from .models import DisabledClient, ClientCount, RogueAP, TrackedRogue

class TrackedRogueAdmin(admin.ModelAdmin):
    search_fields = ['ap__mac', 'ap__ssid', 'booth_number', 'exhibitor_name']
    list_display = ('ap', 'booth_number', 'exhibitor_name')

admin.site.register(RogueAP)
admin.site.register(TrackedRogue, TrackedRogueAdmin)
admin.site.register(ClientCount)
admin.site.register(DisabledClient)

