"""
FITS file utilities for reading and displaying FITS headers.

Uses pure Python implementation to avoid CPU compatibility issues with
compiled astronomy libraries.

Supports both:
- Concatenated FITS files (.fit or .fits) with header and data
- Separate header files (.hdr) containing only the FITS header
"""


def read_fits_header(file_path):
    """
    Read FITS header cards from a FITS file or separate .hdr header file.
    
    FITS headers consist of 80-byte fixed-length records (card images)
    arranged in 2880-byte blocks. Reading stops when the 'END' card is found.
    
    Args:
        file_path: Path to the FITS file (.fit/.fits) or header file (.hdr)
        
    Returns:
        List of 80-character card strings
        
    Raises:
        IOError: If file cannot be read
        ValueError: If file doesn't appear to be a valid FITS file/header
    """
    cards = []
    
    try:
        with open(file_path, 'rb') as f:
            # FITS headers are in 2880-byte blocks
            # Each card is 80 bytes
            block_num = 0
            while True:
                block = f.read(2880)
                if not block or len(block) < 2880:
                    break
                
                block_num += 1
                
                # Extract 80-byte cards from this block
                for i in range(0, 2880, 80):
                    card = block[i:i+80].decode('ascii', errors='replace')
                    cards.append(card)
                    
                    # Check if this is the END card
                    if card.startswith('END'):
                        # Validate it's a FITS file (should have SIMPLE = T at start)
                        if not cards[0].startswith('SIMPLE'):
                            raise ValueError("File does not appear to be a valid FITS file")
                        return cards
            
            # If we get here, no END card was found
            if cards:
                raise ValueError("FITS file appears incomplete (no END card found)")
            else:
                raise ValueError("File appears to be empty or not a FITS file")
                
    except UnicodeDecodeError as e:
        raise ValueError(f"File contains invalid ASCII in header: {e}")


def format_header_for_display(cards):
    """
    Format FITS header cards for HTML display.
    
    Args:
        cards: List of 80-character FITS card strings
        
    Returns:
        List of dictionaries with 'line_num' and 'text' keys
    """
    return [
        {
            'line_num': i + 1,
            'text': card.rstrip()  # Remove trailing spaces for display
        }
        for i, card in enumerate(cards)
    ]


def get_header_summary(cards):
    """
    Extract key information from FITS header for summary display.
    
    Args:
        cards: List of 80-character FITS card strings
        
    Returns:
        Dictionary with key header values
    """
    summary = {}
    
    for card in cards:
        if card.startswith('END'):
            break
            
        # Parse key=value cards
        if '=' in card:
            parts = card.split('=', 1)
            key = parts[0].strip()
            value_comment = parts[1]
            
            # Extract value (before comment if present)
            if '/' in value_comment:
                value = value_comment.split('/', 1)[0].strip()
            else:
                value = value_comment.strip()
            
            # Remove quotes from string values
            if value.startswith("'") and "'" in value[1:]:
                value = value.strip("'").strip()
            
            summary[key] = value
    
    return summary
