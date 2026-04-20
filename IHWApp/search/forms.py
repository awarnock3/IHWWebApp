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
            'type': 'date',
            'class': 'form-control',
            'placeholder': 'YYYY-MM-DD'
        }),
        label='Start Date',
        help_text='Beginning of date range (UTC)'
    )
    
    end_date = forms.DateField(
        required=True,
        input_formats=['%Y-%m-%d'],  # Force YYYY-MM-DD format
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'placeholder': 'YYYY-MM-DD'
        }),
        label='End Date',
        help_text='End of date range (UTC)'
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
