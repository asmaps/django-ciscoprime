from django.db import models
from django.conf import settings

class CiscoPrimeBaseModelNoCreatedBy(models.Model):
    last_update = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class CiscoPrimeBaseModel(CiscoPrimeBaseModelNoCreatedBy):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)

    class Meta:
        abstract = True


class ClientCount(CiscoPrimeBaseModelNoCreatedBy):
    count = models.IntegerField()

    def __unicode__(self):
        return "%d at %s" % (self.count, self.created)


class DisabledClient(CiscoPrimeBaseModel):
    mac = models.CharField(max_length=32)
    reason = models.TextField()

    def __unicode__(self):
        return "%s (%s)" % (self.mac, self.reason)


class RogueAP(CiscoPrimeBaseModel):
    ssid = models.CharField(max_length=128)
    mac = models.CharField(max_length=32)

    def __unicode__(self):
        return "%s (%s)" % (self.ssid, self.mac)


class TrackedRogue(CiscoPrimeBaseModel):
    ap = models.ForeignKey(RogueAP)
    booth_number = models.CharField(max_length=128, null=True, blank=True)
    exhibitor_name = models.CharField(max_length=128, null=True, blank=True)
    additional_info = models.TextField()

    def __unicode__(self):
        return "%s: %s (%s)" % (self.ap, self.exhibitor_name, self.booth_number)

