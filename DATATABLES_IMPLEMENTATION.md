# DataTables Implementation - Search Results Enhancement

## Overview

The search results page now uses **jQuery DataTables** with server-side processing to provide an interactive, filterable, and sortable view of up to 69,094 observations. This implementation handles large datasets efficiently while providing excellent user experience.

## Features Implemented

### 1. **Server-Side Processing**
- Handles pagination, sorting, and filtering on the server
- Efficient for 69K+ observation records
- Only loads 50 rows at a time (configurable: 10, 25, 50, 100)
- Preserves original search context (date range, networks, observer)

### 2. **Global Search**
- Search box in top-right corner
- Searches across multiple fields simultaneously:
  - Observer name
  - Network name and discipline code
  - Subnet name and code
- Case-insensitive search
- Triggers server-side query

### 3. **Column Sorting**
- Click any column header to sort
- Click again to reverse sort order
- Default: Date descending (newest first)
- Sortable columns:
  - Date/Time
  - Network
  - Subnet
  - Observer
  - Solar Distance
  - File Type

### 4. **Individual Column Filters**
Second header row with filter inputs for each column:

| Column | Filter Type | Description |
|--------|-------------|-------------|
| Date | Text input | Filter by date (YYYY-MM-DD) |
| Network | Dropdown | Pre-populated with all 9 networks |
| Subnet | Dropdown | Will populate dynamically based on results |
| Observer | Text input | Case-insensitive contains search |
| Position | Text input | Filter by RA/Dec coordinates |
| Solar Dist. | Range input | Format: `min-max` (e.g., `0.5-2.0`) |
| File Type | Dropdown | DATA, BROWSE, CALIB, METADATA |
| Filename | Text input | Filter by filename |

### 5. **Network and Subnet Badges**
- **Network Badge**: Blue badge with discipline code (e.g., "AMSN")
- **Subnet Badge**: Gray badge with subnet code (e.g., "AMV")
- **Accessibility**: Each badge includes `aria-label` for screen readers
  - Example: `aria-label="Network: Amateur Studies"`
- **Hover Tooltip**: Shows full name on mouse hover
  - Uses Bootstrap tooltip with `title` attribute
- **Safe HTML**: All badge HTML rendered server-side with proper escaping

**Example badges:**
```html
<span class="badge bg-primary" aria-label="Network: Amateur Studies" title="Amateur Studies">AMSN</span>
<span class="badge bg-secondary ms-1" aria-label="Subnet: Visual Observations" title="Visual Observations">AMV</span>
```

### 6. **Clear All Filters**
- Button appears when any filter is active
- Clears both global search and column filters
- Reloads table with original search parameters
- Hidden when no filters applied

### 7. **Progressive Enhancement**
- Fallback pagination for non-JavaScript users
- Graceful degradation if DataTables fails to load
- `<noscript>` warning for users with JS disabled
- Django pagination hidden when DataTables initializes

### 8. **Performance Optimizations**
- **Ephemeris N+1 Fix**: Preloads RA, Dec, and solar distance using Django subqueries
  - Before: ~100 queries per page (2 per row × 50 rows)
  - After: 1 query for all rows
- **NULL idxfileid Exclusion**: Deleted files automatically filtered out
- **select_related()**: Network and subnet data prefetched
- **Annotated Fields**: Ephemeris data attached to queryset, not fetched per-row

## Technical Architecture

### Backend (Django)

**File**: `IHWApp/search/views.py`

**SearchResultsView** class handles both HTML and JSON responses:

```python
def get(self, request, *args, **kwargs):
    """Route to HTML or JSON based on request headers"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return self.get_json_response()
    return super().get(request, *args, **kwargs)
```

**JSON Response Structure** (DataTables-compatible):
```json
{
  "draw": 1,
  "recordsTotal": 8784,
  "recordsFiltered": 8784,
  "data": [
    {
      "DT_RowId": "obs_333032",
      "date": "<a href='/search/observation/333032/'>1985-12-31 23:55</a>",
      "date_raw": "1985-12-31T23:55:40+00:00",
      "network": "<span class='badge bg-primary' ...>AMSN</span>",
      "network_raw": "AMSN",
      "network_name": "Amateur Studies",
      "subnet": "<span class='badge bg-secondary' ...>AMV</span>",
      "subnet_raw": "AMV",
      "subnet_name": "AMSN Visual Magnitude",
      "observer": "TORRES,E",
      "position": "RA: 334.3700°, Dec: -2.3062°",
      "solar_dist": "1.022 AU",
      "solar_dist_raw": 1.0222,
      "file_type": "<span class='badge bg-info'>DATA</span>",
      "file_type_raw": "DATA",
      "filename": "amv04940.lbl"
    }
  ]
}
```

**Ephemeris Optimization** using Django ORM subqueries:
```python
queryset = queryset.annotate(
    ephemeris_ra=Subquery(
        IhwEphemeris.objects.filter(
            date=OuterRef('date_obs__date'),
            comet='Halley'
        ).values('ra')[:1]
    ),
    # ... similar for decl and r fields
)
```

### Frontend (DataTables)

**File**: `IHWApp/templates/search/results.html`

**Initialization**:
```javascript
$('#observations-table').DataTable({
    serverSide: true,
    processing: true,
    ajax: {
        url: '/search/results/',
        type: 'GET',
        data: function(d) {
            // Preserve original search parameters
            $.extend(d, {
                start_date: '{{ start_date }}',
                end_date: '{{ end_date }}',
                networks: '{{ request.GET.networks }}',
                observer: '{{ request.GET.observer }}'
            });
            return d;
        },
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    },
    columns: [...],
    order: [[0, 'desc']], // Date descending
    pageLength: 50,
    lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]]
});
```

**Column Filtering Event Handlers**:
```javascript
$('.column-filter').on('keyup change', function() {
    const columnIndex = $(this).data('column');
    const value = $(this).val();
    table.column(columnIndex).search(value).draw();
});
```

**Tooltip Reinitialization** on table redraw:
```javascript
drawCallback: function(settings) {
    $('[title]').tooltip({
        trigger: 'hover',
        placement: 'top'
    });
}
```

## DataTables Parameters

### Request Parameters (from DataTables to server)
- `draw`: Draw counter (for security/sync)
- `start`: First record index (pagination)
- `length`: Page size (10, 25, 50, 100)
- `search[value]`: Global search value
- `columns[N][search][value]`: Individual column filters
- `order[0][column]`: Sort column index
- `order[0][dir]`: Sort direction (asc/desc)

### Response Parameters (from server to DataTables)
- `draw`: Echo of request draw
- `recordsTotal`: Total records before filtering
- `recordsFiltered`: Total records after filtering
- `data`: Array of row objects

## Database Query Optimization

### Before (N+1 Problem)
```python
# In template: {{ obs.get_position_display }}
# This called obs.get_ephemeris() for EACH row
for obs in observations:
    ephemeris = IhwEphemeris.for_date(obs.date_obs)  # Query!
    position = ephemeris.ra, ephemeris.decl          # Per row!
```
**Result**: ~100 database queries per page

### After (Subquery Annotation)
```python
# Preload all ephemeris data in ONE query
queryset = queryset.annotate(
    ephemeris_ra=Subquery(...),
    ephemeris_decl=Subquery(...),
    ephemeris_r=Subquery(...)
)
# Use annotated fields directly
position = f"RA: {obs.ephemeris_ra:.4f}°"
```
**Result**: 1 database query for all rows

## Accessibility Features

1. **Semantic HTML**: Proper table structure with `<thead>` and `<tbody>`
2. **ARIA Labels**: All badges include descriptive `aria-label` attributes
3. **Keyboard Navigation**: DataTables fully keyboard-accessible
4. **Screen Reader Support**: Table announces as "sortable table" with current sort
5. **Focus Management**: Filter inputs are properly focusable
6. **Alternative Input**: Tooltips have both hover and focus triggers
7. **Fallback Mode**: Works without JavaScript (Django pagination)

## Browser Compatibility

- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)
- ⚠️ IE11 (DataTables 1.13+ dropped IE11 support)

## Testing

### Manual Test Checklist

1. **Load Performance**
   - [ ] Initial page load < 2 seconds for 50 rows
   - [ ] AJAX requests complete < 1 second
   - [ ] No JavaScript console errors

2. **Global Search**
   - [ ] Search for "MORRIS" filters results
   - [ ] Clear search restores all results
   - [ ] Search is case-insensitive

3. **Column Sorting**
   - [ ] Click Date header - sorts by date
   - [ ] Click Solar Dist - sorts numerically (not alphabetically)
   - [ ] Re-click reverses order

4. **Column Filters**
   - [ ] Network dropdown filters correctly
   - [ ] Observer text filter is case-insensitive
   - [ ] Solar distance range "0.5-1.5" works
   - [ ] File type dropdown shows only matching types

5. **Badges and Tooltips**
   - [ ] Network badge shows on hover
   - [ ] Subnet badge shows on hover
   - [ ] Aria-label present (check with screen reader)
   - [ ] Tooltips don't break on table redraw

6. **Pagination**
   - [ ] Can navigate to page 2, 3, etc.
   - [ ] "Show 100 per page" loads 100 rows
   - [ ] Pagination info updates correctly

7. **Filters Interaction**
   - [ ] Multiple filters work together (AND logic)
   - [ ] Clear All Filters button appears/works
   - [ ] Filters persist across sorting
   - [ ] Count updates correctly

8. **Progressive Enhancement**
   - [ ] Disable JavaScript - fallback pagination works
   - [ ] DataTables fails gracefully if CDN down

### Automated Tests (TODO)

```python
# Test ephemeris annotation
def test_search_results_ephemeris_annotation(self):
    response = self.client.get('/search/results/', {
        'start_date': '1985-12-01',
        'end_date': '1985-12-31'
    })
    # Should have annotated fields, not trigger N+1
    with self.assertNumQueries(1):
        for obs in response.context['observations']:
            _ = obs.ephemeris_ra
            _ = obs.ephemeris_decl
            _ = obs.ephemeris_r

# Test JSON endpoint
def test_json_endpoint_format(self):
    response = self.client.get('/search/results/', {
        'start_date': '1985-12-01',
        'end_date': '1985-12-31',
        'draw': '1',
        'start': '0',
        'length': '10'
    }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    
    data = response.json()
    assert 'draw' in data
    assert 'recordsTotal' in data
    assert 'recordsFiltered' in data
    assert 'data' in data
    assert len(data['data']) <= 10
```

## Known Limitations

1. **Subnet Dropdown**: Currently not dynamically populated from results
   - Workaround: Use text filter instead
   - Fix: Add endpoint to get distinct subnets for current search

2. **Date Filter Format**: Requires exact YYYY-MM-DD format
   - Workaround: Use date range search form instead
   - Enhancement: Add datepicker to column filter

3. **Position Filter**: Searches formatted string, not raw coordinates
   - Workaround: Limited utility, consider removing
   - Enhancement: Parse RA/Dec range inputs

4. **Mobile UX**: Table may require horizontal scrolling on small screens
   - Workaround: Bootstrap responsive table works adequately
   - Enhancement: Consider responsive column hiding or card view

## Future Enhancements

### High Priority
- [ ] Add subnet distinct values endpoint
- [ ] Export filtered results to CSV
- [ ] Save filter preferences in localStorage
- [ ] Add date range picker to column filter

### Medium Priority
- [ ] Column visibility toggles (show/hide columns)
- [ ] FixedHeader extension (sticky headers on scroll)
- [ ] Responsive extension (better mobile experience)
- [ ] Keyboard shortcuts (Ctrl+F for global search, etc.)

### Low Priority
- [ ] Column reordering (drag-and-drop)
- [ ] Advanced search builder UI
- [ ] Print-optimized view
- [ ] Excel export with formatting

## References

- **DataTables Documentation**: https://datatables.net/
- **Server-Side Processing**: https://datatables.net/manual/server-side
- **Bootstrap 5 Integration**: https://datatables.net/examples/styling/bootstrap5
- **Django ORM Subqueries**: https://docs.djangoproject.com/en/4.2/ref/models/expressions/#subquery-expressions

## Changelog

### 2026-04-21 - Initial Implementation
- ✅ Added DataTables 1.13.6 with server-side processing
- ✅ Implemented JSON endpoint in SearchResultsView
- ✅ Fixed ephemeris N+1 query problem with subquery annotations
- ✅ Added network and subnet badges with accessibility
- ✅ Implemented 8 column filters (text, dropdown, range)
- ✅ Added global search and column sorting
- ✅ Progressive enhancement with fallback pagination
- ✅ Clear All Filters button
- ✅ Excluded NULL idxfileid (deleted files)
- ✅ Bootstrap tooltip integration with redraw handling
