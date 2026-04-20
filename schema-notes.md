# IHW Database Schema Analysis

**Database:** ihwdb2  
**Server:** MariaDB 10.11.14  
**Character Sets:** utf8mb3 and utf8mb4  
**Total Tables:** 39

---

## 1. Table Inventory

### idx_meta_* Tables (Discipline-Specific Metadata) - 27 tables

**Core Common Metadata:**
- `idx_meta_common` - Central hub for all observations (332k records)

**Amateur Studies Network (AM):**
- `idx_meta_amdr` - Amateur Drawings (2.5k records)
- `idx_meta_ampg` - Amateur Photography (4.3k records)
- `idx_meta_amsp` - Amateur Spectroscopy (TBD records)
- `idx_meta_amvis` - Amateur Visual (46.5k records)

**Astrometry Network:**
- `idx_meta_astrom` - Astrometry observations (25k records)

**Infrared Studies:**
- `idx_meta_irim` - IR Imaging (520 records)
- `idx_meta_irph` - IR Photometry (961 records)
- `idx_meta_irpol` - IR Polarimetry (57 records)
- `idx_meta_irsp` - IR Spectroscopy (337 records)

**Large-Scale Phenomena Network:**
- `idx_meta_lspn` - Large-Scale Phenomena (11.1k records)

**Meteor Studies Network:**
- `idx_meta_msnrdr` - Meteor Radar (20.8k records)
- `idx_meta_msnvis` - Meteor Visual (3.2k records)

**Near-Nucleus Studies Network:**
- `idx_meta_nnsn` - Near-Nucleus Imaging (10.5k records)

**Photometry Network:**
- `idx_meta_pflx` - Photometric Flux (74.1k records)
- `idx_meta_pmag` - Broadband Magnitude (11.6k records)
- `idx_meta_ppol` - Polarization (2.4k records)
- `idx_meta_psto` - Stokes Parameters (397 records)

**Radio Studies Network:**
- `idx_meta_rscn` - Radio Continuum (7 records)
- `idx_meta_rsoc` - Radio Occultation Continuum (37 records)
- `idx_meta_rsoh` - Radio OH Spectral Line (20.3k records)
- `idx_meta_rsrdr` - Radio Radar (6 records)
- `idx_meta_rssl` - Radio Spectral Line (842 records)
- `idx_meta_rsuv` - Radio UV Interferometry (251 records)

**Spectroscopy Studies Network:**
- `idx_meta_spectra` - Spectroscopy (37k records)

### ihw_* Tables (Core Infrastructure) - 6 tables

- `ihw_network` - Master list of disciplines/networks (10 records)
- `ihw_subnet` - Discipline subnets (28 records)
- `ihw_files` - Unique archive files by MD5 digest (136k records)
- `ihw_file_filepath` - Link table: files to directory paths
- `ihw_filepath` - Directory paths relative to archive root (4.1k paths)
- `ihw_ephemeris` - Comet ephemeris data (5.5k records)

### apx_* Tables (Appendix Lookup Tables) - 6 tables

**Observatory/Observer Data:**
- `apx_am_obs_site` - Amateur observation sites (3.4k records)
- `apx_ihw_country` - Country codes (180 countries)
- `apx_ihw_obscodes` - Observatory site codes (1.1k records)
- `apx_msnvis_observers` - Meteor visual observers (522 records)
- `apx_msnvis_sites` - Meteor visual observation sites (314 sites)

**Supplemental Data:**
- `apx_msn_counts` - Meteor observation counts (118 records)
- `apx_msn_obscodes` - Meteor radar station codes (326 records)
- `apx_pflx_notes` - Photometric flux explanatory notes

---

## 2. Entity Map

### Core Domain Entities

**1. Observation Master (idx_meta_common)**
- Central hub for ALL observations across all 10 networks
- Links discipline-specific tables via FK to `meta_common_id`
- Stores common observation metadata: time, observer, discipline
- Links to `ihw_files` for data file provenance
- **Key fields:** id, discipline, date_obs, net_num, observer, syscode, object

**2. Networks & Disciplines**
- `ihw_network` - Master list of 10 IHW disciplines (ASTR, AMDR, AMVIS, etc.)
- `ihw_subnet` - 28 subnets representing sub-specializations within disciplines
- **Example:** AMDR (Amateur Drawings) is a subnet of discipline "AM" (Amateur Studies)

**3. File Management**
- `ihw_files` - Master registry of unique archive files (identified by MD5)
- `ihw_filepath` - Directory paths on disk (relative to archive root)
- `ihw_file_filepath` - Junction table (files can exist in multiple directories)
- **Purpose:** Deduplication + efficient path management

**4. Observatory/Observer Lookups**
- `apx_ihw_obscodes` - Professional observatories (1.1k entries)
- `apx_am_obs_site` - Amateur observer locations (3.4k entries)
- `apx_msnvis_observers` - Meteor visual network observers
- `apx_msnvis_sites` - Meteor visual observation sites
- **Pattern:** Each discipline-specific metadata table can FK to appropriate observer/site table

**5. Supporting Reference Data**
- `ihw_ephemeris` - Comet positions over time (supports astrometry, photometry)
- `apx_ihw_country` - Country codes with IHW templates
- `apx_pflx_notes` - Explanatory notes for flux measurements
- `apx_msn_counts` - Summary statistics for meteor observations

---

## 3. Relationship Diagram (Text-Based)

```
┌─────────────────────────────────────────────────────────────────────┐
│                     IHW OBSERVATION ECOSYSTEM                       │
└─────────────────────────────────────────────────────────────────────┘

                         ┌──────────────────────┐
                         │  ihw_network         │ (10 disciplines)
                         │  id, netnum,         │ e.g., "ASTR", "AM", "MSN"
                         │  discipline, name    │
                         └──────────┬───────────┘
                                    │ 1:N
                                    │
                         ┌──────────▼───────────┐
                         │  ihw_subnet          │ (28 subnets)
                         │  id, subnet,         │ e.g., "AMDR", "AMVIS", "MSNRDR"
                         │  subnet_name,        │
                         │  discipline (FK)     │
                         └──────────┬───────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
         ┌──────────────────┐   ┌──────────┐   ┌──────────┐
         │  ihw_files       │   │apx_ihw_  │   │apx_msn_  │
         │  fileid, digest, │   │obscodes  │   │obscodes  │
         │  network_id(FK)  │   │(1.1k)    │   │(326)     │
         │  subnet_id(FK)   │   └──────────┘   └──────────┘
         └────────┬─────────┘
                  │ 1:N
                  │
    ┌─────────────┴──────────────────────────────────────┐
    │                                                    │
    ▼                                                    ▼
┌──────────────────────┐                  ┌──────────────────────┐
│  ihw_file_filepath   │                  │  idx_meta_common     │
│  (fileid, filepath   │                  │  id, discipline,     │
│   FK composite)      │                  │  date_obs, net_num,  │
└──────────┬───────────┘                  │  observer, syscode,  │
           │ N:1                          │  idxfileid (FK)      │
           │                              └──────────┬───────────┘
    ┌──────▼──────┐                                   │ 1:N
    │ ihw_filepath│                                   │
    │ id, dirpath │                                   │
    └─────────────┘                    ┌──────────────┴──────────────────┐
                                       │                                 │
                        ┌──────────────┴────────────────┐        ┌────────┴──────────────┐
                        │                               │        │                       │
                   ▼    ▼    ▼    ▼    ▼    ▼    ▼     │    ▼   ▼   ▼   ▼   ▼   ▼      │
              idx_meta_amdr, amvis, ampg, amsp          │  Other discipline-specific
              idx_meta_astrom                           │  metadata tables...
              idx_meta_irim, irph, irpol, irsp          │
              idx_meta_lspn                             │
              idx_meta_msnrdr, msnvis                   │
              idx_meta_nnsn                             │
              idx_meta_pflx, pmag, ppol, psto           │
              idx_meta_rscn, rsoc, rsoh, rsrdr,         │
                           rssl, rsuv                   │
              idx_meta_spectra                          │
                        │                               │
                        └──────────────┬──────────────┘
                                       │
                                       ▼
                     ┌─────────────────────────────────┐
                     │ Observatory/Observer FK chains  │
                     ├─────────────────────────────────┤
                     │ → apx_ihw_obscodes (for LSPN,   │
                     │   NNSN, PFLX, ASTROM, etc.)     │
                     │ → apx_am_obs_site (for AM nets) │
                     │ → apx_msnvis_sites/observers    │
                     │   (for MSNVIS)                  │
                     │ → apx_msn_obscodes (for MSN)    │
                     └─────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                    SUPPLEMENTARY TABLES                              │
├──────────────────────────────────────────────────────────────────────┤
│ ihw_ephemeris        → links to ihw_files (comet positions)          │
│ apx_ihw_country      → FK from apx_am_obs_site.country              │
│ apx_pflx_notes       → FK from idx_meta_pflx.note_code              │
│ apx_msn_counts       → summary stats for MSNVIS/MSNRDR              │
└──────────────────────────────────────────────────────────────────────┘
```

### Key FK Relationships

1. **All discipline tables → idx_meta_common.id**
   - Pattern: `meta_common_id` FK
   - Allows single query to find all observations of a given type

2. **idx_meta_common → ihw_files.fileid**
   - Pattern: `idxfileid` FK
   - Traces observation back to source data file
   - NULL if no associated data file

3. **ihw_subnet → ihw_network.id**
   - Discipline hierarchy (NETWORK → SUBNET)

4. **ihw_files → ihw_network.id, ihw_subnet.id**
   - File inventory organized by network/subnet

5. **Observatory chains:**
   - `apx_ihw_obscodes` ← LSPN, NNSN, PFLX, ASTROM, IRIM, IRPH, IRPOL, IRSP
   - `apx_am_obs_site` ← AMDR, AMPG, AMSP, AMVIS (via obs_site_id)
   - `apx_msnvis_sites` + `apx_msnvis_observers` ← MSNVIS
   - `apx_msn_obscodes` ← MSNRDR

6. **Supplementary FKs:**
   - `idx_meta_pflx.note_code` → `apx_pflx_notes.note_code`
   - `idx_meta_msnvis.observer_id` → `apx_msnvis_observers.id`
   - `idx_meta_msnvis.source_fileid,filepathid` → `ihw_file_filepath`

---

## 4. Field Patterns

### Universal Fields (Present in Most Tables)

| Field | Purpose | Type | Notes |
|-------|---------|------|-------|
| `id` | Primary Key | INT AUTO_INCREMENT | Unsigned in some idx_meta_* tables |
| `meta_common_id` | FK to common metadata | INT NOT NULL | All discipline-specific tables |

### idx_meta_common Fields (Observation Hub)

| Field | Type | Comment |
|-------|------|---------|
| `id` | INT PK AUTO_INC | - |
| `discipline` | VARCHAR(8) | Discipline code (ASTR, AMDR, MSNVIS, etc.) |
| `date_obs` | DATETIME | UTC observation timestamp |
| `net_num` | INT | Discipline-specific observation ID |
| `syscode` | VARCHAR(8) | IHW system code from FITS SYSTEM |
| `observer` | VARCHAR(64) | Observer name/code |
| `filename` | VARCHAR(32) | Source file root name |
| `object` | VARCHAR(24) | Target object (default: '1P/Halley') |
| `idxfileid` | INT FK | Link to ihw_files (NULL if no file) |
| `linenum` | INT | Line number in source file |
| `note_flag` | TINYINT(1) | 1 if notes present |
| `note` | TEXT | Free-form notes |

**Indexes:**
- UNIQUE: (discipline, idxfileid, linenum)
- Regular: date_obs, discipline, net_num, observer

### Common Observation Metadata Fields

Patterns across different discipline tables:

**Photometric Measurements:**
- `magnitude`, `mag_error`, `filter_name`, `wavelength`, `bandpass`
- `airmass`, `offset_rho`, `offset_theta`
- `aperture_diam`, `duration`, `exposure`

**Imaging Metadata:**
- `image_lines`, `image_samples`, `pixel_scale`
- `flux_unit`, `bitpix`, `naxis`, `naxis1`, `naxis2`
- `crval1`, `crval2`, `crpix1`, `crpix2` (WCS keywords)

**Spectroscopic Metadata:**
- `wavelength`, `resolution`, `range_lo`, `range_hi`
- `aperture`, `slit_size`, `slit_pa`
- `axes`, `axis_1`, `axis_2`

**Radio/Radar Metadata:**
- `cent_freq`, `bandwidth`, `beamsize`
- `scaling_factor`, `offset_val`
- `derived_max`, `derived_min`

**Observatory Reference Fields:**
- `observatory_id` (FK to apx_ihw_obscodes in most cases)
- `obs_site_id` (FK in AMDR, AMPG, AMVIS - to apx_am_obs_site)
- `obs_code`, `lon_obs`, `lat_obs`, `lat_calc_flag`

**Quality Indicators:**
- `note_flag`, `acceptance_flag`, `image_quality`
- `data_quality`, `calibration_flag`, `quality`
- `mag_gt` (greater-than flag for magnitude upper limits)
- `limit_flag` (for flux upper limits)

### Field Types Distribution

- **VARCHAR(8)** - Discipline/subnet codes (AMDR, IRIM, NNSN, MSNVIS, etc.)
- **VARCHAR(12-32)** - System codes, filter names, site names
- **DECIMAL(7,4)** - Aperture, focal length (meters)
- **DECIMAL(5,1)** - F-ratio, magnitudes (with decimal places)
- **FLOAT/DOUBLE** - Coordinates (RA, Dec, JD), wavelengths
- **INT/SMALLINT** - Counters, row/column counts
- **TINYINT(1)** - Flags (note_flag, calibration, etc.)
- **TEXT** - Notes, comments, descriptions
- **CHAR(1)** - Single-character flags (Y/N, T/F, A/D)

---

## 5. Indexes and Constraints

### Primary Keys
- All tables use `id` as PK (INT AUTO_INCREMENT)
- Most idx_meta_* use INT(10 UNSIGNED) or INT(11)

### UNIQUE Constraints

| Table | Constraint | Columns | Purpose |
|-------|-----------|---------|---------|
| `idx_meta_common` | `uq_common_obs` | (discipline, idxfileid, linenum) | Prevent duplicate observation imports |
| `ihw_files` | `uniq_digest` | (digest) | One file per MD5 hash |
| `ihw_subnet` | `uniq_subnet` | (subnet) | Unique subnet codes |
| `ihw_filepath` | `uniq_dirpath` | (dirpath) | Unique directory paths |
| `apx_ihw_country` | `uniq_apx_ccode` | (code) | Unique country codes |
| `apx_msnvis_observers` | `uniq_number` | (number) | Unique observer IDs |
| `apx_msnvis_sites` | `uniq_number` | (number) | Unique site IDs |
| `ihw_file_filepath` | `uniq_fileid_filepathid` | (fileid, filepathid) | Junction table uniqueness |

### Foreign Keys

**To idx_meta_common (27 discipline tables):**
```
All idx_meta_* tables:
FK `meta_common_id` → idx_meta_common.id
```

**To Observatory/Observer Tables:**
```
idx_meta_astrom.observatory_id → apx_ihw_obscodes.id
idx_meta_lspn.observatory_id → apx_ihw_obscodes.id
idx_meta_nnsn.observatory_id → apx_ihw_obscodes.id
idx_meta_pflx.observatory_id → apx_ihw_obscodes.id
idx_meta_irim.observatory_id → apx_ihw_obscodes.id
idx_meta_irph.observatory_id → apx_ihw_obscodes.id
idx_meta_irpol.observatory_id → apx_ihw_obscodes.id
idx_meta_irsp.observatory_id → apx_ihw_obscodes.id
```

**Inter-infrastructure FKs:**
```
ihw_files.network_id → ihw_network.id
ihw_files.subnet_id → ihw_subnet.id
ihw_subnet.discipline → ihw_network.id
ihw_ephemeris.fileid → ihw_files.fileid
idx_meta_common.idxfileid → ihw_files.fileid
ihw_file_filepath.fileid → ihw_files.fileid
ihw_file_filepath.filepathid → ihw_filepath.id
```

**Appendix Table FKs:**
```
apx_am_obs_site.country → apx_ihw_country.code
apx_ihw_obscodes.subdiscipline → ihw_subnet.id
apx_msn_counts.subnet → ihw_subnet.subnet
apx_msn_obscodes.subnet → ihw_subnet.subnet
apx_msnvis_sites.subdiscipline → ihw_subnet.subnet
idx_meta_msnvis.observer_id → apx_msnvis_observers.id
idx_meta_msnvis.source_fileid,filepathid → ihw_file_filepath(fileid,filepathid)
idx_meta_pflx.note_code → apx_pflx_notes.note_code
```

### Index Strategy

**High-volume Query Paths:**
- `idx_meta_common.date_obs` - Range queries by observation date
- `idx_meta_common.discipline` - Filter by network type
- `idx_meta_common.observer` - Search by observer name (16-char prefix index)
- `idx_meta_astrom.jd, ra, decl` - Astrometry sky searches
- `ihw_files.filename, digest` - File lookups

**Join Keys:**
- All `meta_common_id` indexed for discipline table joins
- Network/subnet IKs in ihw_files
- Observatory IDs in discipline-specific tables

---

## 6. Data Types

### Character Sets

| Table Group | Character Set | Collation |
|-------------|---------------|-----------|
| idx_meta_* | utf8mb4 | utf8mb4_general_ci |
| ihw_* | Mixed (ihw_network/ihw_subnet: utf8mb3; others: utf8mb4) | general_ci |
| apx_* | Mixed (apx_country/apx_obscodes/msn: utf8mb3; others: utf8mb4) | general_ci |

**Implication:** utf8mb4 supports full Unicode; utf8mb3 is legacy 3-byte UTF-8 (limited emoji/symbols)

### Storage Engines
- **All tables:** InnoDB (transaction-safe, FK support)
- **Default charset:** utf8mb4 (for new tables)

### AUTO_INCREMENT Patterns

| Table | Current Value | Notes |
|-------|---------------|-------|
| idx_meta_common | 332,406 | Central hub ~332k records |
| idx_meta_lspn | 11,160 | FITS header metadata |
| idx_meta_msnrdr | 20,887 | Radar observations |
| idx_meta_rsoh | 20,302 | Radio OH spectral line |
| idx_meta_spectra | 37,001 | Spectroscopy records |
| idx_meta_pflx | 74,189 | Photometric flux (largest single discipline) |
| idx_meta_amvis | 46,565 | Amateur visual (second largest) |
| ihw_files | 136,329 | File registry |
| ihw_filepath | 4,131 | Directory paths |
| apx_am_obs_site | 3,483 | Amateur sites |
| apx_ihw_obscodes | 1,198 | Professional observatories |

### Notable Field Types

- **DECIMAL(7,4)** - 7 total digits, 4 decimal places
  - Used for: aperture (meters), focal length, scale factors
  - Range: -999.9999 to 999.9999

- **DECIMAL(9,6)** - Coordinates (latitude/longitude)
  - Range: ±999.999999 (6 decimal places ≈ 0.1 meters precision)

- **DOUBLE** - High-precision values
  - Used for: Julian Dates, RA/Dec in radians, scaling factors

- **ENUM('Halley','Crommelin','GZ')** - ihw_ephemeris.comet
  - Fixed set of comet targets

---

## 7. Schema Issues & Legacy Quirks

### Normalization Issues

1. **Mixed UTF-8 in same schema**
   - Some tables utf8mb3, others utf8mb4
   - **Risk:** Emoji/Unicode in utf8mb3 tables will fail
   - **Fix:** Migrate all to utf8mb4

2. **Denormalization in ihw_files**
   ```sql
   CREATE TABLE ihw_files (
     fileid, filename, 
     network_id (FK), network (VARCHAR), -- redundant!
     subnet (VARCHAR), subnet_id (FK),   -- redundant!
     ...
   )
   ```
   - `network` and `subnet` can be JOINed from network_id/subnet_id
   - **Why:** Performance optimization (avoid JOINs in large queries)
   - **Risk:** Update anomalies if not carefully maintained

3. **Discipline code in multiple places**
   - `ihw_network.discipline` (VARCHAR)
   - `idx_meta_common.discipline` (VARCHAR)
   - `ihw_subnet.subnet` (VARCHAR) — not quite the same
   - **Issue:** No central enum table for valid discipline codes

4. **Observatory ID mismatch**
   - `apx_ihw_obscodes.id` (used by most discipline tables)
   - `apx_am_obs_site.id` (used only by AMDR, AMPG, AMVIS)
   - `apx_msnvis_sites.id`, `apx_msnvis_observers.id` (used by MSNVIS)
   - **Why:** Each discipline has different observer structures
   - **Problem:** No unified observer model

5. **File path normalization**
   - Paths split into directory + filename
   - `ihw_file_filepath` is a junction table for many-to-many
   - **Why:** Same file might exist in multiple locations
   - **Unclear:** When/why multiple paths per file occur

### Naming Inconsistencies

| Issue | Example | Impact |
|-------|---------|--------|
| `idxfileid` vs `fileid` | FK names inconsistent | Hard to grep for "file" relationships |
| `net_num` unclear | Should be `discipline_obs_num` | Ambiguous meaning |
| `meta_common_id` | Verbose; could be `observation_id` | Verbose in joins |
| `observatory_id` vs `observatory` | Mixed naming in apx_* | Unclear which is the ID |
| `apx_msn_obscodes.subnet` (VARCHAR) vs `apx_msn_counts.subnet` (VARCHAR) | Both reference ihw_subnet.subnet | No explicit FK in msn_obscodes! |
| `idx_meta_lspn.observer` duplicate | Also in idx_meta_common | Why store twice? |

### Missing Constraints

1. **apx_ihw_obscodes → ihw_subnet**
   - `subdiscipline` FK exists, but subnet is used in apx_msn_* tables
   - Missing explicit FK from `apx_msn_obscodes.subnet`

2. **Discipline code validation**
   - No check constraint ensuring discipline ∈ valid set
   - Relies on application layer

3. **Observatory type enforcement**
   - Can't prevent wrong observatory_id FK (e.g., MSNRDR pointing to apx_am_obs_site)
   - Would need triggers or application logic

### Data Quality Oddities

1. **NULL handling inconsistency**
   - Most instrument/observation fields: NULL = not measured
   - Some flags: NULL = false, 'Y'/'N'/'T'/'F' = true
   - **Example:** `idx_meta_pflx.limit_flag` — '<' = upper limit, NULL = detected

2. **String codes vs numeric IDs**
   - `ihw_subnet.subnet` is VARCHAR (MSNVIS, AMDR, etc.)
   - `ihw_subnet.id` is INT
   - Inconsistent: some FKs use subnet string, others use id

3. **Magnitude limits**
   - `idx_meta_amvis.mag_gt` = flag for ">" magnitude upper limit
   - `idx_meta_pflx.limit_flag` = '<' character
   - Inconsistent representation

4. **FITS Header Proliferation in idx_meta_lspn**
   - ~90 fields for FITS metadata
   - Many appear to be direct column mappings (CRVAL1, CRVAL2, etc.)
   - Could be normalized into a separate FITS table
   - **Why?** Historical: likely direct dump from FITS files

---

## 8. Django Integration Notes

### Model Generation Strategy

All tables **MUST** be unmanaged (`managed = False`) since this is a legacy database.

```python
# models.py example structure

class IhwNetwork(models.Model):
    netnum = models.IntegerField()
    discipline = models.CharField(max_length=8, db_index=True)
    name = models.CharField(max_length=32)
    
    class Meta:
        managed = False
        db_table = 'ihw_network'
        indexes = [...]
    
    def __str__(self):
        return f"{self.discipline}: {self.name}"
```

### Priority for Admin Interface

**Tier 1 (Core):**
- `IhwNetwork` - Small, read-only reference
- `IhwSubnet` - Small, read-only reference
- `IdxMetaCommon` - Central hub, filterable by discipline/date
  - **Include:** inline displays of related discipline tables
  - **Actions:** Export filtered observations to CSV/JSON

**Tier 2 (Discipline-Specific, High Volume):**
- `IdxMetaAmvis` (46k) - Amateur visual observations
- `IdxMetaPflx` (74k) - Photometric flux (largest single table)
- **Features:**
  - Filter by date range, discipline, observer
  - Read-only display
  - Related observation links

**Tier 3 (Reference Data):**
- `ApxIhwObscodes` - Observatory lookup (enable search, disable edit)
- `ApxAmObsSite` - Amateur sites (enable search)
- `ApxMsnvisObservers`, `ApxMsnvisSites` - Meteor data
- `IhwFiles` - File registry (read-only, large)

**Tier 4 (Rarely Used):**
- Appendix tables (country, msn_counts, pflx_notes) - read-only

### Custom Model Methods

**IdxMetaCommon:**
```python
def get_discipline_table(self):
    """Return the specific discipline metadata record for this observation."""
    tables = {
        'AMDR': IdxMetaAmdr,
        'AMVIS': IdxMetaAmvis,
        'ASTROM': IdxMetaAstrom,
        # ... etc
    }
    table = tables.get(self.discipline)
    return table.objects.get(meta_common_id=self.id) if table else None

def get_source_file(self):
    """Return the ihw_files record, if available."""
    return self.idxfileid  # Auto-populated FK

def date_range_query(self, start_date, end_date):
    """Common query pattern: observations in date range."""
    return self.__class__.objects.filter(
        date_obs__gte=start_date,
        date_obs__lte=end_date
    )

@property
def has_notes(self):
    return bool(self.note_flag)
```

**IhwNetwork:**
```python
def get_subnets(self):
    return self.ihwsubnet_set.all()

def get_observation_count(self):
    """Count observations in this network."""
    return IdxMetaCommon.objects.filter(
        discipline__in=self.ihwsubnet_set.values_list('subnet', flat=True)
    ).count()
```

**IhwFiles:**
```python
def get_paths(self):
    """All directory paths where this file exists."""
    return self.ihw_file_filepath_set.values_list(
        'filepathid__dirpath', flat=True
    )

@property
def full_paths(self):
    """Full file paths (useful for bulk export/archive operations)."""
    return [f"{path}/{self.filename}" for path in self.get_paths()]
```

### Query Patterns for Common Use Cases

**1. Find all observations from a given observer:**
```python
IdxMetaCommon.objects.filter(observer__icontains='Smith')
```

**2. Find all amateur visual observations in a date range:**
```python
IdxMetaCommon.objects.filter(
    discipline='AMVIS',
    date_obs__range=['1986-01-01', '1986-06-30']
).select_related('idxfileid')
```

**3. Find LSPN observations with related FITS metadata:**
```python
IdxMetaCommon.objects.filter(
    discipline='LSPN'
).prefetch_related('idxmetalspn_set')
```

**4. Get all observations that cite a specific observatory:**
```python
IdxMetaAstrom.objects.filter(
    observatory__name__contains='Mauna Kea'
).select_related('meta_common_id')
```

**5. Find observations missing data files:**
```python
IdxMetaCommon.objects.filter(idxfileid__isnull=True)
```

**6. Statistics by discipline:**
```python
from django.db.models import Count
IdxMetaCommon.objects.values('discipline').annotate(
    count=Count('id')
).order_by('-count')
```

### Manager/QuerySet Customization

**Suggested custom manager for IdxMetaCommon:**
```python
class ObservationQuerySet(models.QuerySet):
    def with_discipline_data(self):
        """Prefetch discipline-specific tables (expensive!)."""
        # Note: Requires custom prefetch_related since FKs are dynamic
        return self.prefetch_related(
            'idxmetalspn_set', 'idxmetaamvis_set', # ... etc
        )
    
    def by_date_range(self, start, end):
        return self.filter(date_obs__range=[start, end])
    
    def by_observer(self, name):
        return self.filter(observer__icontains=name)
    
    def with_files(self):
        return self.filter(idxfileid__isnull=False)

class ObservationManager(models.Manager):
    def get_queryset(self):
        return ObservationQuerySet(self.model, using=self._db)
    
    def by_date_range(self, start, end):
        return self.get_queryset().by_date_range(start, end)

# In model:
class IdxMetaCommon(models.Model):
    objects = ObservationManager()
```

### Admin Configuration Considerations

**IdxMetaCommon admin:**
```python
class IdxMetaCommonAdmin(admin.ModelAdmin):
    list_display = ('id', 'discipline', 'date_obs', 'observer', 'syscode')
    list_filter = ('discipline', 'date_obs', 'observer')
    search_fields = ('observer', 'filename', 'syscode')
    readonly_fields = ('id', 'date_obs', 'linenum')
    
    # Inline for related discipline records (example for AMVIS)
    inlines = [AmvisObservationInline]
    
    def has_delete_permission(self, request):
        return False  # Read-only archive
    
    def has_add_permission(self, request):
        return False  # No manual entry
```

**Raw_id_fields for large FKs:**
```python
# IdxMetaLspn, IdxMetaNnsn, etc.
raw_id_fields = ('meta_common_id', 'observatory_id')
```

### Schema Optimization Recommendations for Django

1. **Add computed properties with `@cached_property`:**
   ```python
   @cached_property
   def full_observation_data(self):
       """Lazy-load discipline-specific data."""
       ...
   ```

2. **Create model managers for common queries:**
   ```python
   class DateRangeManager(models.Manager):
       def in_range(self, start, end):
           return self.filter(date_obs__range=[start, end])
   ```

3. **Use select_related() for single FKs:**
   ```python
   IdxMetaCommon.objects.select_related('idxfileid').filter(...)
   ```

4. **Use prefetch_related() for reverse lookups:**
   ```python
   ihw_network = IhwNetwork.objects.prefetch_related('ihwsubnet_set').get(...)
   ```

5. **Avoid loading all 74k PFLX records at once:**
   - Use pagination in views
   - Consider raw SQL for aggregations
   - Implement caching for statistics

6. **Consider database views for common aggregations:**
   - Observation counts by discipline/date
   - Observer activity summaries
   - File statistics
   - Stored as unmanaged Django models

7. **Add constraints in the app layer:**
   ```python
   def clean(self):
       if self.discipline not in VALID_DISCIPLINES:
           raise ValidationError(f"Invalid discipline: {self.discipline}")
   ```

### Known Limitations & Workarounds

**Limitation:** Dynamic FK to discipline-specific tables
- **Workaround:** Use ContentType framework or manual routing based on discipline code
- **Better:** Store discipline-specific FK in idx_meta_common (requires schema migration)

**Limitation:** Observer table varies by discipline
- **Workaround:** Create abstract base model for observers
- **Better:** Unify observer records under single apx_observers table

**Limitation:** Many discipline tables have minimal fields (e.g., IRPOL has only syscode + meta_common_id)
- **Why:** Placeholder tables for future extensibility
- **Implication:** Some disciplines may have limited query usefulness

---

## Summary: Django Model Hierarchy

```
BaseModel (abstract)
├── IhwNetwork
├── IhwSubnet
├── IhwFile
├── IhwFilePath
├── IhwEphemeris
│
├── IdxMetaCommon (central hub)
│   ├── related_set: idxmetalspn_set
│   ├── related_set: idxmetaamvis_set
│   ├── related_set: idxmetaamdr_set
│   ├── related_set: idxmetaastrom_set
│   ├── ... (25 more discipline tables)
│   └── property: get_discipline_table()
│
├── ApxIhwObscodes
├── ApxAmObsSite
├── ApxIhwCountry
├── ApxMsnvisObservers
├── ApxMsnvisSites
└── ApxPflxNotes
```

---

## Appendix: Table-by-Table Reference

| Table | Records | Primary Purpose | Character Set | Key Fields |
|-------|---------|-----------------|---------------|------------|
| idx_meta_common | 332k | Observation hub | utf8mb4 | discipline, date_obs, observer |
| idx_meta_pflx | 74k | Flux measurements | utf8mb4 | filter_name, log_flux, airmass |
| idx_meta_amvis | 46k | Visual magnitude | utf8mb4 | magnitude, coma_maj, tail_len |
| idx_meta_spectra | 37k | Spectroscopy | utf8mb4 | wavelength, resolution, exposure |
| idx_meta_rsoh | 20k | Radio OH line | utf8mb4 | bandwidth, velocity spectrum |
| idx_meta_msnrdr | 21k | Meteor radar | utf8mb4 | shower, altitude bins |
| idx_meta_lspn | 11k | Large phenomena FITS | utf8mb4 | 90+ FITS fields |
| idx_meta_pmag | 12k | Broadband magnitude | utf8mb4 | magnitude, filter, aperture |
| idx_meta_nnsn | 10k | Near-nucleus imaging | utf8mb4 | image_lines, pixel_scale |
| ihw_files | 136k | File registry | utf8mb4 | digest, filename, network |
| ... | ... | ... | ... | ... |

