# Discipline-Specific Metadata Display

## Overview

The IHW Django application now displays discipline-specific metadata for all observations. Each of the 9 main IHW networks has specialized metadata fields that capture scientific measurements and instrument parameters specific to that observing technique.

## Implementation

### Models (core/models.py)

Added 24 Django models representing the `idx_meta_*` tables:

**Amateur Studies (AMSN):**
- `IdxMetaAmdr` - Drawing observations (scale, aperture, power, etc.)
- `IdxMetaAmpg` - Photography (focal length, emulsion, exposure, etc.)
- `IdxMetaAmsp` - Spectroscopy (spectral range, resolution, dispersion)
- `IdxMetaAmvis` - Visual observations (magnitude, coma size, tail length)

**Professional Networks:**
- `IdxMetaAstrom` - Astrometry (RA/Dec, uncertainties, reference catalogs)
- `IdxMetaIrim` - Infrared Imaging (wavelength, bandwidth, aperture)
- `IdxMetaIrph` - Infrared Photometry
- `IdxMetaIrpol` - Infrared Polarimetry
- `IdxMetaIrsp` - Infrared Spectroscopy (spectral range, resolution)
- `IdxMetaLspn` - Large-Scale Phenomena (extensive FITS metadata, FOV, exposure)
- `IdxMetaMsnrdr`, `IdxMetaMsnvis` - Meteor Studies
- `IdxMetaNnsn` - Near-Nucleus Studies (filter, exposure, data quality)
- `IdxMetaPflx`, `IdxMetaPmag`, `IdxMetaPpol`, `IdxMetaPsto` - Photometry/Polarimetry
- `IdxMetaRscn`, `IdxMetaRsoc`, `IdxMetaRsoh`, `IdxMetaRsrdr`, `IdxMetaRssl`, `IdxMetaRsuv` - Radio Science
- `IdxMetaSpectra` - Optical Spectroscopy

All models:
- Use `managed=False` (read-only legacy database)
- Link to `IdxMetaCommon` via `meta_common_id` foreign key
- Include nullable fields for optional measurements

### Helper Functions

**`get_discipline_metadata_model(observation)`**
- Maps subnet code (AMV, LSPN, IRSP, etc.) to appropriate model class
- Handles alternative naming (AMV vs AMVIS)
- Returns `None` if no metadata table exists for discipline

**`get_discipline_metadata(observation)`**
- Fetches discipline-specific metadata instance for an observation
- Returns `None` if metadata doesn't exist or observation has no files
- Handles `DoesNotExist` exceptions gracefully

**`format_metadata_fields(metadata_obj)`**
- Converts model instance to list of (label, value) tuples
- Skips system fields (id, meta_common_id)
- Formats field names: `spectral_range_lo` → "Spectral Range (Low)"
- Filters out null/empty values for clean display

### View Integration (search/views.py)

`ObservationDetailView.get_context_data()` now:
1. Calls `get_discipline_metadata()` to fetch specialized data
2. Formats fields using `format_metadata_fields()`
3. Adds `discipline_metadata` to template context

### Template Display (templates/search/observation_detail.html)

New "Observation Metadata" card displays when `discipline_metadata` exists:
- Warning-colored header for visibility
- Striped table layout for readability
- 40% width labels, 60% width values
- Informational note explaining metadata source

## Examples

### Amateur Visual Observation (AMV)
**Observation:** 324005  
**Date:** 1985-04-07 09:21:36 UTC  
**Observer:** W.MARETT  

**Metadata Displayed:**
- Magnitude: 6.2
- Magnitude Estimation Method: B
- Chart: 6
- Coma Major Axis: 5.0
- Observing Conditions: 4
- Tail Length: 1.0°
- Tail Position Angle: 285°
- Aperture: 0.2032m
- Instrument: REF
- F-Ratio: 8.0
- Power: 32x
- Limiting Magnitude: 8.5

### Large-Scale Phenomena (LSPN)
**Observation:** 311991  
**Date:** 1986-03-03 17:00:00 UTC  
**Observer:** GERASIMENKO,S  

**Metadata Displayed:**
- Observer: GERASIMENKO,S
- Emulsion: ORWO ZU21
- Filter Name: NONE
- Exposure: 2699.4s
- Field of View X: 0.3058
- Field of View Y: 0.3058
- Data Quality: GOOD
- Observatory ID: 21
- Airmass (mid): 1.06
- Aperture: 0.4
- Number of Axes: 2
- X-Axis Size: 4096
- Y-Axis Size: 3072
- BITPIX: 16

### Infrared Spectroscopy (IRSP)
**Observation:** 312415  
**Date:** 1986-03-13 07:30:00 UTC  
**Observer:** MUMMA,M  

**Metadata Displayed:**
- Spectral Range (Low): 3.1147 µm
- Spectral Range (High): 3.6841 µm
- Resolution: 0.009
- Aperture: 5.0"
- Syscode: 25680100
- Observatory ID: 24

## Coverage

### Disciplines with Metadata (All 9)
✅ AMSN - Amateur Studies  
✅ ASTROM - Astrometry  
✅ IRSN - Infrared Studies  
✅ LSPN - Large-Scale Phenomena  
✅ MSN - Meteor Studies  
✅ NNSN - Near-Nucleus Studies  
✅ PPSN - Photometry & Polarimetry  
✅ RSN - Radio Science  
✅ SSSN - Spectroscopy & Spectrophotometry  

### Total Tables: 24 metadata tables modeled

## Technical Notes

### Field Name Mapping
Common abbreviations are expanded for user-friendliness:
- `lambda_eff` → "Effective Wavelength (λ)"
- `mag_gt` → "Magnitude >"
- `coma_maj` → "Coma Major Axis"
- `fov_x` → "Field of View X"
- `ref_cat` → "Reference Catalog"

### Missing Metadata
Not all observations have discipline-specific metadata:
- Some observations may only have basic `idx_meta_common` fields
- Metadata section won't display if no specialized data exists
- This is expected for certain observation types

### Database Considerations
- Metadata tables use same `id` sequence as observations (not PKs)
- `meta_common_id` is the foreign key linking to `IdxMetaCommon`
- Some tables have minimal fields (Meteor Studies)
- LSPN table has 90+ FITS header fields (abbreviated in model)

## Future Enhancements

Potential improvements for metadata display:

1. **Unit conversion** - Display distances in km/AU, wavelengths in nm/µm
2. **Linked fields** - Make observatory_id clickable to show observatory details
3. **Grouped display** - Organize fields by category (Instrument, Conditions, Measurements)
4. **Comparison view** - Show metadata side-by-side for multiple observations
5. **Export** - Include metadata in CSV/JSON exports
6. **Search filters** - Allow searching by specific metadata fields (e.g., wavelength range)

## Testing

Tested with observations from multiple disciplines:
- ✅ AMV/AMVIS (Amateur Visual) - Observation 324005
- ✅ LSPN (Large-Scale) - Observation 311991
- ✅ IRSP (Infrared Spectroscopy) - Observation 312415

All display correctly with properly formatted field names and values.

## Related Files

- `IHWApp/core/models.py` - Model definitions and helper functions (lines 215-740)
- `IHWApp/search/views.py` - View integration (lines 87-119)
- `IHWApp/templates/search/observation_detail.html` - Template display (lines 106-130)
- `plan.md` - Implementation planning and status

## Commit

Git commit: `ccfcd4e`  
Date: 2026-04-20  
Message: "Add discipline-specific metadata display"
