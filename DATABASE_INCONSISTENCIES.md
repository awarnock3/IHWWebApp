# Database Inconsistencies - Issues to Fix

This document tracks known database inconsistencies discovered during development of the IHW Django archive interface. These should be addressed in future database maintenance work.

## Understanding the Structure

**Network vs Subnet:**
- **Networks** are the 9 main disciplines (e.g., AMSN = Amateur Studies Network)
- **Subnets** are subdisciplines within each network (e.g., AMV = AMSN Visual Observations)
- Directory paths may use different naming (e.g., `ihw-c-amvis-*` for AMV subnet)

**AMSN (Amateur Studies Network) Subnets:**
- **AMDR** - Drawing
- **AMPG** - Photography  
- **AMSP** - Spectroscopy
- **AMV** / **AMVIS** - Visual Observations (stored in `ihw-c-amvis-*` directories)
  - *Note: Database lists as "AMSN Visual Magnitude" but actually means "Visual Observations"*

---

## AMV Subnet (AMSN Visual Observations) - Priority Issues

### Summary Statistics
- **Subnet:** AMV / AMVIS (AMSN Visual Observations)
  - *Database incorrectly lists as "AMSN Visual Magnitude"*
- **Directory paths:** `ihw-c-amvis-*` 
- **Total files in database:** 34,373
- **Files linked to observations:** 11,641 (33.9%)
- **Orphaned files:** 22,732 (66.1%)
- **Observations with files:** 11,641
- **Date range:** 1985-01-23 to 1988-02-23

### Issue 1: Separate Header Files (.hdr)
**Status:** Active - System handles this, but files should be concatenated

**Details:**
- **Count:** 11,643 .hdr files in database
- **Impact:** 92% of sampled files use separate .hdr files (46 out of 50)
- **Problem:** FITS standard is concatenated header+data in single file
- **Current workaround:** Application checks for .hdr if .fit not found

**Recommendation:**
```bash
# For each .hdr file, concatenate with corresponding .dat file
cat file.hdr file.dat > file.fit
# Then update file system (database schema unchanged)
```

**Priority:** Medium - System works but not ideal for long-term archive

---

### Issue 2: Orphaned Files
**Status:** Needs investigation

**Details:**
- **Count:** 22,732 files (66.1% of AMV files)
- **Problem:** Files exist in `ihw_files` table but not linked to any observation in `idx_meta_common`
- **File types affected:**
  - METADATA: 23,290 files
  - DATA: 11,072 files  
  - INDEX: 4 files
  - CATALOG: 3 files
  - SOFTWARE: 2 files
  - DOCUMENT: 2 files

**Questions to resolve:**
1. Are these legitimate files that should have observations created?
2. Are these supporting files (calibration, documentation) that don't need observations?
3. Are these duplicates or obsolete files that should be removed?

**Priority:** High - Affects archive completeness

---

### Issue 3: Missing Files in Sample
**Status:** Investigation needed

**Details:**
- **Count:** 4 out of 50 sampled files (8%)
- **Problem:** Database references files that don't exist on filesystem
- **Implication:** Either files were deleted or paths are incorrect

**To investigate:**
- Check if files were moved or renamed
- Verify directory structure matches database paths
- Check archive integrity

**Priority:** Medium - Small percentage but indicates potential data loss

---

## AMSN Network Summary

### All AMSN Subnets Combined
When analyzing all 4 AMSN subnets together:
- **Total AMSN observations:** 16,444
- **Observations with files:** 15,150 (92.1%)
- **Observations without files:** 1,294 (7.9%)

### Breakdown by Subnet
Need to scan remaining subnets:
- [ ] **AMDR** (Drawing) - Not yet scanned
- [ ] **AMPG** (Photography) - Not yet scanned
- [ ] **AMSP** (Spectroscopy) - Not yet scanned
- [x] **AMV / AMVIS** (Visual Observations) - Scanned (see above)

---

## Other Networks - Status

### Networks to check:
- [ ] Astrometry (ASTR)
- [ ] Infrared Studies (IRSN)
- [ ] Large-Scale Phenomena (LSPN)
- [ ] Near-Nucleus Studies (NNSN)
- [ ] Photometry & Polarimetry (PPSN)
- [ ] Radio Studies (RSN)
- [ ] Spectroscopy & Spectrophotometry (SSSN)
- [ ] Meteor Studies (MSN)

### Quick check recommendation:
```python
# Run this to scan all networks
from core.models import IhwNetwork, IdxMetaCommon, IhwFiles

for network in IhwNetwork.objects.all():
    total = IdxMetaCommon.objects.filter(network=network).count()
    with_files = IdxMetaCommon.objects.filter(network=network, idxfileid__isnull=False).count()
    print(f"{network.discipline}: {with_files}/{total} = {with_files/total*100:.1f}%")
```

---

## Application Adaptations

### Implemented Workarounds

1. **Separate .hdr files:**
   - `find_fits_header_file()` checks .fit → .fits → .hdr
   - System works with both concatenated and separate headers
   - No database changes needed when files are concatenated

2. **Relative paths:**
   - Archive root path configurable in settings.py
   - Paths stored in database are relative
   - Supports archive relocation without database migration

3. **Archive availability:**
   - System checks if archive directory exists
   - Gracefully degrades when files unavailable
   - Database-only mode for development/testing

---

## Next Steps

### Immediate (No Code Changes Needed)
1. Review orphaned files - determine if they should be linked
2. Investigate duplicate filenames - identify root cause
3. Document decision on .hdr files - concatenate or keep separate

### Future (Database Maintenance)
1. Concatenate .hdr + .dat → .fit files for AMSN network
2. Create missing observations for orphaned files (if appropriate)
3. Resolve duplicate filename conflicts
4. Run consistency checks on other 8 networks

### Long-term (Archive Enhancement)
1. Add data quality flags to observations
2. Track file modification history
3. Implement automated consistency checks
4. Create archive integrity reports

---

## Scan Commands

To re-run the AMSN scan:
```bash
cd IHWApp
source ../venv/bin/activate
python manage.py shell < /path/to/scan_amsn.py
```

To scan all networks:
```python
# See "Other Networks" section above for quick check code
```

---

**Last Updated:** 2026-04-20  
**Scanned By:** Django database analysis tools  
**Archive Version:** IHW v2.0
