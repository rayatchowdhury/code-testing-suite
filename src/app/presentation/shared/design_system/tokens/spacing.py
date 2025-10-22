"""
Spacing and Typography Constants for Consistent Design.

Provides standardized spacing values and font sizes to ensure
consistency across all UI components.

Usage:
    from src.app.presentation.shared.design_system.tokens.spacing import SPACING, FONTS, BORDER_RADIUS
    
    # In stylesheets
    padding: {SPACING['MD']}px;
    font-size: {FONTS['BODY']}px;
    border-radius: {BORDER_RADIUS['MD']}px;
"""

# ============================================================================
# SPACING CONSTANTS
# ============================================================================

SPACING = {
    # Component spacing
    "NONE": 0,
    "XS": 4,      # Tiny gaps, tight spacing
    "SM": 8,      # Small spacing within components
    "MD": 12,     # Default spacing between related elements
    "LG": 16,     # Larger spacing between sections
    "XL": 20,     # Extra large spacing for major sections
    "XXL": 24,    # Maximum spacing for clear separation
    
    # Container padding
    "PADDING_SM": 10,
    "PADDING_MD": 16,
    "PADDING_LG": 20,
    
    # Margins
    "MARGIN_SM": 8,
    "MARGIN_MD": 12,
    "MARGIN_LG": 16,
}

# ============================================================================
# TYPOGRAPHY CONSTANTS
# ============================================================================

FONTS = {
    # Font sizes (in pixels)
    "CAPTION": 11,      # Very small text, captions, hints
    "BODY_SM": 12,      # Small body text
    "BODY": 13,         # Default body text
    "BODY_LG": 14,      # Large body text
    "SUBTITLE": 15,     # Subtitles, secondary headers
    "TITLE_SM": 16,     # Small titles
    "TITLE": 18,        # Section titles
    "TITLE_LG": 20,     # Large titles
    "HEADER": 24,       # Major headers
    "HEADER_LG": 28,    # Large headers
    "DISPLAY": 32,      # Display text (e.g., large percentage)
    
    # Font weights
    "WEIGHT_LIGHT": 300,
    "WEIGHT_REGULAR": 400,
    "WEIGHT_MEDIUM": 500,
    "WEIGHT_SEMIBOLD": 600,
    "WEIGHT_BOLD": 700,
    "WEIGHT_EXTRABOLD": 800,
}

# ============================================================================
# BORDER RADIUS CONSTANTS
# ============================================================================

BORDER_RADIUS = {
    "NONE": 0,
    "SM": 4,       # Small radius for buttons, badges
    "MD": 8,       # Medium radius for cards, panels
    "LG": 10,      # Large radius for containers
    "XL": 12,      # Extra large radius for major sections
    "ROUND": 999,  # Fully rounded (pills, circular buttons)
}

# ============================================================================
# BORDER WIDTH CONSTANTS
# ============================================================================

BORDER_WIDTH = {
    "THIN": 1,
    "MEDIUM": 2,
    "THICK": 3,
}

# ============================================================================
# SIZE CONSTANTS
# ============================================================================

SIZES = {
    # Component heights
    "BUTTON_SM": 28,
    "BUTTON_MD": 32,
    "BUTTON_LG": 36,
    
    # Progress bars
    "PROGRESS_SM": 24,
    "PROGRESS_MD": 32,
    "PROGRESS_LG": 40,
    
    # Minimum widths
    "MIN_WIDTH_SM": 60,
    "MIN_WIDTH_MD": 90,
    "MIN_WIDTH_LG": 120,
}
