from django.db import models
import uuid
from users.models import Profile
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncMonth

class Record(models.Model):
    owner = models.ForeignKey(Profile, blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    vehicle_no = models.CharField(max_length=100, null=True, blank=True)
    weight_kg = models.FloatField(null=True, blank=True)
    source_panchayat = models.CharField(max_length=255, null=True, blank=True)
    waste_type = models.CharField(max_length=255, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)

    def __str__(self):
        return f"{self.date} - {self.vehicle_no} - {self.source_panchayat}"

    # ------- ✅ Reporting Methods (inside Record model) --------
    @classmethod
    def get_total_quantities(cls):
        return cls.objects.aggregate(
            total_records=Count('id'),
            total_weight=Sum('weight_kg'),
            average_weight=Avg('weight_kg')
        )

    @classmethod
    def get_all_records(cls):
        return cls.objects.values(
            'date', 'vehicle_no', 'weight_kg', 'source_panchayat', 'waste_type'
        ).order_by('-date')

    @classmethod
    def get_quantity_by_county(cls):
        return cls.objects.values('source_panchayat').annotate(
            total_weight=Sum('weight_kg'),
            record_count=Count('id')
        ).order_by('-total_weight')

    @classmethod
    def get_monthly_summary(cls):
        return cls.objects.annotate(month=TruncMonth('date')).values('month').annotate(
            total_weight=Sum('weight_kg'),
            entries=Count('id')
        ).order_by('month')


class Tag(models.Model):
    name = models.CharField(null=True, blank=True, max_length=400)
    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)

    def __str__(self):
        return self.name
