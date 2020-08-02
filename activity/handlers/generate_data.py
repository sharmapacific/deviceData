import logging
import os
import random
import time

from activity.constants import ACTIVITY, HEART_RATE, RESPIRATION_RATE, USER_ID
from activity.models import DeviceModel
from activity.utils import generate_csv_file, readable_time

import arrow
from django.conf import settings
from django.db.models import Avg, Max, Min
logging.basicConfig(
    level=logging.INFO,
    filename=os.path.join(settings.LOG_DIR) + '/activity.log',
    format='%(asctime)s - [%(levelname)s] - %(app)s - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s',
)
logger = logging.getLogger(__name__)
logger = logging.LoggerAdapter(logger, {'app': 'Activity'})


class DeviceData:

    def __init__(self):
        self.user_qs = DeviceModel.objects.values_list('user_id', flat=True).distinct()

    def generate_data(self):
        data = {
            'user_id': random.choice(USER_ID),
            'heart_rate': random.choice(HEART_RATE),
            'respiration_rate': random.choice(RESPIRATION_RATE),
            'activity': random.choice(ACTIVITY)
        }
        return data

    def insert_to_db(self, limit):
        """
        Generating random data and inserting into database
        """
        try:
            for i in range(limit):
                data = self.generate_data()
                DeviceModel.objects.create(**data)
                time.sleep(1)
            return True, {'message': 'Generated Successfully'}
        except Exception as e:
            logger.error('Exception-{}'.format(e))
            return False, {'message': 'Unable to Generat'}

    def aggregate_value(self, file_path):
        """
        calculating avg, min, max of entire data for each user
        """
        try:
            result = []
            for user in [*self.user_qs]:
                logger.info('user - {}'.format(user))
                queryset = DeviceModel.objects.filter(user_id=user).aggregate(
                    Avg('heart_rate'), Max('heart_rate'), Min('heart_rate'),
                    Avg('respiration_rate'), Max('respiration_rate'),
                    Min('respiration_rate'), Min('timestamp'), Max('timestamp')
                    )
                data = self.format_data(user, queryset)
                result.append(data)
            generate_csv_file(file_path, result)
            return True
        except Exception as e:
            logger.error('Exception-{}'.format(e))
            return False

    def format_data(self, user, queryset):
        """
        formatting data before writing it into csv
        """
        data = {
            'start_time': readable_time(queryset.get('timestamp__min')),
            'end_time': readable_time(queryset.get('timestamp__max')),
            'user_id': user,
            'avg_hr': queryset.get('heart_rate__avg'),
            'max_hr': queryset.get('heart_rate__max'),
            'min_hr': queryset.get('heart_rate__min'),
            'avg_rr': queryset.get('respiration_rate__avg'),
            'max_rr': queryset.get('respiration_rate__max'),
            'min_rr': queryset.get('respiration_rate__min')
        }
        return data

    def segment_value(self, file_path):
        """
        To calculate hourly avg, min, max, for each user using the entire data
        in 15 mins segments
        """
        try:
            seg_list = []
            device_objs = DeviceModel.objects.all()
            for user in [*self.user_qs]:
                logger.info('user - {}'.format(user))
                min_ts = device_objs.aggregate(Min('timestamp'))
                from_seg = arrow.get(min_ts.get('timestamp__min'))
                to_seg = from_seg.shift(minutes=15)
                while True:
                    data = self.calculate_segment(user, device_objs, from_seg, to_seg)
                    seg_list.append(data)
                    if device_objs.filter(timestamp__gte=to_seg.timestamp):
                        from_seg = to_seg
                        to_seg = from_seg.shift(minutes=15)
                    else:
                        break
            generate_csv_file(file_path, seg_list)
            return True
        except Exception as e:
            logger.error('Exception-{}'.format(e))
            return False

    def calculate_segment(self, user, objs, from_seg, to_seg):
        """
        Comman function to segmented query
        """
        queryset = objs.filter(
            user_id=user,
            timestamp__range=[from_seg.datetime, to_seg.datetime]
            ).aggregate(Avg('heart_rate'), Max('heart_rate'),
                        Min('heart_rate'), Avg('respiration_rate'),
                        Max('respiration_rate'), Min('respiration_rate'),
                        Min('timestamp'), Max('timestamp'))
        data = self.format_data(user, queryset)
        data['start_time'] = from_seg.format('YYYY-MM-DD HH:mm:ss')
        data['end_time'] = to_seg.format('YYYY-MM-DD HH:mm:ss')
        return data

    def range_segment(self, file_path, timestamp, timezone):
        """
        To calculate hourly range of avg, min, max of each user from the
        original UTC to particular timezone
        """
        try:
            seg_list = []
            for user in [*self.user_qs]:
                logger.info('user - {}'.format(user))
                from_ts = timestamp.to(timezone)
                to_ts = from_ts.shift(minutes=60)
                device_objs = DeviceModel.objects.filter(
                                user_id=user,
                                timestamp__range=[from_ts.datetime, to_ts.datetime]
                            )
                cur_ts = from_ts.shift(minutes=15)
                while True:
                    data = self.calculate_segment(user, device_objs, from_ts, cur_ts)
                    seg_list.append(data)
                    if cur_ts == to_ts:
                        break
                    from_ts = cur_ts
                    cur_ts = from_ts.shift(minutes=15)
            generate_csv_file(file_path, seg_list)
            return True
        except Exception as e:
            logger.error('Exception-{}'.format(e))
            return False
