from django.db import models
from unixtimestampfield.fields import UnixTimeStampField


class DeviceModel(models.Model):
    user_id = models.CharField(max_length=500, blank=True, null=True)
    heart_rate = models.FloatField(null=True, blank=True, default=None)
    respiration_rate = models.FloatField(null=True, blank=True, default=None)
    activity = models.IntegerField(blank=True, null=True)
    timestamp = UnixTimeStampField(auto_now_add=True)

    def __str__(self):
        return self.user_id
