# How to Optimize Your Database (Reclaim Space)

## Problem
After deleting test results, the database file stays large and doesn't shrink.

## Solution
Use the new "Optimize Database" feature!

---

## Step-by-Step Guide

### 1. Open Settings
Click the **⚙️ Settings** button in the main window toolbar.

### 2. Go to Database Management Tab
In the Settings dialog, click on the **"Database Management"** tab.

### 3. Check Current Size
Click **"Refresh Stats"** to see your current database statistics:
```
📊 Database Statistics:
• Test Results: 0
• Sessions: 0
• Database Size: 3.5 GB    ← This is the problem!
```

### 4. Optimize Database
Click the **"🔧 Optimize Database"** button (it's between "Cleanup Old Data" and "Delete ALL Data").

### 5. Confirm Optimization
You'll see a confirmation dialog:
```
Optimize Database

This will optimize the database file and reclaim unused space.

Current database size: 3.5 GB

This may take a few moments.

Continue?
```

Click **"Yes"** to continue.

### 6. See Results
After optimization, you'll see the results:
```
✅ Optimization Complete

Database successfully optimized!

Before: 3.5 MB
After: 0.03 MB
Space saved: 3.47 MB
```

### 7. Verify
Click **"Refresh Stats"** again to see the updated database size:
```
📊 Database Statistics:
• Test Results: 0
• Sessions: 0
• Database Size: 0.03 MB    ← Fixed! ✅
```

---

## When to Use Optimization

### Automatic (No Action Needed)
- After clicking "Delete ALL Data"
- After "Cleanup Old Data (30 days)"

### Manual (Click "Optimize Database")
- Database seems larger than expected
- After manually deleting many results
- Periodic maintenance (monthly)

---

## FAQ

**Q: Is optimization safe?**  
A: Yes! It's a standard SQLite operation that doesn't delete any data.

**Q: How long does it take?**  
A: A few seconds for typical databases. Larger databases take longer.

**Q: Will I lose data?**  
A: No! Optimization only reclaims empty space. All data is preserved.

**Q: Can I use the app during optimization?**  
A: The database is briefly locked (1-5 seconds). Just wait for the completion dialog.

**Q: How often should I optimize?**  
A: After deleting large amounts of data, or if the database size seems wrong.

---

## Button Location Reference

```
Settings Dialog
├── General
├── AI Configuration  
├── Test Configuration
└── Database Management  ← Click here
    ├── Database Statistics
    │   └── [Refresh Stats]
    ├── Database Operations
    │   ├── [Refresh Stats]
    │   ├── [Cleanup Old Data (30 days)]
    │   └── [🔧 Optimize Database]  ← New button!
    └── Dangerous Operations
        └── [⚠️ Delete ALL Data]
```

---

## Technical Note

**What "Optimize" does:**
- Runs SQLite's VACUUM command
- Rebuilds database file
- Removes empty pages from deleted records
- Shrinks file to actual data size

---

**Problem Fixed:** ✅  
**Available in:** Current version  
**Documentation:** See `docs/fixes/database_vacuum_fix.md` for technical details
