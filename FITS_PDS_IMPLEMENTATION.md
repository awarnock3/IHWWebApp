# FITS Header and PDS Label Viewer Implementation

## Overview
Implemented browser-based viewers for FITS headers and PDS label files, allowing users to inspect file metadata without downloading files.

## Components

### 1. FITS Utilities (`IHWApp/core/fits_utils.py`)
Pure Python implementation for reading FITS files (no compiled astronomy libraries needed to avoid CPU compatibility issues):

- `read_fits_header(file_path)` - Reads 80-character card images from FITS files in 2880-byte blocks
- `format_header_for_display(cards)` - Formats cards for HTML display with line numbers
- `get_header_summary(cards)` - Extracts key-value pairs from header

**Key Features:**
- Respects FITS standard: 80-character cards, 2880-byte blocks
- Stops at END card
- Pure Python (no external dependencies)
- Handles ASCII decoding gracefully

### 2. Views (`IHWApp/search/views.py`)

#### FitsHeaderView
- URL: `/search/observation/<id>/fits-header/`
- Finds FITS file (.fit or .fits) for observation
- Reads header using `read_fits_header()`
- Displays all cards with line numbers

#### PdsLabelView
- URL: `/search/observation/<id>/pds-label/`
- Finds PDS label file (.lbl) for observation  
- Reads as plain ASCII text
- Displays with line numbers

### 3. Templates

#### `fits_header.html`
- Displays FITS header cards in monospace font
- Shows total card count
- Explains FITS format
- Breadcrumb navigation

#### `pds_label.html`
- Displays PDS label content in monospace font
- Shows total line count
- Explains PDS format
- Breadcrumb navigation

### 4. UI Integration

#### Observation Detail Page
- Detects if FITS (.fit/.fits) and/or PDS label (.lbl) files exist
- Shows "View File Metadata" buttons for available formats
- 📄 FITS Header button (blue)
- 📋 PDS Label button (green)

#### Search Results Table
- New "Actions" column replaces simple checkmark
- 📄 button for FITS header (quick access)
- 📋 button for PDS label (quick access)
- Tooltips for accessibility

## File Detection Logic
1. Get observation's file path from database
2. Extract base path (without extension)
3. Check for existence of:
   - `{base}.fit` or `{base}.fits` for FITS headers
   - `{base}.lbl` for PDS labels
4. Show buttons only for files that exist

## Technical Notes

### Why Pure Python Instead of Astropy?
- Astropy 7.2.0 caused "Illegal instruction (core dumped)" errors due to CPU incompatibility
- Pure Python approach is more portable and lightweight
- FITS header format is simple enough to parse manually

### FITS Header Structure
```
SIMPLE  =                    T /CONFORMS TO FITS FORMAT?                        
BITPIX  =                   16 /NUMBER OF BITS PER PIXEL                        
...
END                                                                             
```
- Each card: exactly 80 characters
- Blocks: 2880 bytes (36 cards per block)
- Last card: "END" followed by blank padding

### PDS Label Structure
```
RECORD_TYPE                     = FIXED_LENGTH
RECORD_BYTES                    = 1
...
END
```
- Plain ASCII text
- Keyword = value format
- Ends with "END"

## Testing
Tested with real IHW archive files:
- FITS: `/data/working/IHWv2/data/.../spec4249.fit`
- PDS: `/data/working/IHWv2/data/.../spec4249.lbl`

All utilities working correctly on live data.

## Future Enhancements
- Syntax highlighting for PDS labels
- Search/filter within headers
- Export header as JSON/CSV
- Multi-extension FITS support (currently only primary HDU)
