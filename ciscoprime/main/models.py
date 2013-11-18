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
