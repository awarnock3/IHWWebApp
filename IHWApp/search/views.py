"""
Search views for IHW archive
"""
from django.views.generic import FormView, ListView, DetailView, TemplateView
from django.db.models import Q, F, OuterRef, Subquery, Exists
from django.http import Http404, HttpResponse, JsonResponse
from core.models import IdxMetaCommon, IhwEphemeris, IhwFiles, IhwFileFilepath, IhwFilepath
from core.fits_utils import read_fits_header, format_header_for_display, get_header_summary
from core.archive_utils import is_archive_available, find_fits_header_file, find_pds_label_file
from .forms import ObservationSearchForm
import os
from datetime import datetime


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
        
        if form.cleaned_data.get('min_solar_distance') is not None:
            params['min_solar_dist'] = str(form.cleaned_data['min_solar_distance'])
        
        if form.cleaned_data.get('max_solar_distance') is not None:
            params['max_solar_dist'] = str(form.cleaned_data['max_solar_distance'])
        
        return redirect('/search/results/?' + urlencode(params))


class SearchResultsView(ListView):
    """Display search results with DataTables support"""
    model = IdxMetaCommon
    template_name = 'search/results.html'
    context_object_name = 'observations'
    paginate_by = 50
    
    def get_base_queryset(self):
        """Get base queryset with all filters applied"""
        # Exclude observations with NULL idxfileid (deleted files)
        queryset = IdxMetaCommon.objects.exclude(idxfileid__isnull=True)
        
        queryset = queryset.select_related(
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
        
        # Solar distance filter (optional)
        min_solar_dist = self.request.GET.get('min_solar_dist')
        max_solar_dist = self.request.GET.get('max_solar_dist')
        
        if min_solar_dist or max_solar_dist:
            # Need to join with ephemeris table for filtering
            from django.db.models import Exists, OuterRef
            
            ephemeris_filter = IhwEphemeris.objects.filter(
                date=OuterRef('date_obs__date'),
                comet='Halley'
            )
            
            if min_solar_dist:
                try:
                    ephemeris_filter = ephemeris_filter.filter(r__gte=float(min_solar_dist))
                except (ValueError, TypeError):
                    pass
            
            if max_solar_dist:
                try:
                    ephemeris_filter = ephemeris_filter.filter(r__lte=float(max_solar_dist))
                except (ValueError, TypeError):
                    pass
            
            queryset = queryset.filter(Exists(ephemeris_filter))
        
        return queryset
    
    def get_queryset(self):
        """Get queryset with ephemeris data preloaded to avoid N+1 queries"""
        queryset = self.get_base_queryset()
        
        # Preload ephemeris data using subquery to avoid N+1
        # Find ephemeris entry matching observation date
        ephemeris_subquery = IhwEphemeris.objects.filter(
            date=OuterRef('date_obs__date'),
            comet='Halley'
        ).values('ra')[:1]
        
        queryset = queryset.annotate(
            ephemeris_ra=Subquery(
                IhwEphemeris.objects.filter(
                    date=OuterRef('date_obs__date'),
                    comet='Halley'
                ).values('ra')[:1]
            ),
            ephemeris_decl=Subquery(
                IhwEphemeris.objects.filter(
                    date=OuterRef('date_obs__date'),
                    comet='Halley'
                ).values('decl')[:1]
            ),
            ephemeris_r=Subquery(
                IhwEphemeris.objects.filter(
                    date=OuterRef('date_obs__date'),
                    comet='Halley'
                ).values('r')[:1]
            ),
        )
        
        return queryset.order_by('-date_obs')
    
    def get(self, request, *args, **kwargs):
        """Handle both HTML and JSON requests for DataTables"""
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
            return self.get_json_response()
        return super().get(request, *args, **kwargs)
    
    def get_json_response(self):
        """Return DataTables-compatible JSON response"""
        # DataTables parameters
        draw = int(self.request.GET.get('draw', 1))
        start = int(self.request.GET.get('start', 0))
        length = int(self.request.GET.get('length', 50))
        search_value = self.request.GET.get('search[value]', '')
        
        # Get base queryset
        queryset = self.get_queryset()
        
        # Apply global search across multiple fields
        if search_value:
            queryset = queryset.filter(
                Q(observer__icontains=search_value) |
                Q(network__name__icontains=search_value) |
                Q(network__discipline__icontains=search_value) |
                Q(idxfileid__subnet__subnet__icontains=search_value)
            )
        
        # Apply individual column filters
        # Column 0: Date
        date_filter = self.request.GET.get('columns[0][search][value]', '')
        if date_filter:
            try:
                filter_date = datetime.fromisoformat(date_filter).date()
                queryset = queryset.filter(date_obs__date=filter_date)
            except:
                pass
        
        # Column 1: Network
        network_filter = self.request.GET.get('columns[1][search][value]', '')
        if network_filter:
            queryset = queryset.filter(network__discipline__iexact=network_filter)
        
        # Column 2: Subnet
        subnet_filter = self.request.GET.get('columns[2][search][value]', '')
        if subnet_filter:
            queryset = queryset.filter(idxfileid__subnet__subnet__iexact=subnet_filter)
        
        # Column 3: Observer
        observer_filter = self.request.GET.get('columns[3][search][value]', '')
        if observer_filter:
            queryset = queryset.filter(observer__icontains=observer_filter)
        
        # Column 5: Solar Distance (range filter)
        solar_dist_filter = self.request.GET.get('columns[5][search][value]', '')
        if solar_dist_filter and '-' in solar_dist_filter:
            try:
                min_dist, max_dist = solar_dist_filter.split('-')
                queryset = queryset.filter(
                    ephemeris_r__gte=float(min_dist),
                    ephemeris_r__lte=float(max_dist)
                )
            except:
                pass
        
        # Column 6: File Type
        file_type_filter = self.request.GET.get('columns[6][search][value]', '')
        if file_type_filter:
            queryset = queryset.filter(idxfileid__type__iexact=file_type_filter)
        
        # Get total counts
        records_total = self.get_base_queryset().count()
        records_filtered = queryset.count()
        
        # Apply ordering
        order_column = int(self.request.GET.get('order[0][column]', 0))
        order_dir = self.request.GET.get('order[0][dir]', 'desc')
        
        order_fields = {
            0: 'date_obs',
            1: 'network__discipline',
            2: 'idxfileid__subnet__subnet',
            3: 'observer',
            5: 'ephemeris_r',
            6: 'idxfileid__type',
        }
        
        if order_column in order_fields:
            order_field = order_fields[order_column]
            if order_dir == 'desc':
                order_field = '-' + order_field
            queryset = queryset.order_by(order_field)
        
        # Pagination
        observations = queryset[start:start + length]
        
        # Build data array
        data = []
        for obs in observations:
            # Format RA/Dec from preloaded ephemeris
            if obs.ephemeris_ra is not None and obs.ephemeris_decl is not None:
                position = f"RA: {obs.ephemeris_ra:.4f}°, Dec: {obs.ephemeris_decl:.4f}°"
            else:
                position = "N/A"
            
            # Format solar distance from preloaded ephemeris
            if obs.ephemeris_r is not None:
                solar_dist = f"{obs.ephemeris_r:.3f} AU"
                solar_dist_raw = obs.ephemeris_r
            else:
                solar_dist = "N/A"
                solar_dist_raw = None
            
            # Network and subnet badges (server-side rendering with safe escaping)
            network_badge = f'<span class="badge bg-primary" aria-label="Network: {obs.network.name}" title="{obs.network.name}">{obs.network.discipline}</span>'
            
            if obs.idxfileid and obs.idxfileid.subnet:
                subnet_badge = f'<span class="badge bg-secondary ms-1" aria-label="Subnet: {obs.idxfileid.subnet.subnet_name or obs.idxfileid.subnet.subnet}" title="{obs.idxfileid.subnet.subnet_name or obs.idxfileid.subnet.subnet}">{obs.idxfileid.subnet.subnet}</span>'
            else:
                subnet_badge = '<span class="text-muted">—</span>'
            
            # File type badge
            if obs.idxfileid:
                file_type_badge = f'<span class="badge bg-info">{obs.idxfileid.type}</span>'
                filename = obs.idxfileid.filename
            else:
                file_type_badge = '<span class="text-muted">—</span>'
                filename = ''
            
            # Detail link
            detail_url = f'/search/observation/{obs.pk}/'
            date_link = f'<a href="{detail_url}">{obs.date_obs.strftime("%Y-%m-%d %H:%M")}</a>'
            
            data.append({
                'DT_RowId': f'obs_{obs.pk}',
                'date': date_link,
                'date_raw': obs.date_obs.isoformat(),
                'network': network_badge,
                'network_raw': obs.network.discipline,
                'network_name': obs.network.name,
                'subnet': subnet_badge,
                'subnet_raw': obs.idxfileid.subnet.subnet if obs.idxfileid and obs.idxfileid.subnet else '',
                'subnet_name': obs.idxfileid.subnet.subnet_name if obs.idxfileid and obs.idxfileid.subnet else '',
                'observer': obs.observer[:50] + '...' if len(obs.observer) > 50 else obs.observer,
                'position': position,
                'solar_dist': solar_dist,
                'solar_dist_raw': solar_dist_raw,
                'file_type': file_type_badge,
                'file_type_raw': obs.idxfileid.type if obs.idxfileid else '',
                'filename': filename,
            })
        
        return JsonResponse({
            'draw': draw,
            'recordsTotal': records_total,
            'recordsFiltered': records_filtered,
            'data': data,
        })
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add search parameters to context for display
        context['start_date'] = self.request.GET.get('start_date')
        context['end_date'] = self.request.GET.get('end_date')
        context['observer_query'] = self.request.GET.get('observer', '')
        
        # Add result count
        context['total_results'] = self.get_base_queryset().count()
        
        # Preload ephemeris for current page to use annotated data
        context['use_annotated_ephemeris'] = True
        
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


class AboutView(TemplateView):
    """About page for IHW Archive"""
    template_name = 'about.html'


class DocumentationView(ListView):
    """Display all documentation files from the archive"""
    model = IhwFiles
    template_name = 'documentation.html'
    context_object_name = 'documents'
    
    def get_queryset(self):
        """Get all files where type='DOCUMENT'"""
        # Get documents with their paths
        queryset = IhwFiles.objects.filter(type='DOCUMENT').select_related('subnet')
        
        # Annotate with file paths
        documents = []
        for doc in queryset:
            # Get all paths for this file
            paths = IhwFileFilepath.objects.filter(fileid=doc).select_related('filepathid')
            if paths.exists():
                # Use the first path (most files have only one)
                doc.dirpath = paths.first().filepathid.dirpath
            else:
                doc.dirpath = ''
            documents.append(doc)
        
        return documents
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_documents'] = len(context['documents'])
        context['archive_available'] = is_archive_available()
        return context


class FileViewerView(TemplateView):
    """Generic file viewer for documentation and other text files"""
    template_name = 'file_viewer.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Check if archive is available
        if not is_archive_available():
            raise Http404("Archive files are not available")
        
        # Get file by ID
        try:
            file_obj = IhwFiles.objects.select_related('subnet').get(pk=kwargs['file_id'])
        except IhwFiles.DoesNotExist:
            raise Http404("File not found")
        
        # Get full path
        full_path = file_obj.get_full_path()
        if not full_path or not os.path.exists(full_path):
            raise Http404("File not found in archive")
        
        # Try to read the file
        try:
            # Try common text encodings
            for encoding in ['utf-8', 'ascii', 'latin-1']:
                try:
                    with open(full_path, 'r', encoding=encoding, errors='replace') as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            else:
                # If all encodings fail, read as binary and show hex
                with open(full_path, 'rb') as f:
                    binary_content = f.read(1024)  # First 1KB
                context['is_binary'] = True
                context['binary_preview'] = binary_content.hex()
                context['file'] = file_obj
                context['filename'] = os.path.basename(full_path)
                context['full_path'] = full_path
                return context
            
            # Split into lines for display
            lines = content.split('\n')
            context['file_lines'] = [
                {'line_num': i + 1, 'text': line}
                for i, line in enumerate(lines[:1000])  # Limit to first 1000 lines
            ]
            context['total_lines'] = len(lines)
            context['truncated'] = len(lines) > 1000
            
        except Exception as e:
            raise Http404(f"Error reading file: {e}")
        
        context['file'] = file_obj
        context['filename'] = os.path.basename(full_path)
        context['full_path'] = full_path
        context['is_binary'] = False
        
        return context
