# -*- coding: utf-8 -*-
"""
Test View Styles - Modular organization.

This package contains all styling for test views (comparator, benchmarker, validator),
split into logical modules for better maintainability.
"""

from .test_editor_styles import (
    TEST_VIEW_BUTTON_PANEL_STYLE,
    TEST_VIEW_FILE_BUTTON_STYLE,
    TEST_VIEW_CONTENT_PANEL_STYLE,
    TEST_VIEW_SLIDER_STYLE,
    TEST_VIEW_SLIDER_VALUE_LABEL_STYLE,
)
from .test_control_styles import (
    TEST_VIEW_STATUS_DIALOG_STYLE,
    TEST_VIEW_HISTORY_ITEM_STYLE,
    TEST_VIEW_COMPILATION_STATUS_DIALOG_STYLE,
    TEST_VIEW_COMPILATION_STATUS_LABEL_STYLE,
    TEST_VIEW_COMPILATION_PROGRESS_BAR_STYLE,
    TEST_VIEW_COMPILATION_DETAIL_LABEL_STYLE,
    TEST_VIEW_COMPILATION_CLOSE_BUTTON_STYLE,
    TEST_VIEW_STATUS_LABEL_STYLE,
    TEST_VIEW_TIME_LABEL_STYLE,
    get_history_label_style,
    get_running_status_style,
    get_test_view_error_status_style,
    get_test_view_success_status_style,
    get_compilation_status_style,
    get_status_label_style,
    get_passed_status_style,
    get_failed_status_style,
)
from .test_tab_styles import (
    TAB_CONTAINER_STYLE,
    TAB_FILE_BUTTON_STYLE,
    TAB_FILE_BUTTON_SINGLE_STYLE,
    LANGUAGE_CONTAINER_STYLE,
    LANGUAGE_LABEL_STYLE,
    LANGUAGE_CONTEXT_MENU_STYLE,
    get_file_button_style,
)

__all__ = [
    # Editor styles
    "TEST_VIEW_BUTTON_PANEL_STYLE",
    "TEST_VIEW_FILE_BUTTON_STYLE",
    "TEST_VIEW_CONTENT_PANEL_STYLE",
    "TEST_VIEW_SLIDER_STYLE",
    "TEST_VIEW_SLIDER_VALUE_LABEL_STYLE",
    # Control styles
    "TEST_VIEW_STATUS_DIALOG_STYLE",
    "TEST_VIEW_HISTORY_ITEM_STYLE",
    "TEST_VIEW_COMPILATION_STATUS_DIALOG_STYLE",
    "TEST_VIEW_COMPILATION_STATUS_LABEL_STYLE",
    "TEST_VIEW_COMPILATION_PROGRESS_BAR_STYLE",
    "TEST_VIEW_COMPILATION_DETAIL_LABEL_STYLE",
    "TEST_VIEW_COMPILATION_CLOSE_BUTTON_STYLE",
    "TEST_VIEW_STATUS_LABEL_STYLE",
    "TEST_VIEW_TIME_LABEL_STYLE",
    # Tab styles
    "TAB_CONTAINER_STYLE",
    "TAB_FILE_BUTTON_STYLE",
    "TAB_FILE_BUTTON_SINGLE_STYLE",
    "LANGUAGE_CONTAINER_STYLE",
    "LANGUAGE_LABEL_STYLE",
    "LANGUAGE_CONTEXT_MENU_STYLE",
    # Utility functions
    "get_history_label_style",
    "get_running_status_style",
    "get_test_view_error_status_style",
    "get_test_view_success_status_style",
    "get_compilation_status_style",
    "get_status_label_style",
    "get_passed_status_style",
    "get_failed_status_style",
    "get_file_button_style",
]
