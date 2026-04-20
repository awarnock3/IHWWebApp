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

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("Start date must be before end date")
        
        return cleaned_data
