# Design Language Preservation Checklist

## Color Scheme
- [ ] Material Design colors preserved
- [ ] Sidebar gradients: Dark theme (#1b1b1e) with blue accents (#007acc)
- [ ] Editor syntax highlighting: Custom color scheme with proper contrast
- [ ] Button states: Hover (#2d2d30), active, disabled states maintained
- [ ] Status colors: Success (green), error (red), warning (amber)

## Typography
- [ ] Font families: System defaults with fallbacks maintained
- [ ] Size hierarchy: Headers, body, code, small text consistent
- [ ] Code font: Monospace (Consolas/Monaco) with proper line height
- [ ] Icon fonts: Consistent sizing and alignment (14px for emoji buttons)

## Layout & Spacing
- [ ] Sidebar: Fixed width (280px) with expandable sections
- [ ] Main area: Responsive with splitter controls (min 150px)
- [ ] Margins: Consistent 8px/16px grid system throughout
- [ ] Component spacing: Uniform 6px-8px spacing between elements

## Component Behaviors
- [ ] Sidebar navigation: Smooth transitions and hover effects
- [ ] Code editor: Syntax highlighting, auto-complete functionality
- [ ] Console output: Scrolling behavior and formatting preserved
- [ ] Dialog modals: Consistent styling and behavior (config, error dialogs)
- [ ] Loading states: Progress indicators and user feedback maintained

## Animation & Transitions
- [ ] Window switching: Fade transitions between views
- [ ] Button interactions: Hover effects with proper timing
- [ ] Progress indicators: Smooth animation for test progress
- [ ] Sidebar expand/collapse: Animated state changes

## Critical UI Elements (Cannot Change)
- **Sidebar Width**: Exactly 280px
- **Splitter Minimum**: 150px for main content area
- **Header Height**: 40px where applicable
- **Button Styles**: Material design with #007acc primary color
- **Separator Styles**: QFrame.VLine with proper styling
- **Web View Styling**: Consistent with overall theme

## Validation Requirements
- [ ] Visual comparison: Before/after screenshots identical
- [ ] Interaction testing: All user flows work identically
- [ ] Performance: No degradation in responsiveness
- [ ] Cross-platform: Behavior consistent across Windows/Mac/Linux
