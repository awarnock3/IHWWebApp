"""
Search views for IHW archive
"""
from django.views.generic import FormView, ListView, DetailView
from django.db.models import Q
from core.models import IdxMetaCommon, IhwEphemeris
from .forms import ObservationSearchForm


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
        context = super().get_context_data(**kwargs)
        
        # Add ephemeris data
        context['ephemeris'] = self.object.get_ephemeris()
        
        # Add file paths if file exists
        if self.object.idxfileid:
            context['file_paths'] = self.object.idxfileid.get_file_paths()
        
        return context
