"""Database operations for configuration management."""

from PySide6.QtWidgets import QInputDialog, QMessageBox
from src.app.presentation.services import ErrorHandlerService


class DatabaseOperations:
    """Handles database operations for the configuration dialog."""

    def __init__(self, parent_dialog, database_manager):
        self.parent = parent_dialog
        self.database_manager = database_manager

    def refresh_database_stats(self):
        """Refresh and display database statistics"""
        try:
            stats = self.database_manager.get_database_stats()
            if stats:
                stats_text = f"""📊 Database Statistics:
• Test Results: {stats['test_results_count']:,}
• Sessions: {stats['sessions_count']:,}
• Database Size: {stats['database_size_mb']} MB

📅 Date Ranges:
• Tests: {stats['oldest_test']} → {stats['newest_test']}
• Sessions: {stats['oldest_session']} → {stats['newest_session']}"""
                self.parent.db_stats_label.setText(stats_text)
            else:
                self.parent.db_stats_label.setText(
                    "❌ Could not retrieve database statistics"
                )
        except Exception as e:
            self.parent.db_stats_label.setText(f"❌ Error retrieving stats: {str(e)}")

    def cleanup_old_data(self):
        """Clean up old data with user confirmation"""
        error_service = ErrorHandlerService.instance()
        try:
            # Get current stats
            stats = self.database_manager.get_database_stats()
            if not stats:
                error_service.show_warning(
                    "Error", "Could not retrieve database statistics", self.parent
                )
                return

            # Show confirmation dialog
            reply = error_service.ask_question(
                "Cleanup Old Data",
                f"This will delete test results and sessions older than 30 days.\n\n"
                f"Current database contents:\n"
                f"• {stats['test_results_count']:,} test results\n"
                f"• {stats['sessions_count']:,} sessions\n"
                f"• {stats['database_size_mb']} MB total size\n\n"
                f"Continue with cleanup?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
                self.parent
            )

            if reply == QMessageBox.Yes:
                # Get stats before cleanup
                stats_before = self.database_manager.get_database_stats()

                # Perform cleanup
                self.database_manager.cleanup_old_data(30)

                # Get stats after cleanup
                stats_after = self.database_manager.get_database_stats()

                if stats_before and stats_after:
                    deleted_tests = (
                        stats_before["test_results_count"]
                        - stats_after["test_results_count"]
                    )
                    deleted_sessions = (
                        stats_before["sessions_count"] - stats_after["sessions_count"]
                    )

                    error_service.show_success(
                        "Cleanup Complete",
                        f"Successfully cleaned up old data:\n"
                        f"• Deleted {deleted_tests} test results\n"
                        f"• Deleted {deleted_sessions} sessions",
                        self.parent
                    )

                    # Refresh the stats display
                    self.refresh_database_stats()
                else:
                    error_service.show_success(
                        "Cleanup Complete", "Data cleanup completed", self.parent
                    )

        except Exception as e:
            error_service.show_error(
                "Cleanup Error", f"Failed to cleanup data: {str(e)}", self.parent
            )

    def delete_all_data(self):
        """Delete all data with strong confirmation"""
        error_service = ErrorHandlerService.instance()
        try:
            # Get current stats
            stats = self.database_manager.get_database_stats()
            if not stats:
                error_service.show_warning(
                    "Error", "Could not retrieve database statistics", self.parent
                )
                return

            if stats["test_results_count"] == 0 and stats["sessions_count"] == 0:
                error_service.show_info(
                    "No Data", "Database is already empty", self.parent
                )
                return

            # First confirmation
            reply1 = error_service.ask_question(
                "⚠️ DELETE ALL DATA",
                f"🚨 WARNING: This will permanently delete ALL data!\n\n"
                f"Current database contents:\n"
                f"• {stats['test_results_count']:,} test results\n"
                f"• {stats['sessions_count']:,} sessions\n"
                f"• {stats['database_size_mb']} MB total size\n\n"
                f"This action CANNOT be undone!\n\n"
                f"Are you absolutely sure you want to continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
                self.parent
            )

            if reply1 != QMessageBox.Yes:
                return

            # Second confirmation with text input
            text, ok = QInputDialog.getText(
                self.parent,
                "Final Confirmation",
                f"To confirm deletion of ALL data, type exactly:\nDELETE ALL\n\n"
                f"This will delete {stats['test_results_count']:,} test results and {stats['sessions_count']:,} sessions permanently.",
            )

            if not ok or text.strip() != "DELETE ALL":
                error_service.show_info(
                    "Cancelled", "Data deletion cancelled", self.parent
                )
                return

            # Perform deletion
            success = self.database_manager.delete_all_data(confirm=True)

            if success:
                error_service.show_success(
                    "✅ Data Deleted",
                    "All data has been successfully deleted from the database.\n"
                    "The database is now empty.",
                    self.parent
                )
                # Refresh the stats display
                self.refresh_database_stats()
            else:
                error_service.show_error(
                    "Deletion Failed",
                    "Failed to delete data. Check console for details.",
                    self.parent
                )

        except Exception as e:
            error_service.show_error(
                "Deletion Error", f"Failed to delete data: {str(e)}", self.parent
            )

    def optimize_database(self):
        """Optimize database by reclaiming unused space"""
        error_service = ErrorHandlerService.instance()
        try:
            # Get current stats
            stats = self.database_manager.get_database_stats()
            if not stats:
                error_service.show_warning(
                    "Error", "Could not retrieve database statistics", self.parent
                )
                return

            current_size = stats["database_size_mb"]

            # Show confirmation
            reply = error_service.ask_question(
                "Optimize Database",
                f"This will optimize the database file and reclaim unused space.\n\n"
                f"Current database size: {current_size} MB\n\n"
                f"This may take a few moments.\n\n"
                f"Continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
                self.parent
            )

            if reply != QMessageBox.Yes:
                return

            # Perform optimization
            result = self.database_manager.optimize_database()

            if result:
                space_saved = result["space_saved_mb"]
                size_before = result["size_before_mb"]
                size_after = result["size_after_mb"]

                if space_saved > 0.01:  # More than 10 KB saved
                    error_service.show_success(
                        "✅ Optimization Complete",
                        f"Database successfully optimized!\n\n"
                        f"Before: {size_before} MB\n"
                        f"After: {size_after} MB\n"
                        f"Space saved: {space_saved} MB",
                        self.parent
                    )
                else:
                    error_service.show_success(
                        "✅ Optimization Complete",
                        f"Database is already optimized.\n\n"
                        f"Current size: {size_after} MB\n"
                        f"No significant space to reclaim.",
                        self.parent
                    )

                # Refresh the stats display
                self.refresh_database_stats()
            else:
                error_service.show_error(
                    "Optimization Failed",
                    "Failed to optimize database. Check console for details.",
                    self.parent
                )

        except Exception as e:
            error_service.show_error(
                "Optimization Error",
                f"Failed to optimize database: {str(e)}",
                self.parent
            )
