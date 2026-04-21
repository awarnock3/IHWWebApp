"""
Search views for IHW archive
"""
from django.views.generic import FormView, ListView, DetailView, TemplateView
from django.db.models import Q
from django.http import Http404, HttpResponse
from core.models import IdxMetaCommon, IhwEphemeris
from core.fits_utils import read_fits_header, format_header_for_display, get_header_summary
from core.archive_utils import is_archive_available, find_fits_header_file, find_pds_label_file
from .forms import ObservationSearchForm
import os


class SearchView(FormView):
    """Main search page with form"""
    template_name = 'search/search.html'
    form_class = ObservationSearchForm
    
    def form_valid(self, form):
        # Redirect to results with query parameters
        from django.shortcuts import redirect
        from urllib.parse import urlencode
        
        params = {
            'start_date': form.cleaned_data['start_date'].isoformat(),
            'end_date': form.cleaned_data['end_date'].isoformat(),
        }
        
        if form.cleaned_data.get('networks'):
            params['networks'] = ','.join(str(n.id) for n in form.cleaned_data['networks'])
        
        if form.cleaned_data.get('observer'):
            params['observer'] = form.cleaned_data['observer']
        
        return redirect('/search/results/?' + urlencode(params))


class SearchResultsView(ListView):
    """Display search results"""
    model = IdxMetaCommon
    template_name = 'search/results.html'
    context_object_name = 'observations'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = IdxMetaCommon.objects.select_related(
            'network', 'idxfileid', 'idxfileid__subnet'
        )
        
        # Date range filter (required)
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        if start_date and end_date:
            queryset = queryset.filter(
                date_obs__date__gte=start_date,
                date_obs__date__lte=end_date
            )
        
        # Network filter (optional)
        networks = self.request.GET.get('networks')
        if networks:
            network_ids = [int(n) for n in networks.split(',') if n.isdigit()]
            queryset = queryset.filter(network_id__in=network_ids)
        
        # Observer filter (optional)
        observer = self.request.GET.get('observer')
        if observer:
            queryset = queryset.filter(observer__icontains=observer)
        
        return queryset.order_by('-date_obs')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add search parameters to context for display
        context['start_date'] = self.request.GET.get('start_date')
        context['end_date'] = self.request.GET.get('end_date')
        context['observer_query'] = self.request.GET.get('observer', '')
        
        # Add result count
        context['total_results'] = self.get_queryset().count()
        
        return context


class ObservationDetailView(DetailView):
    """Detail view for a single observation"""
    model = IdxMetaCommon
    template_name = 'search/observation_detail.html'
    context_object_name = 'observation'
    
    def get_context_data(self, **kwargs):
        from core.models import get_discipline_metadata, format_metadata_fields
        
        context = super().get_context_data(**kwargs)
        
        # Add ephemeris data
        context['ephemeris'] = self.object.get_ephemeris()
        
        # Check if archive is available
        context['archive_available'] = is_archive_available()
        
        # Add file paths if file exists and archive is available
        if self.object.idxfileid and context['archive_available']:
            context['file_paths'] = self.object.idxfileid.get_file_paths()
            
            # Check if FITS or PDS label files exist
            full_path = self.object.idxfileid.get_full_path()
            if full_path:
                base_path = os.path.splitext(full_path)[0]
                context['has_fits'] = find_fits_header_file(base_path) is not None
                context['has_pds_label'] = find_pds_label_file(base_path) is not None
        
        # Fetch discipline-specific metadata
        metadata_obj = get_discipline_metadata(self.object)
        if metadata_obj:
            context['discipline_metadata'] = format_metadata_fields(metadata_obj)
        
        return context


class FitsHeaderView(TemplateView):
    """Display FITS header for a file"""
    template_name = 'search/fits_header.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Check if archive is available
        if not is_archive_available():
            raise Http404("Archive files are not available")
        
        # Get observation
        try:
            observation = IdxMetaCommon.objects.select_related('idxfileid').get(pk=kwargs['pk'])
        except IdxMetaCommon.DoesNotExist:
            raise Http404("Observation not found")
        
        if not observation.has_file:
            raise Http404("No file associated with this observation")
        
        # Find FITS header file (.fit, .fits, or .hdr)
        full_path = observation.idxfileid.get_full_path()
        if not full_path:
            raise Http404("File path not found")
        
        base_path = os.path.splitext(full_path)[0]
        fits_path = find_fits_header_file(base_path)
        
        if not fits_path:
            raise Http404("FITS header file not found (.fit, .fits, or .hdr)")
        
        # Read FITS header
        try:
            cards = read_fits_header(fits_path)
            context['header_cards'] = format_header_for_display(cards)
            context['header_summary'] = get_header_summary(cards)
            context['total_cards'] = len(cards)
        except Exception as e:
            raise Http404(f"Error reading FITS header: {e}")
        
        context['observation'] = observation
        context['fits_filename'] = os.path.basename(fits_path)
        
        return context


class PdsLabelView(TemplateView):
    """Display PDS label for a file"""
    template_name = 'search/pds_label.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Check if archive is available
        if not is_archive_available():
            raise Http404("Archive files are not available")
        
        # Get observation
        try:
            observation = IdxMetaCommon.objects.select_related('idxfileid').get(pk=kwargs['pk'])
        except IdxMetaCommon.DoesNotExist:
            raise Http404("Observation not found")
        
        if not observation.has_file:
            raise Http404("No file associated with this observation")
        
        # Find PDS label file
        full_path = observation.idxfileid.get_full_path()
        if not full_path:
            raise Http404("File path not found")
        
        base_path = os.path.splitext(full_path)[0]
        label_path = find_pds_label_file(base_path)
        
        if not label_path:
            raise Http404("PDS label file not found (.lbl)")
        
        # Read PDS label
        try:
            with open(label_path, 'r', encoding='ascii', errors='replace') as f:
                label_content = f.read()
                
            # Split into lines for display with line numbers
            lines = label_content.split('\n')
            context['label_lines'] = [
                {'line_num': i + 1, 'text': line}
                for i, line in enumerate(lines)
            ]
        except Exception as e:
            raise Http404(f"Error reading PDS label: {e}")
        
        context['observation'] = observation
        context['label_filename'] = os.path.basename(label_path)
        context['total_lines'] = len(lines)
        
        return context
