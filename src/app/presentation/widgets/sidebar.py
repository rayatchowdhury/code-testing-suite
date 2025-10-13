from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
    QLabel,
    QFrame,
    QScrollArea,
    QComboBox,
    QSpinBox,
    QSlider,
    QHBoxLayout,
)
from PySide6.QtCore import Qt, Signal
from src.app.presentation.styles import (
    SIDEBAR_STYLE,
    SIDEBAR_BUTTON_STYLE,
    SCROLLBAR_STYLE,
)
from src.app.presentation.styles.components.sidebar_dividers import (
    SIDEBAR_DIVIDER_CONTAINER_STYLE,
    SIDEBAR_DIVIDER_SPACE_STYLE,
    SIDEBAR_MAIN_DIVIDER_STYLE,
    SIDEBAR_FOOTER_CONTAINER_STYLE,
    SIDEBAR_FOOTER_SPACE_STYLE,
    SIDEBAR_FOOTER_DIVIDER_STYLE,
    SIDEBAR_VERTICAL_FOOTER_DIVIDER_STYLE,
)


class SidebarSection(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar_section")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Add section title
        if title:
            title_label = QLabel(title)
            title_label.setObjectName("section_title")
            layout.addWidget(title_label)

    def add_widget(self, widget):
        self.layout().addWidget(widget)


class Sidebar(QWidget):
    button_clicked = Signal(str)

    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setStyleSheet(SIDEBAR_STYLE)

        # Set consistent size constraints
        self.setMinimumWidth(250)
        self.setMaximumWidth(350)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)

        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Header Section
        self.header = QWidget()
        header_layout = QVBoxLayout(self.header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)

        # Add title widget for compatibility with tests
        self.windowTitleWidget = None
        if title:
            title_label = QLabel(title)
            title_label.setObjectName("sidebar_title")
            header_layout.addWidget(title_label)
            self.windowTitleWidget = title_label

        main_layout.addWidget(self.header)

        # Add divider after header
        self.add_divider(main_layout)

        # 2. Scrollable Content Section
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Ensure this is set
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setObjectName("sidebar_scroll")
        scroll.setStyleSheet(SCROLLBAR_STYLE)
        scroll.setFrameShape(QFrame.NoFrame)  # Add this line

        # Create content widget for scroll area
        self.content = QWidget()
        self.content.setObjectName("sidebar_content")
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        # Remove the addSpacing from here
        self.content_layout.setAlignment(Qt.AlignTop)

        scroll.setWidget(self.content)
        main_layout.addWidget(scroll)

        # 3. Footer Section (reordered)
        self.footer = QWidget()
        footer_layout = QVBoxLayout(self.footer)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(0)
        self.back_button = None

        # Add divider before adding footer
        self.add_divider(main_layout)

        # Now add the footer
        main_layout.addWidget(self.footer)

    def add_divider(self, layout):
        """Add a visually appealing horizontal divider line with padding."""
        # Create container for the divider section with background
        container = QWidget()
        container.setStyleSheet(SIDEBAR_DIVIDER_CONTAINER_STYLE)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # Add top spacing
        top_space = QWidget()
        top_space.setFixedHeight(10)
        top_space.setStyleSheet(SIDEBAR_DIVIDER_SPACE_STYLE)
        container_layout.addWidget(top_space)

        # Create a widget to serve as the divider
        line_widget = QWidget()
        line_widget.setFixedHeight(3)
        line_widget.setStyleSheet(SIDEBAR_MAIN_DIVIDER_STYLE)
        container_layout.addWidget(line_widget)

        # Add bottom spacing
        bottom_space = QWidget()
        bottom_space.setFixedHeight(10)
        bottom_space.setStyleSheet(SIDEBAR_DIVIDER_SPACE_STYLE)
        container_layout.addWidget(bottom_space)

        layout.addWidget(container)
        return line_widget

    def add_footer_divider(self):
        """Add a divider in the footer with the same style as the main divider"""
        # Create container for the footer divider section
        container = QWidget()
        container.setStyleSheet(SIDEBAR_FOOTER_CONTAINER_STYLE)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # Add top spacing
        top_space = QWidget()
        top_space.setFixedHeight(1)
        top_space.setStyleSheet(SIDEBAR_FOOTER_SPACE_STYLE)
        container_layout.addWidget(top_space)

        # Create a widget to serve as the divider
        line_widget = QWidget()
        line_widget.setFixedHeight(1)
        line_widget.setStyleSheet(SIDEBAR_FOOTER_DIVIDER_STYLE)
        container_layout.addWidget(line_widget)

        # Add bottom spacing
        bottom_space = QWidget()
        bottom_space.setFixedHeight(2)
        bottom_space.setStyleSheet(SIDEBAR_FOOTER_SPACE_STYLE)
        container_layout.addWidget(bottom_space)

        self.footer.layout().addWidget(container)
        return line_widget

    def add_vertical_footer_divider(self):
        """Add a vertical divider in the footer"""
        line_widget = QWidget()
        line_widget.setFixedWidth(1)
        line_widget.setMinimumHeight(30)  # Match button height
        # Apply a gradient background for a modern look
        line_widget.setStyleSheet(SIDEBAR_VERTICAL_FOOTER_DIVIDER_STYLE)
        return line_widget

    def setup_horizontal_footer_buttons(self, left_btn, right_btn):
        """Setup two buttons horizontally in the footer with a divider"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Add left button with 2/3 stretch
        layout.addWidget(left_btn, stretch=2)

        # Add vertical divider with no stretch
        layout.addWidget(self.add_vertical_footer_divider(), stretch=0)

        # Add right button with 1/3 stretch
        layout.addWidget(right_btn, stretch=1)

        self.footer.layout().addWidget(container)

    def add_section(self, title=None):
        section = SidebarSection(title)
        section.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Maximum
        )  # Add this line
        self.content_layout.addWidget(section)
        return section

    def add_button(self, text, section=None):
        btn = QPushButton(text)
        btn.setObjectName("sidebar_button")
        btn.clicked.connect(lambda: self.button_clicked.emit(text))

        if section:
            section.add_widget(btn)
        else:
            self.content_layout.addWidget(btn)
        return btn

    def add_spacer(self):
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.content_layout.addItem(spacer)

    def add_back_button(self):
        self.back_button = QPushButton("Back")
        self.back_button.setObjectName("footer_button")  # Changed from back_button
        self.back_button.clicked.connect(lambda: self.button_clicked.emit("Back"))
        self.footer.layout().addWidget(self.back_button)
        return self.back_button

    def add_results_button(self):
        results_btn = QPushButton("Results")
        results_btn.setObjectName("results_button")
        results_btn.clicked.connect(lambda: self.button_clicked.emit("Results"))
        self.footer.layout().addWidget(results_btn)
        self.results_button = results_btn  # Store reference
        self.results_button_index = self.footer.layout().count() - 1  # Store position
        return results_btn

    def replace_results_with_save_button(self):
        """Replace Results button with Save button for status view (Issue #39)"""
        # Get the position of results button before hiding it
        results_index = 0
        if hasattr(self, "results_button") and self.results_button:
            # Find the index of the results button in the layout
            for i in range(self.footer.layout().count()):
                if self.footer.layout().itemAt(i).widget() == self.results_button:
                    results_index = i
                    break
            self.results_button.hide()

        # Add save button at the same position with results_button style
        save_btn = QPushButton("Tests Running...")
        save_btn.setObjectName("results_button")  # Use same style as results button
        save_btn.setEnabled(False)  # Disabled until tests complete
        save_btn.clicked.connect(lambda: self.button_clicked.emit("Save"))
        self.footer.layout().insertWidget(results_index, save_btn)
        self.save_button = save_btn
        return save_btn

    def enable_save_button(self):
        """Enable save button when tests complete"""
        if hasattr(self, "save_button") and self.save_button:
            self.save_button.setEnabled(True)
            self.save_button.setText("💾 Save Results")

    def mark_results_saved(self):
        """Update save button to show results are saved"""
        if hasattr(self, "save_button") and self.save_button:
            self.save_button.setText("✓ Saved")
            self.save_button.setEnabled(False)

    def restore_results_button(self):
        """Restore Results button when leaving status view"""
        # Remove save button if it exists
        if hasattr(self, "save_button") and self.save_button:
            self.footer.layout().removeWidget(self.save_button)
            self.save_button.deleteLater()
            self.save_button = None

        # Restore results button if not already there
        if not hasattr(self, "results_button") or not self.results_button:
            self.add_results_button()
        else:
            # Show existing results button
            self.results_button.show()

    def add_footer_button_divider(self):
        """Add a simple divider between footer buttons"""
        self.add_footer_divider()

    def add_help_button(self):
        help_btn = QPushButton("Help Center")
        help_btn.setObjectName("footer_button")  # Changed from back_button
        help_btn.clicked.connect(lambda: self.button_clicked.emit("Help Center"))
        self.footer.layout().addWidget(help_btn)
        return help_btn
