# Archive Configuration and Graceful Degradation

## Overview
The IHW Django application now gracefully handles scenarios where the archive data files are not available, allowing the database to be queried even when the physical archive is not mounted.

## Configuration

### Archive Root Path
In `IHWApp/settings.py`:
```python
# IHW Archive Configuration
# Root path to the archive data files
IHW_ARCHIVE_ROOT = '/data/working/IHWv2/data/'
```

**To deploy without archive files:**
- Set `IHW_ARCHIVE_ROOT` to `None` or a non-existent path
- The web app will function normally but hide file-related features

## File Path Handling

### Relative Paths (Display)
File paths are now displayed without the archive root prefix:
- Before: `/data/working/IHWv2/data/ihw-c-nnsn-3-edr-halley-v2.0/data/198904/nnsn3523.fit`
- After: `ihw-c-nnsn-3-edr-halley-v2.0/data/198904/nnsn3523.fit`

This allows the database to be portable across different mount points.

### Model Methods
`IhwFiles` model provides three path methods:

1. **`get_relative_path()`** - Returns path without archive root (for display)
2. **`get_full_path()`** - Returns complete filesystem path (for file operations)
3. **`get_primary_path()`** - Returns directory object from database

## FITS Header File Support

The system now checks for FITS headers in multiple formats:

1. **Concatenated FITS files** (.fit or .fits) - Header + data together
2. **Separate header files** (.hdr) - Header only (for archives not yet concatenated)

Priority order: `.fit` → `.fits` → `.hdr`

### Why .hdr Support?
Some archive directories have FITS headers and data as separate files:
- `file.hdr` - FITS header (2880-byte blocks, 80-char cards)
- `file.dat` - Binary data
- `file.lbl` - PDS label

Future work will concatenate these into standard .fit files, but the database schema won't change.

## Graceful Degradation

### Archive Utilities (`core/archive_utils.py`)

#### `is_archive_available()`
Returns `True` if `IHW_ARCHIVE_ROOT` exists and is accessible.

#### `find_fits_header_file(base_path)`
Searches for FITS header in order: `.fit`, `.fits`, `.hdr`  
Returns `None` if archive is unavailable.

#### `find_pds_label_file(base_path)`
Searches for `.lbl` file  
Returns `None` if archive is unavailable.

### View Behavior

**When archive is available:**
- Shows file paths (relative, no root prefix)
- Shows "View File Metadata" buttons (FITS header, PDS label)
- Allows metadata viewing

**When archive is unavailable:**
- Still shows file metadata from database (filename, size, MD5, type)
- Hides file paths
- Hides metadata viewer buttons
- Shows warning: "Archive files are not currently accessible"
- All database queries work normally

### Template Changes

**Observation Detail Page:**
```django
{% if archive_available %}
    {# Show file paths and metadata buttons #}
{% else %}
    <div class="alert alert-warning">
        Archive files not available
    </div>
{% endif %}
```

## Use Cases

### 1. Full Deployment (Database + Archive)
- `IHW_ARCHIVE_ROOT = '/data/working/IHWv2/data/'`
- Directory exists and is mounted
- Full functionality: search, metadata viewing, future downloads

### 2. Database-Only Deployment
- `IHW_ARCHIVE_ROOT = '/data/working/IHWv2/data/'` (not mounted)
- Directory does not exist
- Limited functionality: search works, file info from DB, no metadata viewing

### 3. Development Environment
- `IHW_ARCHIVE_ROOT = None` or different path
- No archive access expected
- Database queries and UI development possible

## Migration Path

When archive files are moved or reorganized:

1. Only `IHW_ARCHIVE_ROOT` in settings.py needs to change
2. Database paths remain unchanged (relative paths)
3. UI automatically adapts based on archive availability
4. No database migrations required

## Future File Reorganization

When concatenating .hdr + .dat into .fit files:

1. Physical files change (combine header + data)
2. Database schema stays the same (ihw_files, ihw_filepath unchanged)
3. Application code adapts automatically (checks .fit first, then .hdr)
4. Old and new archive structures work side-by-side during transition
