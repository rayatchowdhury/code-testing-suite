# ADR-001: Adopt src/ Layout Structure

## Status
Proposed

## Context  
Current project has flat structure mixing source code, tests, docs, and config files.
Industry standard is src/ layout for better organization and packaging.

## Decision
Adopt src/ layout with 4-layer architecture:
- `src/app/core/` - Business logic (AI services, testing services, config management)
- `src/app/persistence/` - Data layer (database operations, file operations, caching)
- `src/app/presentation/` - UI layer (feature-based organization, shared widgets, styling)
- `src/app/shared/` - Common utilities (constants, exceptions, utils, resources)

## Consequences
**Positive:**
- Clear separation of concerns
- Better testability and maintainability
- Standard project structure familiar to Python developers
- Easier packaging and deployment
- Supports future growth and team collaboration

**Negative:**  
- Requires import path updates throughout codebase
- Migration effort needed (estimated 16-20 hours)
- Temporary learning curve for developers familiar with current structure
- Risk of breaking functionality during migration (mitigated by comprehensive testing)
