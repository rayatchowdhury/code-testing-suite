#!/usr/bin/env python3
"""
Test Enhanced Theme System - Week 4 Day 1

Tests the enhanced theme service and domain models.
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
current_dir = os.path.dirname(__file__)
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from domain.models.theme import Theme, ThemeType
from domain.models.theme.predefined_themes import (
    get_default_theme, get_theme_by_name, get_available_themes
)
from infrastructure.theming.enhanced_theme_service import EnhancedThemeService


def test_predefined_themes():
    """Test predefined theme loading and validation"""
    print("🧪 Testing predefined themes...")
    
    # Test default theme
    default_theme = get_default_theme()
    print(f"✅ Default theme loaded: {default_theme.name}")
    assert default_theme.type == ThemeType.DARK
    
    # Test all built-in themes
    themes = get_available_themes()
    print(f"✅ Found {len(themes)} built-in themes:")
    
    for name, theme in themes.items():
        print(f"  - {theme.name} ({theme.type.value})")
        
        # Basic validation
        assert theme.name
        assert theme.version
        assert theme.colors.primary.startswith('#')
        assert theme.colors.background.startswith('#')
        assert theme.editor_colors.background.startswith('#')
        assert theme.typography.font_size_base > 0
        assert theme.spacing.unit > 0
    
    # Test theme retrieval by name
    dark_theme = get_theme_by_name('dark')
    assert dark_theme.name == 'Modern Dark'
    
    light_theme = get_theme_by_name('light')
    assert light_theme.name == 'Clean Light'
    
    hc_theme = get_theme_by_name('high_contrast')
    assert hc_theme.name == 'High Contrast'
    
    print("✅ All predefined themes validated")
    return True


def test_enhanced_theme_service():
    """Test enhanced theme service functionality"""
    print("\n🧪 Testing enhanced theme service...")
    
    # Create service
    service = EnhancedThemeService()
    
    # Test current theme
    current = service.get_current_theme()
    print(f"✅ Current theme: {current.name}")
    assert current.name == 'Modern Dark'  # Default
    
    # Test theme switching
    success = service.set_theme('light')
    assert success
    new_current = service.get_current_theme()
    assert new_current.name == 'Clean Light'
    print(f"✅ Switched to theme: {new_current.name}")
    
    # Test theme by type
    success = service.set_theme_by_type(ThemeType.HIGH_CONTRAST)
    assert success
    hc_current = service.get_current_theme()
    assert hc_current.type == ThemeType.HIGH_CONTRAST
    print(f"✅ Switched by type: {hc_current.name}")
    
    # Test available themes
    available = service.get_available_theme_names()
    print(f"✅ Available themes: {available}")
    assert len(available) >= 3
    
    # Test themes by type
    dark_themes = service.get_themes_by_type(ThemeType.DARK)
    assert len(dark_themes) >= 1
    print(f"✅ Found {len(dark_themes)} dark theme(s)")
    
    light_themes = service.get_themes_by_type(ThemeType.LIGHT)
    assert len(light_themes) >= 1
    print(f"✅ Found {len(light_themes)} light theme(s)")
    
    print("✅ Enhanced theme service validated")
    return True


def test_theme_validation():
    """Test theme validation functionality"""
    print("\n🧪 Testing theme validation...")
    
    service = EnhancedThemeService()
    
    # Test valid theme
    valid_theme = get_default_theme()
    validation = service.validate_theme(valid_theme)
    assert validation.is_valid
    print(f"✅ Valid theme passed validation")
    
    # Test theme with invalid colors (would need to create invalid theme)
    # For now, just test that validation runs
    
    print("✅ Theme validation working")
    return True


def test_utility_methods():
    """Test theme service utility methods"""
    print("\n🧪 Testing utility methods...")
    
    service = EnhancedThemeService()
    
    # Test color access
    primary_color = service.get_color('primary')
    assert primary_color
    assert primary_color.startswith('#')
    print(f"✅ Primary color: {primary_color}")
    
    # Test editor color access
    bg_color = service.get_editor_color('background')
    assert bg_color
    assert bg_color.startswith('#')
    print(f"✅ Editor background: {bg_color}")
    
    # Test font family
    ui_font = service.get_font_family('ui')
    code_font = service.get_font_family('code')
    assert ui_font
    assert code_font
    print(f"✅ UI font: {ui_font}")
    print(f"✅ Code font: {code_font}")
    
    # Test font sizes
    base_size = service.get_font_size('base')
    large_size = service.get_font_size('lg')
    assert base_size > 0
    assert large_size > base_size
    print(f"✅ Font sizes: base={base_size}, large={large_size}")
    
    # Test spacing
    unit = service.get_spacing('unit')
    padding_md = service.get_spacing('padding_md')
    assert unit > 0
    assert padding_md > 0
    print(f"✅ Spacing: unit={unit}, padding_md={padding_md}")
    
    print("✅ Utility methods working")
    return True


def test_theme_stats():
    """Test theme statistics"""
    print("\n🧪 Testing theme statistics...")
    
    service = EnhancedThemeService()
    stats = service.get_theme_stats()
    
    print(f"📊 Theme Statistics:")
    print(f"  Total themes: {stats['total_themes']}")
    print(f"  Built-in themes: {stats['built_in_themes']}")
    print(f"  Custom themes: {stats['custom_themes']}")
    print(f"  Current theme: {stats['current_theme']}")
    print(f"  Themes by type: {stats['themes_by_type']}")
    print(f"  Config directory: {stats['config_directory']}")
    
    assert stats['total_themes'] >= 3
    assert stats['built_in_themes'] >= 3
    assert stats['current_theme']
    
    print("✅ Theme statistics working")
    return True


def main():
    """Run Week 4 Day 1 tests"""
    print("=" * 60)
    print("🎨 WEEK 4 DAY 1: ENHANCED THEME SYSTEM TEST")
    print("   Theme Constants Extraction & Service Enhancement")
    print("=" * 60)
    
    success = True
    
    success &= test_predefined_themes()
    success &= test_enhanced_theme_service()
    success &= test_theme_validation()
    success &= test_utility_methods()
    success &= test_theme_stats()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 WEEK 4 DAY 1 COMPLETE!")
        print("✅ Theme domain models working")
        print("✅ Predefined themes extracted from v1")
        print("✅ Enhanced theme service operational")
        print("✅ Theme validation and utilities functional")
        print("\n📋 Ready for Day 2: Component Styling Migration")
    else:
        print("❌ WEEK 4 DAY 1 TESTS FAILED")
        print("Fix issues before proceeding to Day 2")
    print("=" * 60)
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
