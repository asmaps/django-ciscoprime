from django.contrib import admin

from .models import DisabledClient, ClientCount, RogueAP, TrackedRogue

admin.site.register(RogueAP)
admin.site.register(TrackedRogue)
admin.site.register(ClientCount)
admin.site.register(DisabledClient)

