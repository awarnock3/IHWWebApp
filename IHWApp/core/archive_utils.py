"""
Utilities for checking archive file availability
"""
import os
from django.conf import settings


def is_archive_available():
    """
    Check if the IHW archive root directory exists and is accessible.
    
    Returns:
        bool: True if archive is available, False otherwise
    """
    archive_root = getattr(settings, 'IHW_ARCHIVE_ROOT', None)
    if not archive_root:
        return False
    return os.path.isdir(archive_root)


def get_archive_status():
    """
    Get detailed status of archive availability.
    
    Returns:
        dict: Status information including availability and path
    """
    archive_root = getattr(settings, 'IHW_ARCHIVE_ROOT', None)
    return {
        'available': is_archive_available(),
        'root_path': archive_root,
        'configured': archive_root is not None,
    }


def find_fits_header_file(base_path):
    """
    Find FITS header file, checking for .fit, .fits, or .hdr files.
    
    Args:
        base_path: Path without extension (e.g., /path/to/file)
        
    Returns:
        str: Path to FITS header file if found, None otherwise
    """
    if not is_archive_available():
        return None
    
    # Check in priority order: .fit, .fits, .hdr
    for ext in ['.fit', '.fits', '.hdr']:
        path = base_path + ext
        if os.path.exists(path):
            return path
    
    return None


def find_pds_label_file(base_path):
    """
    Find PDS label file (.lbl).
    
    Args:
        base_path: Path without extension (e.g., /path/to/file)
        
    Returns:
        str: Path to PDS label file if found, None otherwise
    """
    if not is_archive_available():
        return None
    
    label_path = base_path + '.lbl'
    return label_path if os.path.exists(label_path) else None
