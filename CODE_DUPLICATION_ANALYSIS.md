# Code Duplication Analysis Report
**Date:** October 21, 2025  
**Analysis Tool:** Pylint (duplicate-code checker)  
**Scope:** src/app/presentation  
**Rating:** 9.96/10

## Executive Summary

Pylint detected **24 instances of code duplication** in the presentation layer. The duplications fall into several categories:

### Duplication Categories

1. **Test Window Initialization** (Highest Priority)
   - Sidebar setup code duplicated across 3 test windows
   - Button creation and connection logic
   - ~25-35 lines per window

2. **Export Functionality** (High Priority)
   - Test results export logic duplicated
   - ZIP file creation and formatting
   - ~40 lines duplicated

3. **Status View Initialization** (Medium Priority)
   - Widget creation and layout setup
   - Presenter initialization
   - ~15-30 lines per view

4. **Compilation Checks** (Medium Priority)
   - Unsaved changes validation
   - Dialog prompts
   - ~15-25 lines duplicated

5. **Styling Constants** (Low Priority)
   - Font and spacing configuration
   - Style definitions
   - ~10-15 lines per file

---

## Detailed Findings

### 1. Test Window Sidebar Setup (CRITICAL)
**Files Affected:**
- `benchmarker_window.py` [78:102]
- `comparator_window.py` [42:66]
- `validator_window.py` [32:66, 42:67]

**Duplicated Code:**
```python
for button_text in ["Compile", "Run"]:
    btn = self.sidebar.add_button(button_text, self.action_section)
    btn.clicked.connect(
        lambda _, text=button_text: self.handle_action_button(text)
    )
    if button_text == "Compile":
        self.compile_btn = btn
    elif button_text == "Run":
        self.run_btn = btn

self.sidebar.add_results_button()
self.sidebar.add_footer_button_divider()
self.sidebar.add_help_button()
self.sidebar.add_footer_divider()

back_btn, options_btn = self.create_footer_buttons()
self.sidebar.setup_horizontal_footer_buttons(back_btn, options_btn)

# Create display area and testing content
self.display_area = DisplayArea()

tab_config = {
    "Generator": {"cpp": "generator.cpp", "py": "generator.py", "java": "Generator.java"},
    ...
}
```

**Recommendation:** Extract to `TestWindowBase._setup_standard_sidebar()` method

**Impact:** ~75 lines reduction (25 lines × 3 files)

---

### 2. Test Results Export (HIGH PRIORITY)
**Files Affected:**
- `detailed_results_window.py` [536:574]
- `results_window.py` [156:194]

**Duplicated Code:**
```python
for i, test_case in enumerate(test_data, 1):
    test_num = test_case.get("test", i)
    status = test_case.get("status", "unknown")

    # Create test case file content
    test_content = f"Test #{test_num}\n"
    test_content += f"Status: {status}\n"
    test_content += f"{'='*50}\n\n"

    if "input" in test_case:
        test_content += f"INPUT:\n{test_case['input']}\n\n"

    if "output" in test_case:
        test_content += f"EXPECTED OUTPUT:\n{test_case['output']}\n\n"

    if "actual_output" in test_case:
        test_content += f"ACTUAL OUTPUT:\n{test_case['actual_output']}\n\n"

    if "error" in test_case:
        test_content += f"ERROR:\n{test_case['error']}\n\n"

    if "execution_time" in test_case:
        test_content += f"Execution Time: {test_case['execution_time']} seconds\n"

    # Save to appropriate folder
    folder = "passed" if status.lower() == "pass" else "failed"
    zipf.writestr(f"{folder}/test_{test_num}.txt", test_content.encode("utf-8"))

# 3. Create summary file
summary = "Test Results Export\n"
summary += f"{'='*60}\n\n"
```

**Recommendation:** Extract to utility function `export_test_results_to_zip(test_data, zipf)`

**Impact:** ~40 lines reduction

---

### 3. Status View Save Results (HIGH PRIORITY)
**Files Affected:**
- `status_view_base.py` [240:267]
- `benchmarker_status_view.py` [198:225]

**Duplicated Code:**
```python
if not runner:
    QMessageBox.critical(self, "Error", "Runner not found")
    return -1

try:
    result_id = runner.save_test_results_to_database()
    if result_id > 0:
        QMessageBox.information(
            self, "Success",
            f"Results saved!\nDatabase ID: {result_id}"
        )
        if self.parent_window and hasattr(self.parent_window, "mark_results_saved"):
            self.parent_window.mark_results_saved()
    else:
        QMessageBox.critical(self, "Error", "Failed to save")
    return result_id
except Exception as e:
    QMessageBox.critical(self, "Error", f"Error saving: {e}")
    return -1
```

**Recommendation:** Keep in base class only (appears to already be there - verify override necessity)

**Impact:** ~28 lines reduction

---

### 4. Status View Initialization (MEDIUM PRIORITY)
**Files Affected:**
- `status_view_base.py` [154:170, 171:204]
- `benchmarker_status_view.py` [60:76, 77:126]

**Duplicated Code:**
```python
layout = QVBoxLayout(self)
layout.setContentsMargins(0, 0, 0, 0)
layout.setSpacing(0)

# Create widgets
self.header = StatusHeaderSection()
self.performance = PerformancePanelSection()
self.progress_bar = VisualProgressBarSection()
self.cards_section = TestResultsCardsSection()

# Create presenter
self.presenter = StatusViewPresenter(
    header=self.header,
    performance=self.performance,
    progress_bar=self.progress_bar,
    cards_section=self.cards_section,
)

# Add to layout
layout.addWidget(self.header)
layout.addWidget(self.performance)
layout.addWidget(self.progress_bar)
layout.addWidget(self.cards_section, stretch=1)
```

**Recommendation:** Already in base class - remove from subclasses or verify if overriding is needed

**Impact:** ~50 lines reduction

---

### 5. Compilation Unsaved Changes Check (MEDIUM PRIORITY)
**Files Affected:**
- `benchmarker_window.py` [164:187]
- `comparator_window.py` [147:171]
- `validator_window.py` [147:163]

**Duplicated Code:**
```python
if button_text == "Compile":
    # Clear console
    self.testing_content.console.clear()

    # Check for unsaved changes
    for btn_name, btn in self.testing_content.file_buttons.items():
        if btn.property("hasUnsavedChanges"):
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                f"Do you want to save changes to {btn_name}?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            )

            if reply == QMessageBox.Save:
                self.testing_content._handle_file_button(
                    btn_name, skip_save_prompt=True
                )
                if not self.testing_content.editor.saveFile():
                    return
            elif reply == QMessageBox.Cancel:
                return
```

**Recommendation:** Extract to `TestWindowBase._check_unsaved_changes()` method

**Impact:** ~60 lines reduction (20 lines × 3 files)

---

### 6. Document Widget Base (MEDIUM PRIORITY)
**Files Affected:**
- `help_center/document.py` [70:82, 83:100, 102:133]
- `main_window/document.py` [79:91, 92:109, 112:143]

**Duplicated Code:**
- Document initialization
- Scroll area setup
- Fade-in animation
- Base styling

**Recommendation:** Extract to shared base class `GlassmorphismDocumentBase`

**Impact:** ~80 lines reduction

---

### 7. Tool Initialization (LOW PRIORITY)
**Files Affected:**
- `comparator_window.py` [76:102]
- `validator_window.py` [76:102]

**Duplicated Code:**
```python
self.display_area.set_content(self.testing_content)

# Setup splitter with sidebar and display area
self.setup_splitter(self.sidebar, self.display_area)

# Connect signals
self.sidebar.button_clicked.connect(self.handle_button_click)

# Initialize tool with multi-language support
self._initialize_tool()

# Connect filesManifestChanged signal to reinitialize tool
self.testing_content.test_tabs.filesManifestChanged.connect(self._on_files_changed)
```

**Recommendation:** Extract to `TestWindowBase._finalize_window_setup()` method

**Impact:** ~50 lines reduction

---

### 8. Configuration Refresh (LOW PRIORITY)
**Files Affected:**
- `content_window_base.py` [200:217]
- `base_window.py` [110:130]

**Duplicated Code:**
```python
try:
    from src.app.core.ai import reload_ai_config
    reload_ai_config()
except ImportError:
    pass  # AI module not available

# Refresh AI panels with new configuration
if hasattr(self, "refresh_ai_panels"):
    self.refresh_ai_panels()

# Reinitialize tools to pick up new compilation settings
if hasattr(self, "_initialize_tool"):
    self._initialize_tool()
```

**Recommendation:** Extract to `ContentWindowBase._reload_configuration()` method

**Impact:** ~30 lines reduction

---

### 9. Styling Constants Duplication (LOW PRIORITY)
**Files Affected:**
- Multiple style files with shared font/spacing constants
- `console.py` [41:55] vs `sidebar.py` [19:33]
- `help_center/document.py` [20:34] vs `main_window/document.py` [20:34]

**Recommendation:** Consolidate into `styles/constants.py`

**Impact:** ~50 lines reduction

---

### 10. Minor Duplications (LOW PRIORITY)
- Splitter setup code (~10 lines)
- Test detail dialog code (~12 lines)
- Button style definitions (~10 lines)
- Unsaved changes dialogs (~8 lines each)

**Recommendation:** Extract to utility functions as needed

**Impact:** ~50 lines reduction

---

## Prioritized Refactoring Plan

### Phase A: Test Window Refactoring (HIGH IMPACT)
**Estimated Reduction:** ~185 lines

1. Extract `TestWindowBase._setup_standard_sidebar()` for sidebar initialization
2. Extract `TestWindowBase._check_unsaved_changes()` for compilation checks
3. Extract `TestWindowBase._finalize_window_setup()` for tool initialization

**Files to modify:**
- `base/test_window_base.py` (add methods)
- `benchmarker_window.py` (use base methods)
- `comparator_window.py` (use base methods)
- `validator_window.py` (use base methods)

---

### Phase B: Results Export Refactoring (HIGH IMPACT)
**Estimated Reduction:** ~40 lines

1. Create `services/export_service.py`
2. Add `export_test_results_to_zip(test_data, zipf)` function
3. Add `create_export_summary(metadata)` function

**Files to modify:**
- Create `services/export_service.py` (new)
- `views/results/results_window.py` (use service)
- `views/results/detailed_results_window.py` (use service)

---

### Phase C: Status View Cleanup (MEDIUM IMPACT)
**Estimated Reduction:** ~78 lines

1. Verify if `benchmarker_status_view.py` overrides are necessary
2. Remove duplicated initialization if already in base
3. Remove duplicated save_results if already in base

**Files to modify:**
- `views/benchmarker/benchmarker_status_view.py` (remove overrides)

---

### Phase D: Document Base Class (MEDIUM IMPACT)
**Estimated Reduction:** ~80 lines

1. Create `base/glassmorphism_document_base.py`
2. Extract common document initialization
3. Migrate help_center and main_window documents

**Files to modify:**
- Create `base/glassmorphism_document_base.py` (new)
- `views/help_center/document.py` (inherit from base)
- `views/main_window/document.py` (inherit from base)

---

### Phase E: Style Constants Consolidation (LOW IMPACT)
**Estimated Reduction:** ~50 lines

1. Create `styles/shared_constants.py`
2. Consolidate FONTS, SPACING, COLORS
3. Update imports across style files

**Files to modify:**
- Create `styles/shared_constants.py` (new)
- Update all files importing duplicated constants

---

## Overall Impact Summary

| Phase | Priority | Lines Saved | Files Modified | Complexity |
|-------|----------|-------------|----------------|------------|
| A - Test Windows | HIGH | ~185 | 4 | Medium |
| B - Export Service | HIGH | ~40 | 3 | Low |
| C - Status Views | MEDIUM | ~78 | 1 | Low |
| D - Document Base | MEDIUM | ~80 | 3 | Medium |
| E - Style Constants | LOW | ~50 | 10+ | Low |
| **TOTAL** | | **~433 lines** | **20+ files** | |

---

## Recommendations

### Immediate Actions (Do Now)
1. **Phase A** - Highest ROI, improves maintainability of test windows
2. **Phase B** - Clear duplication, easy to extract

### Short-term (Next Session)
3. **Phase C** - Quick verification and cleanup
4. **Phase D** - Improves document architecture

### Long-term (Future Enhancement)
5. **Phase E** - Nice-to-have, low priority

---

## Notes

- Current code rating: **9.96/10** (excellent starting point)
- Most duplications are in window initialization logic
- Base classes already exist but aren't fully utilized
- Extract-to-method refactoring is low-risk
- All changes should maintain existing functionality
- Test after each phase to ensure no regressions

---

## Related Files

- Main analysis: `code_duplication_report.txt`
- Dead code report: `phase3_verification.txt`
- Dead code finder: `find_dead_code.py`
- README: `FIND_DEAD_CODE_README.md`
