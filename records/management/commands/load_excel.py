import pandas as pd
from django.core.management.base import BaseCommand
from records.models import Record  # adjust if app name is different

class Command(BaseCommand):
    help = 'Load data from Excel into Record model'

    def handle(self, *args, **kwargs):
        file_path = 'Mangalore_Waste_Formatted.xlsx'  # Put file in project root or give full path
        df = pd.read_excel(file_path)

        for _, row in df.iterrows():
            Record.objects.create(
                date=row['date'],
                vehicle_no=row['vehicle_no'],
                weight_kg=row['weight_kg'],
                source_panchayat=row['source_panchayat'],
                waste_type=row['waste_type']
            )
        self.stdout.write(self.style.SUCCESS('Excel data loaded successfully!'))
