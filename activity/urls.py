from activity.views import (
                    AggregateDataView,
                    EntireDataView,
                    GenerateDataView,
                    RangeDataView,
                    SegmentDataView
                )
from django.urls import path

app_name = 'activity'

urlpatterns = [
    path('agg_data/', AggregateDataView.as_view(), name='agg_data'),
    path('entire_data/', EntireDataView.as_view(), name='entire_data'),
    path('seg_data/', SegmentDataView.as_view(), name='seg_data'),
    path('range_data/', RangeDataView.as_view(), name='range_data'),
    path('gen_data/', GenerateDataView.as_view(), name='gen_data'),
]
