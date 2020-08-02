import os

from activity.handlers.generate_data import DeviceData
from activity.resources import DeviceResource

import arrow
from django.conf import settings
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView


class EntireDataView(APIView):
    """View for every second data in json file"""
    http_method_names = ['get']

    def get(self, request):
        data = request.query_params.dict()
        file_name = 'completeData.json'
        if data['type'] == 'json':
            json_op = DeviceResource()
            dataset = json_op.export()
            response = HttpResponse(dataset.json, content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename={}'.format(file_name)
        return response

    def post(self, request):
        pass


class AggregateDataView(APIView):
    """Generating the avg, min, max for all data in csv file"""
    http_method_names = ['get']

    def get(self, request):
        file_name = 'agg_report_{}.csv'.format(str(arrow.utcnow().timestamp))
        file_path = os.path.join(settings.MEDIA_DIR) + '/{}'.format(file_name)
        response = DeviceData().aggregate_value(file_path)
        if response:
            with open(file_path) as myfile:
                response = HttpResponse(myfile, content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename={}'.format(file_name)
                return response
        return HttpResponse('Unable to download')


class SegmentDataView(APIView):
    """
    Generating the hourly avg, min, max for 15 mins segments
    of entire data
    """
    http_method_names = ['get']

    def get(self, request):
        file_name = 'seg_report_{}.csv'.format(str(arrow.utcnow().timestamp))
        file_path = os.path.join(settings.MEDIA_DIR) + '/{}'.format(file_name)
        response = DeviceData().segment_value(file_path)
        if response:
            with open(file_path) as myfile:
                response = HttpResponse(myfile, content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename={}'.format(file_name)
                return response
        return HttpResponse('Unable to download')


class RangeDataView(APIView):
    """Generating hourly range avg, min, max in particular timezone"""
    http_method_names = ['post']

    def post(self, request):
        data = request.POST.dict()
        from_ts = arrow.get(data['hour_seg'])
        timezone = data['timezone']

        file_name = 'range_report_{}.csv'.format(str(arrow.utcnow().timestamp))
        file_path = os.path.join(settings.MEDIA_DIR) + '/{}'.format(file_name)
        response = DeviceData().range_segment(file_path, from_ts, timezone)
        if response:
            with open(file_path) as myfile:
                response = HttpResponse(myfile, content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename={}'.format(file_name)
                return response
        return HttpResponse('Unable to download')


class GenerateDataView(APIView):
    """
    API for generate random values of hear_rate, resp_rate and activity
    every second in increasing order of unix timestamp (epoch)
    """
    http_method_names = ['post']

    def post(self, request):
        data = request.data
        limit = data.get('range')
        response, content = DeviceData().insert_to_db(limit)
        return Response(content)
