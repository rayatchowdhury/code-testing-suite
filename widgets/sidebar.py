from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QSpacerItem,
                               QSizePolicy, QLabel, QFrame, QScrollArea, QComboBox,
                               QSpinBox, QSlider)
from PySide6.QtCore import Qt, Signal
from styles.style import SIDEBAR_STYLE, SIDEBAR_BUTTON_STYLE, SCROLLBAR_STYLE, COLORS


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
        if title:
            title_label = QLabel(title)
            title_label.setObjectName("sidebar_title")
            header_layout.addWidget(title_label)
        main_layout.addWidget(self.header)

        # Add divider after header
        self.add_divider(main_layout)

        # 2. Scrollable Content Section
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setObjectName("sidebar_scroll")
        scroll.setStyleSheet(SCROLLBAR_STYLE)

        # Create content widget for scroll area
        self.content = QWidget()
        self.content.setObjectName("sidebar_content")
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        # Add this line to align content to top
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
        """Add a horizontal divider line"""
        divider = QFrame()
        divider.setObjectName("sidebar_divider")
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Plain)
        divider.setLineWidth(1)
        divider.setMidLineWidth(0)
        divider.setFixedHeight(6)  # Total height including margins
        layout.addWidget(divider)
        return divider

    def add_section(self, title=None):
        section = SidebarSection(title)
        section.setSizePolicy(QSizePolicy.Preferred,
                              QSizePolicy.Maximum)  # Add this line
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
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum,
                             QSizePolicy.Expanding)
        self.content_layout.addItem(spacer)

    def add_back_button(self):
        self.back_button = QPushButton("Back")
        self.back_button.setObjectName("back_button")
        self.back_button.clicked.connect(
            lambda: self.button_clicked.emit("Back"))
        self.footer.layout().addWidget(self.back_button)
        return self.back_button

    def add_footer_divider(self):
        """Add a divider in the footer"""
        divider = QFrame()
        divider.setObjectName("footer_divider")
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Plain)
        divider.setLineWidth(1)
        divider.setMidLineWidth(0)
        divider.setFixedHeight(1)  # Thinner than regular divider
        self.footer.layout().addWidget(divider)
        return divider

    def add_help_button(self):
        help_btn = QPushButton("Help Center")
        help_btn.setObjectName("back_button")
        help_btn.clicked.connect(lambda: self.button_clicked.emit("Help Center"))
        self.footer.layout().addWidget(help_btn)
        return help_btn
