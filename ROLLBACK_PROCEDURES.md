# Emergency Rollback Procedures

## Level 1: Step Rollback (Minor Issues)
```powershell
# Undo last commit
git reset --hard HEAD~1

# Or undo specific changes
git checkout HEAD~1 -- path/to/file
```

## Level 2: Phase Rollback (Major Issues)
```powershell
# Find last phase commit
git log --oneline | Select-String "Phase.*Complete"

# Reset to specific phase
git reset --hard <commit-hash>
```

## Level 3: Complete Rollback (Critical Issues)
```powershell
# Return to pre-migration state
git checkout migration-backup-*
# OR
git reset --hard pre-migration-*

# If all else fails, restore from backup
tar -xzf migration_backups/phase_1_start_*.tar.gz
```

## Validation After Rollback
```powershell
# Test app functionality
python main.py  # Should not crash
python -c "import main; print('✅ Basic import works')"
```

## Emergency Contacts & Resources
- **Migration Lead**: GitHub Copilot
- **Backup Location**: `migration_backups/`
- **Git Tags**: All pre-migration states tagged with timestamps
- **Recovery Time**: Estimated 5-15 minutes depending on rollback level
