#!/usr/bin/env python3
"""
Database Manager CLI - Command line interface for managing the test database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database_manager import DatabaseManager


def print_stats(stats):
    """Print database statistics in a readable format"""
    if not stats:
        print("❌ Could not retrieve database statistics")
        return
    
    print("\n📊 Database Statistics:")
    print("=" * 50)
    print(f"Test Results: {stats['test_results_count']:,}")
    print(f"Sessions: {stats['sessions_count']:,}")
    print(f"Database Size: {stats['database_size_mb']} MB ({stats['database_size_bytes']:,} bytes)")
    print()
    print("📅 Date Ranges:")
    print(f"Test Results: {stats['oldest_test']} → {stats['newest_test']}")
    print(f"Sessions: {stats['oldest_session']} → {stats['newest_session']}")
    print("=" * 50)


def main():
    """Main CLI interface"""
    db = DatabaseManager()
    
    if len(sys.argv) < 2:
        print("🗄️  Database Manager CLI")
        print()
        print("Usage: python database_manager_cli.py <command> [options]")
        print()
        print("Commands:")
        print("  stats           - Show database statistics")
        print("  cleanup <days>  - Delete data older than <days> (default: 30)")
        print("  delete-all      - Delete ALL data (requires confirmation)")
        print("  help            - Show this help message")
        print()
        print("Examples:")
        print("  python database_manager_cli.py stats")
        print("  python database_manager_cli.py cleanup 7")
        print("  python database_manager_cli.py delete-all")
        return
    
    command = sys.argv[1].lower()
    
    if command == "stats":
        print("📊 Retrieving database statistics...")
        stats = db.get_database_stats()
        print_stats(stats)
    
    elif command == "cleanup":
        days = 30  # default
        if len(sys.argv) > 2:
            try:
                days = int(sys.argv[2])
            except ValueError:
                print("❌ Error: Days must be a number")
                return
        
        print(f"🧹 Cleaning up data older than {days} days...")
        stats_before = db.get_database_stats()
        
        db.cleanup_old_data(days)
        
        stats_after = db.get_database_stats()
        if stats_before and stats_after:
            deleted_tests = stats_before['test_results_count'] - stats_after['test_results_count']
            deleted_sessions = stats_before['sessions_count'] - stats_after['sessions_count']
            print(f"✅ Cleanup complete!")
            print(f"   Deleted {deleted_tests} test results")
            print(f"   Deleted {deleted_sessions} sessions")
        
        print_stats(stats_after)
    
    elif command == "delete-all":
        print("⚠️  WARNING: This will delete ALL data from the database!")
        print("   This action cannot be undone.")
        print()
        
        # Show current stats
        stats = db.get_database_stats()
        if stats:
            print("Current database contents:")
            print(f"  - {stats['test_results_count']} test results")
            print(f"  - {stats['sessions_count']} sessions")
            print(f"  - {stats['database_size_mb']} MB total size")
            print()
        
        confirm = input("Type 'DELETE ALL' to confirm: ").strip()
        
        if confirm == "DELETE ALL":
            print("🗑️  Deleting all data...")
            success = db.delete_all_data(confirm=True)
            if success:
                print("✅ All data has been deleted successfully!")
                print_stats(db.get_database_stats())
            else:
                print("❌ Failed to delete data. Check error messages above.")
        else:
            print("❌ Deletion cancelled - confirmation text did not match")
    
    elif command == "help":
        print("🗄️  Database Manager CLI")
        print()
        print("Usage: python database_manager_cli.py <command> [options]")
        print()
        print("Commands:")
        print("  stats           - Show database statistics")
        print("  cleanup <days>  - Delete data older than <days> (default: 30)")
        print("  delete-all      - Delete ALL data (requires confirmation)")
        print("  help            - Show this help message")
        print()
        print("Examples:")
        print("  python database_manager_cli.py stats")
        print("  python database_manager_cli.py cleanup 7")
        print("  python database_manager_cli.py delete-all")
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'help' to see available commands")


if __name__ == "__main__":
    main()
