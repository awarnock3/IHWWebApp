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

#### File Downloads
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
- [ ] Add API documentation (if REST API built)
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

## 🐛 Known Issues

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
