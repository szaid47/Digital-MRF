from django.forms import ModelForm
from .models import Record


class RecordForm(ModelForm):
    class Meta:
        model = Record
        fields = '__all__'
        exclude = ['owner']
        labels = {
            'name': 'user-name',
            'vehicle_no': 'Vehicle Number',
            'source_panchayat': 'Source Panchayat',
            'weight_kg': 'Weight (kg)',
            'waste_type': 'Type of Waste',
            'picture': 'Waste photo (if available).',
            'evidence': 'Transport documents evidence (optional)',
        }

    def __init__(self, *args, **kwargs):
        super(RecordForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})

        self.fields['waste_type'].widget.attrs.update({'class': 'content-box'})
        self.fields['name'].widget.attrs.update({'placeholder': 'Enter record title or name'})

    def clean(self):
        cleaned_data = super().clean()
        weight_kg = cleaned_data.get('weight_kg')

        if weight_kg is not None and weight_kg < 0:
            self.add_error('weight_kg', 'Weight must be greater than zero.')
