import django_filters
from .models import Record

class FilterRecords(django_filters.FilterSet):
    class Meta:
        model = Record
        fields = {
            'date': ['exact', 'gte', 'lte'],
            'vehicle_no': ['icontains'],
            'source_panchayat': ['icontains'],
            'waste_type': ['icontains'],
        }
