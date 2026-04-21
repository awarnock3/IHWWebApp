# Metadata Model Completeness Audit

**Date:** 2026-04-21  
**Purpose:** Identify missing fields in Django metadata models compared to actual database schema

---

## Executive Summary

- **Total metadata tables:** 25
- **Complete models:** 11 (44%)
- **Incomplete models:** 14 (56%)
- **Total missing fields:** 266 fields across 14 tables

### Severity Breakdown

**Critical (50+ missing fields):**
- `idx_meta_lspn`: **71 missing** (88 total → 17 in model)

**High (20-49 missing):**
- `idx_meta_msnrdr`: **47 missing** (49 total → 2 in model)
- `idx_meta_nnsn`: **23 missing** (29 total → 6 in model)

**Medium (10-19 missing):**
- `idx_meta_astrom`: **19 missing** (23 total → 18 in model - has extras?)
- `idx_meta_spectra`: **19 missing** (23 total → 8 in model)
- `idx_meta_psto`: **16 missing** (18 total → 7 in model)
- `idx_meta_ppol`: **15 missing** (17 total → 7 in model)
- `idx_meta_pmag`: **13 missing** (15 total → 7 in model)
- `idx_meta_pflx`: **13 missing** (16 total → 7 in model)
- `idx_meta_msnvis`: **12 missing** (14 total → 2 in model)

**Low (< 10 missing):**
- `idx_meta_amsp`: **7 missing** (14 total → 16 in model - has extras?)
- `idx_meta_ampg`: **5 missing** (14 total → 14 in model - name mismatch?)
- `idx_meta_irim`: **5 missing** (9 total → 7 in model)
- `idx_meta_irph`: **1 missing** (5 total → 7 in model - has extras?)

---

## Detailed Findings

### ✅ Complete Models (11 tables)

These models have all database fields defined:

1. **idx_meta_common** (11 fields) - Base observation metadata
2. **idx_meta_amdr** (12 fields) - Amateur Drawing
3. **idx_meta_amvis** (27 fields) - Amateur Visual Magnitude
4. **idx_meta_irpol** (4 fields) - Infrared Polarimetry
5. **idx_meta_irsp** (8 fields) - Infrared Spectroscopy
6. **idx_meta_rscn** (12 fields) - Radio Science Continuum
7. **idx_meta_rsoc** (14 fields) - Radio Science Occultation
8. **idx_meta_rsoh** (15 fields) - Radio Science OH
9. **idx_meta_rsrdr** (19 fields) - Radio Science Radar
10. **idx_meta_rssl** (15 fields) - Radio Science Spectral Line
11. **idx_meta_rsuv** (10 fields) - Radio Science UV

**Analysis:** Amateur Visual and all Radio Science subnets are complete. This was likely intentional focus during initial development.

---

### ⚠️ Incomplete Models (14 tables)

#### 1. idx_meta_lspn (Large-Scale Phenomena)
**Severity:** CRITICAL  
**Missing:** 71 of 88 fields (80% incomplete)  
**Current:** 17 fields in model  
**Observations:** 3,136 records

**Missing Field Categories:**

**WCS (World Coordinate System) - 8 fields:**
- `cdelt1`, `cdelt2` - Coordinate increments
- `crval1`, `crval2` - Reference pixel values
- `crpix1`, `crpix2` - Reference pixel positions
- `crota1`, `crota2` - Rotation angles

**Image Metadata - 7 fields:**
- `naxis`, `naxis1`, `naxis2` - Array dimensions
- `bitpix` - Bits per pixel
- `bscale`, `bzero` - Scaling factors
- `blank` - Undefined pixel value

**Instrument Details - 8 fields:**
- `aperture`, `fratio` - Telescope parameters
- `detector`, `cameraid`, `chip_id` - Detector info
- `filter_name`, `emulsion` - Filter/film
- `instrume` - Instrument name

**Observation Parameters - 10 fields:**
- `exposure` - Exposure time
- `fov_x`, `fov_y` - Field of view
- `pltscale`, `pltsze1`, `pltsze2` - Plate scale/size
- `scnstpx`, `scnstpy` - Scan step
- `size` - Image size
- Various calibration fields

**Processing/Calibration - 15 fields:**
- `bunit` - Brightness units
- `dat_form`, `dat_type` - Data format/type
- `ncalspot`, `ncalwdge` - Calibration info
- `cometmax`, `skyden`, `skymin` - Image statistics
- Multiple scaling/processing fields

**Location/Time - 8 fields:**
- `lat_obs`, `long_obs`, `elev_obs` - Observatory location
- `equinox` - Coordinate epoch
- `date_pds`, `date_prc`, `date_rec`, `date_rel`, `date_wrt` - Processing dates

**Comments - 5 fields:**
- `cmts_anl`, `cmts_log`, `cmts_obs`, `cmts_prc` - Various comment fields
- `obs_cmts`, `log_cmts` - Additional comments

**Other - 10 fields:**
- `file_num`, `ra_head`, `dec_head` - File/coordinate info
- `hypsen` - Hypersensitization
- Other technical fields

**Impact:** LSPN is one of the largest datasets (3,136 obs). Missing critical FITS header info, WCS coordinates, and calibration data severely limits scientific utility.

---

#### 2. idx_meta_msnrdr (Meteor Studies - Radar)
**Severity:** HIGH  
**Missing:** 47 of 49 fields (96% incomplete!)  
**Current:** Only 2 fields in model  
**Observations:** 6,675 records (largest MSN dataset)

**Missing Categories:**
- **Altitude bins (22 fields):** `alt_70_80km`, `alt_100_110km`, ... `alt_320_330km`
- **Duration bins (8 fields):** `dur_ge_1`, `dur_gt_8`, etc.
- **Observation details (17 fields):** `direction`, `limit_sensitiv`, meteor counts, etc.

**Impact:** This is essentially a stub model. Nearly all scientifically useful data is inaccessible.

---

#### 3. idx_meta_nnsn (Near-Nucleus Studies)
**Severity:** HIGH  
**Missing:** 23 of 29 fields (79% incomplete)  
**Current:** 6 fields in model  
**Observations:** 3,517 records

**Missing Fields:**
- `airmass`, `apsize`, `cometmax` - Observing conditions
- `elev_obs`, `lat_obs`, `long_obs` - Observatory location
- `flux_unit`, `pixel_scale`, `image_samples` - Image metadata
- `naxis`, `telefl`, `wavelen` - Technical parameters
- Comments: `cmts_log`, `cmts_anl`, `cmts_prc`, `cmts_obs`
- Dates: `date_wrt`, `date_pds`

**Impact:** Missing critical image metadata and calibration info for near-nucleus imaging studies.

---

#### 4. idx_meta_astrom (Astrometry)
**Severity:** MEDIUM-HIGH  
**Missing:** 19 fields  
**Current:** 18 fields in model (but model has 18, DB has 23 - discrepancy?)  
**Observations:** 8,168 records (second largest dataset)

**Missing Fields:**
- `acceptance_flag` - Data quality flag
- `dec_reported`, `decl`, `ra_reported` - Reported coordinates
- `dxy`, `ra_rms`, `dec_rms` - Positional uncertainties
- `filenum` - File reference
- `lat_obs`, `long_obs` - Observatory location
- `mag_total` - Total magnitude
- `obs_code` - Observatory code
- `utc_corr` - Time correction
- Additional fields (need full list)

**Note:** Model shows 18 fields but DB has 23. May have field name mismatches or extra model fields not in DB.

---

#### 5. idx_meta_spectra (Spectroscopy)
**Severity:** MEDIUM  
**Missing:** 19 of 23 fields (83% incomplete)  
**Current:** 8 fields in model  
**Observations:** 3,312 records

**Missing Fields:**
- `airmass`, `elevation` - Observing conditions
- `axes`, `axis_1` - Data dimensionality
- `calibration` - Calibration info
- `exposure` - Exposure time
- `offset_rho`, `offset_theta` - Offset from nucleus
- `range_lo`, `range_hi` - Wavelength range
- `slit_pa`, `slit_width`, `slit_height` - Slit parameters
- Resolution fields: `resolut`, `res_unit`, `res_code`
- Comments and notes: `spectrum_notes`, `quality`, etc.

**Impact:** Missing key spectroscopic parameters (wavelength range, resolution, slit config).

---

#### 6-9. Photometry/Polarimetry Tables (PPSN)
All four PPSN tables have similar patterns:

**idx_meta_psto** (Stokes Parameters) - 16 missing:
- Stokes parameters: `q_over_i`, `u_over_i`, `v_over_i` + errors
- Standard fields: `airmass`, `aperture_diam`, `filter_name`, `note_flag`, `offset_rho`, `offset_theta`, `ppn_num`
- Additional polarization data

**idx_meta_ppol** (Polarimetry) - 15 missing:
- `polarization`, `polariz_angle`, `polariz_angle_err`
- Standard observing fields (airmass, aperture, filter, offsets)

**idx_meta_pmag** (Magnitude) - 13 missing:
- `magnitude`, `mag_error`, `mag_lt` (magnitude limit)
- Standard observing fields

**idx_meta_pflx** (Flux) - 13 missing:
- `log_flux`, `flux_error`, `limit_flag`
- Standard observing fields
- Bandwidth: `theta`, `bandpass`, `integration_time`

**Pattern:** All PPSN tables are missing the actual scientific measurements plus standard observing parameters.

---

#### 10. idx_meta_msnvis (Meteor Studies - Visual)
**Severity:** MEDIUM  
**Missing:** 12 of 14 fields (86% incomplete)  
**Current:** 2 fields in model  
**Observations:** 1,624 records

**Missing Fields:**
- Meteor counts: `count_shower`, `count_noshower`, `total_meteor_count`, `total_meteor_time`
- Observing conditions: `cloud_cover`, `mag_limit`
- Observer info: `observer_id`, `obs_num`, `site_num`
- Source tracking: `source_fileid`, `source_filepathid`

---

#### 11-13. Amateur Photography/Spectroscopy

**idx_meta_amsp** (Amateur Spectroscopy) - 7 missing:
- `config`, `foc_len`, `fratio`, `instrument`
- `hypsen`, `iso`, `idno`

**idx_meta_ampg** (Amateur Photography) - 5 missing:
- `fov1`, `fov2` - Field of view
- `hypersense`, `iso_din` - Film sensitivity
- `idno` - ID number

---

#### 14-15. Infrared

**idx_meta_irim** (IR Imaging) - 5 missing:
- `filter`, `flux_unit`, `pixel_scale`
- `image_lines`, `image_samples` - Image dimensions

**idx_meta_irph** (IR Photometry) - 1 missing:
- `irphot_type` - Photometry type

---

## Field Name Discrepancies

Some models report more fields than DB columns, suggesting possible issues:

- **idx_meta_astrom:** 18 model fields vs 23 DB columns = 5 DB fields not in model, but count shows 19 missing?
- **idx_meta_amsp:** 16 model fields vs 14 DB columns = 2 extra model fields?
- **idx_meta_ampg:** 14 model fields vs 14 DB columns = 5 missing but counts match?
- **idx_meta_irph:** 7 model fields vs 5 DB columns = 2 extra model fields?

**Recommendation:** Need to check for field name mismatches (e.g., model uses `observer_id` but DB has `observer_code`).

---

## Priority Recommendations

### Phase 1: High-Impact Tables (Top Priority)
Focus on tables with lots of data AND lots of missing fields:

1. **idx_meta_lspn** (3,136 obs, 71 missing) - Large-Scale Phenomena
2. **idx_meta_astrom** (8,168 obs, 19 missing) - Astrometry (second largest!)
3. **idx_meta_spectra** (3,312 obs, 19 missing) - Spectroscopy
4. **idx_meta_nnsn** (3,517 obs, 23 missing) - Near-Nucleus

**Estimated effort:** ~130 fields to add across 4 tables

### Phase 2: Medium-Impact Tables
Tables with moderate data volume or missing key scientific fields:

5. **idx_meta_msnrdr** (6,675 obs, 47 missing) - Meteor Radar
6. **PPSN group** (6,823 total obs, 57 missing across 4 tables):
   - idx_meta_pflx (18,189 obs - largest!)
   - idx_meta_pmag (3,890 obs)
   - idx_meta_ppol (801 obs)
   - idx_meta_psto (132 obs)

**Estimated effort:** ~100 fields

### Phase 3: Lower-Impact Tables
Smaller datasets or fewer missing fields:

7. **idx_meta_msnvis** (1,624 obs, 12 missing)
8. **idx_meta_ampg** (2,170 obs, 5 missing)
9. **idx_meta_amsp** (45 obs, 7 missing)
10. **idx_meta_irim** (106 obs, 5 missing)
11. **idx_meta_irph** (240 obs, 1 missing)

**Estimated effort:** ~30 fields

---

## Implementation Strategy

### Option A: Phased Approach (Recommended)
1. Start with **idx_meta_lspn** (most critical, well-documented FITS headers)
2. Add all 71 fields using DESCRIBE output
3. Update display logic to show all fields
4. Test with real observations
5. Gather user feedback on which fields are useful
6. Repeat for next high-priority table

**Pros:** Manageable chunks, learn as we go, get user feedback early  
**Cons:** Takes longer to complete all tables

### Option B: Bulk Update
1. Generate all missing fields for all 14 tables at once
2. Add ~266 fields across all models
3. Update display logic for all
4. Deploy and gather feedback

**Pros:** Complete solution faster  
**Cons:** More risk, harder to test, massive PR to review

### Option C: Auto-Generate Approach
1. Create script to auto-generate model field definitions from DESCRIBE output
2. Review and adjust field types (CharField vs IntegerField, etc.)
3. Regenerate incomplete models
4. Test and deploy

**Pros:** Reduces manual work, ensures accuracy  
**Cons:** Still need to review 266 fields, type inference may be wrong

---

## Next Steps

1. **Confirm priority:** Which tables are most important to you?
2. **Choose approach:** Phased, bulk, or auto-generate?
3. **Start with LSPN?** It's the poster child for missing fields
4. **Document field meanings:** Many FITS header fields need explanations

---

## Technical Notes

### Field Type Inference
When adding fields, need to determine Django field types from MySQL types:

```python
# Common mappings
varchar(N) → models.CharField(max_length=N)
int(11) → models.IntegerField()
bigint(20) → models.BigIntegerField()
decimal(M,N) → models.DecimalField(max_digits=M, decimal_places=N)
float/double → models.FloatField()
datetime → models.DateTimeField()
date → models.DateField()
text → models.TextField()
```

### Model Template
```python
class IdxMetaExample(models.Model):
    metaid = models.ForeignKey(IdxMetaCommon, ...)
    field_name = models.CharField(max_length=64, blank=True, null=True)
    # ... more fields
    
    class Meta:
        managed = False
        db_table = 'idx_meta_example'
```

### Display Logic Updates
After adding fields, need to update `ObservationDetailView.get_context_data()` to:
1. Fetch all non-null fields
2. Group by category (Instrument, WCS, Processing, Comments)
3. Apply field_labels dict for human-readable names
4. Add tooltips for technical terms

---

## Appendix: Complete Missing Field Lists

(Would contain full DESCRIBE output for each table showing all missing fields with types)

---

**End of Audit Report**
