"""
Search forms for IHW archive
"""
from django import forms
from core.models import IhwNetwork


class ObservationSearchForm(forms.Form):
    """
    Search form for observations by date range and optional filters
    """
    start_date = forms.DateField(
        required=True,
        input_formats=['%Y-%m-%d'],  # Force YYYY-MM-DD format
        widget=forms.DateInput(attrs={
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'YYYY-MM-DD',
            'pattern': r'\d{4}-\d{2}-\d{2}',
            'title': 'Date in YYYY-MM-DD format (e.g., 1986-02-09)',
        }),
        label='Start Date',
        help_text='Format: YYYY-MM-DD (e.g., 1986-02-09)'
    )
    
    end_date = forms.DateField(
        required=True,
        input_formats=['%Y-%m-%d'],  # Force YYYY-MM-DD format
        widget=forms.DateInput(attrs={
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'YYYY-MM-DD',
            'pattern': r'\d{4}-\d{2}-\d{2}',
            'title': 'Date in YYYY-MM-DD format (e.g., 1986-03-15)',
        }),
        label='End Date',
        help_text='Format: YYYY-MM-DD (e.g., 1986-03-15)'
    )
    
    networks = forms.ModelMultipleChoiceField(
        queryset=IhwNetwork.objects.all().order_by('name'),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Disciplines (optional)',
        help_text='Leave unchecked to search all disciplines'
    )
    
    observer = forms.CharField(
        required=False,
        max_length=64,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Observer name (partial match)'
        }),
        label='Observer (optional)',
        help_text='Search by observer name'
    )
    
    min_solar_distance = forms.DecimalField(
        required=False,
        min_value=0,
        max_value=10,
        decimal_places=3,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0.500',
            'step': '0.001',
            'min': '0',
            'max': '10'
        }),
        label='Min Solar Distance (AU)',
        help_text='Minimum distance from Sun in Astronomical Units'
    )
    
    max_solar_distance = forms.DecimalField(
        required=False,
        min_value=0,
        max_value=10,
        decimal_places=3,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '2.000',
            'step': '0.001',
            'min': '0',
            'max': '10'
        }),
        label='Max Solar Distance (AU)',
        help_text='Maximum distance from Sun in Astronomical Units'
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        min_dist = cleaned_data.get('min_solar_distance')
        max_dist = cleaned_data.get('max_solar_distance')

        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("Start date must be before end date")
        
        if min_dist is not None and max_dist is not None:
            if min_dist > max_dist:
                raise forms.ValidationError("Minimum solar distance must be less than maximum")
        
        return cleaned_data
