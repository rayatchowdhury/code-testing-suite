# Code Testing Suite v2 - Clean Architecture Entry Point
"""
Application Entry Point for v2

Clean architecture entry point with dependency injection and proper service separation.
"""
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    """Main application entry point"""
    try:
        from app.application import create_application
        
        print("=" * 50)
        print("Code Testing Suite v2.0.0-alpha")
        print("Clean Architecture Implementation")
        print("=" * 50)
        
        # Create and run application
        app = create_application()
        success = app.run_console_mode()
        
        if success:
            print("\n🎉 v2 architecture is working correctly!")
        else:
            print("\n❌ v2 architecture validation failed")
            sys.exit(1)
            
        app.shutdown()
        
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
