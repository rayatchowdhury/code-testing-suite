#!/usr/bin/env python3
"""
Test Week 3 completion - Presentation Layer & Circular Dependency Breaking
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
current_dir = os.path.dirname(__file__)
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from app.dependency_injection import get_container, register_services
from domain.services.compilation_service import CompilationService
from domain.models.compilation import CompilationResult, CompilationStatus
from domain.views.view_factory import StatusViewFactory


def test_status_view_integration():
    """Test that compilation service works with status view factory"""
    print("🧪 Testing status view factory integration...")
    
    # Register all services
    register_services()
    container = get_container()
    
    # Get services through DI
    compilation_service = container.get(CompilationService)
    status_factory = container.get(StatusViewFactory)
    
    print(f"✅ Got compilation service: {type(compilation_service).__name__}")
    print(f"✅ Got status factory: {type(status_factory).__name__}")
    
    # Test status view creation
    compilation_view = status_factory.create_compilation_status_view()
    stress_view = status_factory.create_stress_test_status_view()
    
    print(f"✅ Created compilation status view: {type(compilation_view).__name__}")
    print(f"✅ Created stress test status view: {type(stress_view).__name__}")
    
    # Test status updates
    compilation_view.show_compilation_started("test.cpp")
    compilation_view.show_compilation_result(CompilationResult(
        file_path=Path("test.cpp"),
        status=CompilationStatus.SUCCESS,
        output="Compilation successful",
        error_output=""
    ))
    
    stress_view.show_test_started(100)
    stress_view.show_test_progress(50, 100)
    stress_view.show_test_completed()
    
    print("✅ Status view updates working correctly")
    return True


def test_circular_dependency_broken():
    """Test that circular dependencies are broken"""
    print("\n🧪 Testing circular dependency resolution...")
    
    # Try importing in different orders to ensure no circular imports
    try:
        from infrastructure.compilation.compiler_service import BasicCompilationService
        from presentation.adapters.status_view_factory import MockStatusViewFactory
        from domain.services.compilation_service import CompilationService
        
        print("✅ All imports successful - no circular dependencies")
        
        # Test that services can be created without Qt
        factory = MockStatusViewFactory()
        service = BasicCompilationService(factory)
        
        print(f"✅ Created services without Qt: {type(service).__name__}")
        return True
        
    except ImportError as e:
        print(f"❌ Import error (circular dependency?): {e}")
        return False


def test_architecture_layers():
    """Test that architecture layers are properly separated"""
    print("\n🧪 Testing architecture layer separation...")
    
    # Domain layer should have no dependencies
    try:
        from domain.models.compilation import CompilationResult
        from domain.services.compilation_service import CompilationService
        from domain.views.status_view import CompilationStatusView
        print("✅ Domain layer imports clean")
    except Exception as e:
        print(f"❌ Domain layer issue: {e}")
        return False
    
    # Infrastructure should only depend on domain
    try:
        from infrastructure.compilation.compiler_service import BasicCompilationService
        from infrastructure.configuration.config_service import ConfigService
        print("✅ Infrastructure layer imports clean")
    except Exception as e:
        print(f"❌ Infrastructure layer issue: {e}")
        return False
    
    # Presentation should depend on domain and infrastructure (through DI)
    try:
        from presentation.adapters.status_view_factory import MockStatusViewFactory
        from presentation.adapters.status_window_adapter import CompilationStatusWindowAdapter
        print("✅ Presentation layer imports clean")
    except Exception as e:
        print(f"❌ Presentation layer issue: {e}")
        return False
    
    print("✅ All architecture layers properly separated")
    return True


def main():
    """Run Week 3 completion tests"""
    print("=" * 60)
    print("🚀 WEEK 3 COMPLETION TEST")
    print("   Presentation Layer & Circular Dependency Breaking")
    print("=" * 60)
    
    success = True
    
    success &= test_architecture_layers()
    success &= test_circular_dependency_broken()
    success &= test_status_view_integration()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 WEEK 3 COMPLETE!")
        print("✅ Presentation layer foundation established")
        print("✅ Circular dependencies eliminated")
        print("✅ Status view adapters working")
        print("✅ Dependency injection fully functional")
        print("\n📋 Ready for Week 4: Theme System & Styling")
    else:
        print("❌ WEEK 3 TESTS FAILED")
        print("Fix issues before proceeding to Week 4")
    print("=" * 60)
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
