# Main Window - Primary Design (V1)

## Overview
The main window now uses a **single unified design**: **Glassmorphism Terminal/Glitch Aesthetic**

This design focuses on:
- 🎯 **Tech-focused monospace typography** (Consolas)
- 💻 **Terminal-style indicators** (`>>` and `──`)
- 🌟 **Glassmorphism cards** with subtle transparency
- 💗 **Pink accent border** (#F72585) matching editor window
- 🎨 **Dark gradient background** for depth

---

## Design System Applied

### Typography
- **Primary Font**: Consolas (monospace) - for headers, titles, CTA
- **Fallback Font**: Segoe UI - for body text and feature lists
- **Letter Spacing**: Enhanced for tech aesthetic

### Color Palette
```python
Gradient Background: #1a1a1c → #1e1e20
Primary Accent: #F72585 (Pink)
Blue: #0096C7
Yellow: #ffb600
Green: #4CAF50
Cyan: #00D9FF
Purple: #B565D8
```

### Spacing Scale (8px base)
```
xs: 8px   - tight spacing
sm: 16px  - normal spacing  
md: 24px  - medium spacing
lg: 32px  - large spacing
```

### Font Sizes
```python
"hero": 26px        # CODE TESTING SUITE
"glitch": 11px      # >> SYSTEM READY
"card_title": 15px  # Card headers
"feature": 11px     # Feature list items
"cta": 14px         # CTA text
"cta_sub": 11px     # CTA subtitle
```

---

## Components

### Main Container
- 2px pink border (#F72585)
- Dark gradient background
- 24px margins (md spacing)
- 12px border radius

### Glass Cards
- Glassmorphism effect (subtle transparency)
- 1px white border with 3px left accent
- 16px padding (sm spacing)
- Hover: White glow effect (no color change)

### Hero Section
```
CODE TESTING SUITE    ← Consolas 26px, ExtraBold
>> SYSTEM READY       ← Consolas 11px, tech indicator
```

### Call-to-Action
```
>> SELECT FEATURE TO BEGIN    ← Consolas 14px
Choose a feature from above   ← Consolas 11px
```

---

## Files Updated

### ✅ Primary Changes
1. **`qt_doc_engine.py`** - Updated with V1 theme
   - AppTheme: Terminal/glitch colors and fonts
   - StyleSheet: Glassmorphism, gradient background, pink border
   - FontUtils: Supports Consolas monospace

2. **`main_window_content.py`** - Set V1 as primary
   - ACTIVE_VARIATION = 1 (locked)
   - Updated documentation

3. **`main_window_variations.py`** - Cleaned up
   - Removed Variation2_Neon class
   - Simplified factory function
   - Updated file header

### 🗑️ Files Removed
1. `DESIGN_ANALYSIS.txt` - No longer needed
2. `preview_variations.py` - Old preview document

---

## Usage

The main window now automatically uses V1 design:
```python
from src.app.presentation.views.main_window.main_window_content import (
    create_main_window_content
)

# Always returns V1 Glassmorphism design
content = create_main_window_content()
```

---

## Feature Cards

All 6 features display with consistent styling:

1. **📝 Code Editor** - Blue (#0096C7)
2. **🔨 Compare** - Pink (#F72585)  
3. **⏱️ Benchmark** - Yellow (#ffb600)
4. **✅ Validate** - Green (#4CAF50)
5. **📊 Analytics** - Cyan (#00D9FF)
6. **⚙️ Configure** - Purple (#B565D8)

Each card has:
- UPPERCASE title in Consolas
- Colored left border accent
- Separator line under title
- Feature list with subtle text
- Hover glow effect

---

## Design Philosophy

**Terminal/Glitch Aesthetic**
- Inspired by command-line interfaces
- Monospace fonts for technical feel
- `>>` indicators like terminal prompts
- Glassmorphism for modern touch
- Pink accent for personality

**Consistency**
- Single design language throughout
- No conflicting variations
- Unified spacing system
- Standardized font hierarchy

---

## Testing

✅ App tested and running successfully
✅ All features display correctly
✅ Hover effects working
✅ Pink border matching editor window
✅ Gradient background applied
✅ Consolas fonts loading properly

---

**Last Updated**: October 17, 2025
**Design Version**: V1 (Primary)
**Status**: ✅ Production Ready
