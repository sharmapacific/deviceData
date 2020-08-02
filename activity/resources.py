from activity.models import DeviceModel
from import_export import resources


class DeviceResource(resources.ModelResource):
    class Meta:
        model = DeviceModel
