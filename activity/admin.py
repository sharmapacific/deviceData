import csv

import arrow
from activity.models import DeviceModel
from django.contrib import admin
from django.http import HttpResponse


@admin.register(DeviceModel)
class DeviceModelAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'heart_rate', 'respiration_rate',
                    'activity', 'created_at',)

    def created_at(self, obj):
        return arrow.get(obj.timestamp).format('YYYY-MM-DD HH:mm:ss')

    search_fields = ('user_id', 'activity',)

    actions = ['export_as_csv']

    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename={}.csv'.format(meta)
        )
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = 'Export Selected'
