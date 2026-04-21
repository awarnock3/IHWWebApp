# IHW Django Archive - TODO List

**Last Updated:** 2026-04-20  
**Current Phase:** Phase 7 - File Downloads

---

## ✅ Completed

### Phase 1: Foundation
- [x] Django 6.0.4 upgrade in virtual environment
- [x] MariaDB connection configured
- [x] Core models created (7 tables)
- [x] All models use `managed=False` for legacy database

### Phase 2: First Vertical Slice
- [x] Date-based search interface with Bootstrap 5 UI
- [x] Search by date range, discipline, observer name
- [x] Results table with pagination (50 per page)
- [x] Observation detail view with ephemeris data
- [x] Quick date shortcuts for key observation periods

### Phase 3: Date Format & Testing
- [x] Fixed date input format to YYYY-MM-DD (international-friendly)
- [x] Unit tests for models (7 tests) and forms/views (7 tests)
- [x] Test environment uses SQLite in-memory
- [x] All 14 tests passing with MariaDB

### Phase 4: FITS Header & PDS Label Viewers
- [x] Pure Python FITS reader (no dependencies)
- [x] FITS header viewer with line numbers
- [x] PDS label viewer with line numbers
- [x] Support for .fit, .fits, and separate .hdr files
- [x] Configurable archive root (IHW_ARCHIVE_ROOT setting)
- [x] Relative path display in UI
- [x] Graceful degradation when archive unavailable

### Phase 5: UI Polish
- [x] Added "File Type" column to results table
- [x] Improved navigation (Back to Results vs New Search)
- [x] Breadcrumb navigation on detail pages
- [x] File metadata viewer buttons conditionally displayed

### Phase 6: Discipline-Specific Metadata Display
- [x] Created 24 Django models for idx_meta_* tables
- [x] Subnet to metadata table mapping
- [x] Dynamic metadata fetch in ObservationDetailView
- [x] Formatted field name display (snake_case → Title Case)
- [x] Tested with AMV, LSPN, IRSP observations

---

## 🚧 In Progress

Nothing currently in progress.

---

## 📋 TODO - Prioritized

### High Priority

#### UI Improvements for Database-Only Mode
These features enhance the UI without requiring archive files, making the interface fully functional with just the database.

##### Results Table Enhancements
- [ ] **Add subnet badge to search results**
  - Show both network and subnet badges in results table
  - Replace descriptive text with compact badges
  - Add hover tooltips showing full network/subnet names
  - Example: Badges "AMSN" and "AMV" with hover "Amateur Studies" / "Visual Observations"
  
- [ ] **Client-side column filtering**
  - Add filter controls to each column header in results table
  - Allow filtering by network, subnet, observer, date range, etc.
  - Filter without re-executing database query
  - Use JavaScript for instant filtering of visible results
  - Preserve filters across pagination
  - Consider using DataTables.js or similar library

##### Search Form Enhancements
- [ ] **Add solar distance search filter**
  - Add distance range inputs (min/max in AU)
  - Query against ephemeris data (ihw_ephemeris.r field)
  - Combine with existing date/observer/network filters
  - Help text: "Distance from Sun in Astronomical Units (AU)"
  - Consider preset ranges: "Perihelion (< 1 AU)", "All observations"

##### Metadata Display Enhancements
- [ ] **Show ALL metadata fields initially (expansive approach)**
  - Display every non-null field from metadata tables
  - Don't hide any fields based on assumptions
  - Create comprehensive view first
  - Add notes/issue markers for fields we decide to omit later
  - This allows us to see what's actually available before filtering
  - Update field_labels dict to cover all possible fields
  - **IMPORTANT:** Many fields currently missing from models:
    - IdxMetaLspn: 71 of 88 fields missing (FITS header fields like CRVAL1, CRPIX1, WCS, etc.)
    - Need to add all fields to see what data actually exists
    - Then decide which are useful vs noise
  - Consider grouping fields by category in display (Instrument, WCS, Processing, etc.)
  - Add "Show All Fields" / "Show Summary" toggle

#### File Downloads
**Note:** Lower priority than UI enhancements above. Archive files not always available.

- [ ] Create FileDownloadView with proper Content-Type headers
- [ ] Support FITS files (.fit, .fits)
- [ ] Support other file types (PDS labels, catalogs, etc.)
- [ ] Add download button to observation detail page
- [ ] Use FileResponse or X-Sendfile for efficient delivery
- [ ] Add error handling for missing files
- [ ] Optional: Add download logging/tracking
- [ ] Test with various file sizes

#### Database Consistency Scanning
- [ ] Create generic network scanner (based on AMV scan)
- [ ] Scan remaining 8 networks for issues:
  - [ ] AMDR (Drawing)
  - [ ] AMPG (Photography)
  - [ ] AMSP (Spectroscopy)
  - [ ] ASTROM (Astrometry)
  - [ ] IRSN networks (4 subnets)
  - [ ] LSPN (Large-Scale)
  - [ ] MSN (Meteor)
  - [ ] NNSN (Near-Nucleus)
  - [ ] PPSN (Photometry/Polarimetry)
  - [ ] RSN (Radio Science - 6 subnets)
  - [ ] SSSN (Spectroscopy)
- [ ] Document all findings in DATABASE_INCONSISTENCIES.md
- [ ] Create prioritized fix list

### Medium Priority

#### REST API Development
**Status:** Design phase
**Framework:** Django REST Framework (DRF) recommended

**Core Endpoints:**
- [ ] **Search API**
  - `GET /api/v1/observations/` - List/search observations with filtering
    - Query params: start_date, end_date, network, subnet, observer, min_distance, max_distance
    - Pagination support (limit/offset or cursor-based)
    - Returns: observation list with basic fields + links to detail endpoints
  - `GET /api/v1/observations/{id}/` - Single observation details
  - `GET /api/v1/observations/{id}/metadata/` - Discipline-specific metadata
  - `GET /api/v1/observations/{id}/ephemeris/` - Ephemeris data for observation date
  - `GET /api/v1/observations/{id}/files/` - List associated files

- [ ] **FITS/PDS API**
  - `GET /api/v1/observations/{id}/fits-header/` - FITS header as JSON
  - `GET /api/v1/observations/{id}/pds-label/` - PDS label as JSON
  - Raw text versions available with `Accept: text/plain` header

- [ ] **Reference Data APIs**
  - `GET /api/v1/networks/` - List all networks
  - `GET /api/v1/subnets/` - List all subnets (filterable by network)
  - `GET /api/v1/observatories/` - List observatories
  - `GET /api/v1/observatories/{id}/` - Observatory details
  - `GET /api/v1/observers/` - List unique observers (searchable)

- [ ] **Ephemeris API**
  - `GET /api/v1/ephemeris/` - Query ephemeris by date range
  - `GET /api/v1/ephemeris/{date}/` - Single date ephemeris
  - Returns: heliocentric distance, geocentric distance, phase angle, etc.

- [ ] **Statistics API**
  - `GET /api/v1/stats/summary/` - Overall dataset statistics
  - `GET /api/v1/stats/by-network/` - Observation counts by network
  - `GET /api/v1/stats/by-date/` - Timeline data (observations per day/month)

**API Features:**
- [ ] Authentication (optional - API key or OAuth2 for rate limiting)
- [ ] Rate limiting (e.g., 100 requests/hour for unauthenticated)
- [ ] CORS support for browser-based clients
- [ ] API versioning (`/api/v1/`)
- [ ] OpenAPI/Swagger documentation
- [ ] Response format: JSON (with option for CSV export on search endpoints)
- [ ] Error handling: Standard HTTP codes + error detail objects
- [ ] Filtering, sorting, pagination standards across all list endpoints
- [ ] Field selection: `?fields=id,date,observer` to limit response size
- [ ] Expansion: `?expand=metadata,ephemeris` to include related data

**Implementation Notes:**
- Use Django REST Framework serializers for all models
- Implement ViewSets for consistent CRUD operations
- Add URL router configuration (`urls.py`)
- Consider read-only API initially (no POST/PUT/DELETE)
- Archive file downloads via API only when archive available
- Document all endpoints in OpenAPI format
- Add rate limiting with `django-ratelimit` or DRF throttling
- Consider ETags/caching headers for performance
- Add HATEOAS links for discoverability

**Use Cases:**
- Automated data analysis pipelines
- External visualization tools
- Mobile apps
- Third-party integrations
- Bulk data extraction for research
- Monitoring/alerting systems

**Example Response Format:**
```json
{
  "count": 69094,
  "next": "/api/v1/observations/?page=2",
  "previous": null,
  "results": [
    {
      "id": 324005,
      "date": "1985-12-07T00:00:00Z",
      "network": "AMSN",
      "subnet": "AMV",
      "observer": "John Doe",
      "files_count": 2,
      "has_metadata": true,
      "links": {
        "self": "/api/v1/observations/324005/",
        "metadata": "/api/v1/observations/324005/metadata/",
        "files": "/api/v1/observations/324005/files/"
      }
    }
  ]
}
```

#### Enhanced Metadata Display
- [ ] Add unit conversion (distances in km/AU, wavelengths in nm/µm)
- [ ] Make observatory_id clickable (link to observatory details)
- [ ] Group metadata fields by category (Instrument, Conditions, Measurements)
- [ ] Add tooltips for technical terms
- [ ] Show metadata field definitions on hover

#### Observatory Data
- [ ] Create IhwObservatory model
- [ ] Display observatory details (name, location, coordinates)
- [ ] Link from observation metadata
- [ ] Add observatory search/filter

#### Advanced Search Features
- [ ] Coordinate range search (RA/Dec boxes)
- [ ] Object type filtering
- [ ] Multiple date range periods (OR logic)
- [ ] Full-text search in observer notes
- [ ] Metadata field filters (wavelength, magnitude, etc.)
- [ ] Export search results (CSV, JSON formats)
- [ ] Save search queries

### Low Priority

#### Documentation Improvements
- [ ] OpenAPI/Swagger API documentation
- [ ] API client examples (Python, JavaScript, curl)
- [ ] User guide with screenshots
- [ ] Developer setup guide
- [ ] Database schema diagram
- [ ] Data quality documentation

#### Archive Administration Tools
- [ ] File integrity checker (MD5 verification)
- [ ] Broken link detector
- [ ] Archive statistics dashboard
- [ ] Batch file operations
- [ ] Data quality flags/reporting

#### Performance Optimization
- [ ] Add database indexes for common queries
- [ ] Implement query result caching
- [ ] Optimize large result set pagination
- [ ] Add database query logging
- [ ] Profile slow pages

#### UI Enhancements
- [ ] Dark mode toggle
- [ ] Responsive mobile layout improvements
- [ ] Keyboard navigation shortcuts
- [ ] Print-friendly observation detail pages
- [ ] Observation comparison view (side-by-side)

---

## 📝 Implementation Notes

### Client-Side Filtering (Search Results)
**Approach Options:**
1. **DataTables.js** (Recommended)
   - Full-featured table plugin with built-in filtering, sorting, pagination
   - Works with server-side or client-side data
   - Large community, well-documented
   - ~50KB minified

2. **Custom JavaScript**
   - Lighter weight
   - More control over UI/UX
   - More work to implement
   - Need to handle pagination interaction

3. **Hybrid Approach**
   - Filter current page results immediately (JavaScript)
   - Add "Apply Filter to All Results" button (server-side)
   - Best of both worlds but more complex

**Considerations:**
- Results already paginated (50 per page)
- Client-side filtering only affects visible results
- May want to show "Showing X of Y results (Z filtered)" message
- Preserve filter state in URL parameters or localStorage

### Solar Distance Search
**Implementation:**
- Add range inputs to search form (min_distance, max_distance)
- Join query with ihw_ephemeris table
- Match observation date to ephemeris date (already have for_date() method)
- Filter on ihw_ephemeris.r field (AU from Sun)
- Useful ranges:
  - Perihelion: < 1.0 AU
  - Inner solar system: < 2.0 AU
  - All observations: 0.5 - 6.0 AU (typical range for Halley)
- Add preset buttons for common ranges
- Handle ephemeris data gaps gracefully

### Subnet Badge Display
**Design:**
- Network badge: `bg-secondary` (existing)
- Subnet badge: `bg-info` or `bg-primary` (new)
- Both with Bootstrap tooltips
- Example: `<span class="badge bg-secondary" data-bs-toggle="tooltip" title="Amateur Studies">AMSN</span>`
- Space-efficient: removes verbose text, keeps table compact
- Mobile-friendly: tooltips work on touch devices

### Comprehensive Metadata Display
**Phased Approach:**
1. **Phase 1:** Add ALL missing fields to models (71 fields for LSPN, others TBD)
2. **Phase 2:** Display all non-null fields without filtering
3. **Phase 3:** Group by category (Instrument, WCS Coordinates, Processing, Comments)
4. **Phase 4:** Add toggle for "Summary" vs "All Fields" view
5. **Phase 5:** User feedback - decide what to hide by default

**Field Categories (LSPN example):**
- **Instrument:** aperture, fratio, detector, cameraid, chip_id
- **Observation:** exposure, filter_name, emulsion, fov_x, fov_y
- **WCS (World Coordinate System):** crval1, crval2, crpix1, crpix2, crota1, crota2, cdelt1, cdelt2
- **Image Data:** naxis, naxis1, naxis2, bitpix, bscale, bzero, blank
- **Processing:** bunit, dat_form, dat_type, scaling info
- **Location:** lat_obs, long_obs, elev_obs, equinox
- **Calibration:** ncalspot, ncalwdge, cometmax, skyden, skymin
- **Metadata:** date_pds, date_prc, date_rec, date_rel, date_wrt
- **Comments:** cmts_anl, cmts_log, cmts_obs, cmts_prc, obs_cmts, log_cmts

---

## 🐛 Known Issues

### ~~RSN Metadata Models~~ (FIXED 2026-04-20)
- ~~RSN observation pages were failing with SQL column errors~~
- ~~Fixed by correcting model field definitions to match actual schema~~
- ~~All 6 RSN subnets now working correctly~~

### Database Issues (Documented in DATABASE_INCONSISTENCIES.md)

**AMV/AMVIS Subnet (AMSN Visual Observations):**
- 11,643 separate .hdr files (should be concatenated)
- 22,732 orphaned files (66.1% not linked to observations)
- System handles gracefully but not ideal for long-term archive

**Other Networks:**
- Not yet scanned (scanning in progress/planned)

### Test Issues
- 3 unit tests fail with SQLite (form choices need real tables)
- Tests pass with MariaDB
- Need to mock ModelChoiceField for SQLite tests

---

## 💡 Ideas / Future Enhancements

### Data Visualization
- [ ] Comet position plot over time
- [ ] Observation frequency timeline
- [ ] Discipline participation chart
- [ ] Interactive sky map

### Integration
- [ ] SIMBAD astronomical database lookups
- [ ] VO (Virtual Observatory) table access
- [ ] FITS header WCS coordinate display
- [ ] Link to external archives

### Collaboration
- [ ] User accounts and saved searches
- [ ] Observation annotations
- [ ] Data quality feedback system
- [ ] Citation export (BibTeX, etc.)

### Bulk Operations
- [ ] Batch download (zip multiple files)
- [ ] Bulk metadata export
- [ ] Query API for programmatic access
- [ ] Data synchronization tools

---

## 📝 Notes

### When Adding TODOs:
1. Add to appropriate priority section
2. Use `[ ]` for incomplete, `[x]` for complete
3. Include brief description of task
4. Link to issues/documentation if relevant
5. Update "Last Updated" date

### When Completing TODOs:
1. Mark with `[x]`
2. Move to "✅ Completed" section (with phase grouping)
3. Update git commit in notes
4. Update plan.md if major milestone

### Dependencies:
- File downloads requires archive to be mounted
- Advanced search may require new database indexes
- Some features may need Django migrations (if we add new tables)

---

## 🔗 Related Documents

- **plan.md** - Detailed implementation plans and notes
- **DATABASE_INCONSISTENCIES.md** - Known database issues
- **METADATA_DISPLAY.md** - Metadata feature documentation
- **FITS_PDS_IMPLEMENTATION.md** - FITS/PDS viewer details
- **ARCHIVE_CONFIGURATION.md** - Archive setup and graceful degradation
- **SESSION_SUMMARY.md** - Daily session summaries
