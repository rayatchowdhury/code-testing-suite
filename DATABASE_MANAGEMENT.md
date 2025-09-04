# Database Management Features

The application now includes comprehensive database management capabilities to help you maintain and control your test data.

## Features Added

### 1. GUI Database Management (Configuration Dialog)

Access through: `Main Menu → Settings/Configuration → Database Management Section`

**Features:**
- **Refresh Stats**: View current database statistics including:
  - Number of test results and sessions
  - Database size in MB
  - Date ranges of stored data
  
- **Cleanup Old Data**: Remove test results and sessions older than 30 days
  - Shows confirmation dialog with current data counts
  - Displays how much data was cleaned up
  
- **Delete ALL Data**: Permanently remove all data from the database
  - Strong safety measures with double confirmation
  - Requires typing "DELETE ALL" to confirm
  - Shows exactly what will be deleted

### 2. Command Line Interface (CLI)

**Usage:** `python database_manager_cli.py <command> [options]`

**Available Commands:**

```bash
# Show database statistics
python database_manager_cli.py stats

# Clean up data older than specific days (default: 30)
python database_manager_cli.py cleanup
python database_manager_cli.py cleanup 7    # Clean data older than 7 days

# Delete all data (requires manual confirmation)
python database_manager_cli.py delete-all

# Show help
python database_manager_cli.py help
```

### 3. Enhanced Database Manager Methods

**New Methods Added:**

- `delete_all_data(confirm=True)`: Safely delete all data with confirmation
- `get_database_stats()`: Retrieve comprehensive database statistics
- `cleanup_old_data(days)`: Fixed date arithmetic bug using proper timedelta

**Safety Features:**
- All deletion operations require explicit confirmation
- Statistics are shown before any destructive operations
- Proper error handling and rollback on failures
- Transaction-based operations for data integrity

## Statistics Provided

The database statistics include:

- **Test Results Count**: Total number of test executions stored
- **Sessions Count**: Total number of testing sessions
- **Database Size**: File size in MB and bytes
- **Date Ranges**: 
  - Oldest and newest test results
  - Oldest and newest sessions
- **Performance Metrics**: Database file size for maintenance planning

## Use Cases

### Regular Maintenance
```bash
# Check current database size
python database_manager_cli.py stats

# Clean up monthly (remove data older than 30 days)
python database_manager_cli.py cleanup
```

### Development/Testing
```bash
# Clear all test data for fresh start
python database_manager_cli.py delete-all
```

### Storage Management
- Monitor database growth through GUI stats
- Set up periodic cleanup routines
- Clear data when switching between projects

## Safety Considerations

1. **Backup Important Data**: Always backup important test results before cleanup
2. **Confirmation Required**: All destructive operations require explicit confirmation
3. **No Undo**: Deleted data cannot be recovered
4. **Transaction Safety**: Operations are atomic with proper rollback on errors

## Error Handling

The system includes comprehensive error handling for:
- Database connection issues
- File permission problems
- Invalid date operations
- Malformed data structures
- UI component failures

## Integration

Both GUI and CLI tools use the same underlying `DatabaseManager` class, ensuring consistent behavior across interfaces.
