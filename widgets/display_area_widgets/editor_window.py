from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from .editor import EditorWidget
from .console import ConsoleOutput
from styles.style import MATERIAL_COLORS, SCROLLBAR_STYLE  # Add SCROLLBAR_STYLE import

class EditorWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Apply scrollbar style to the entire editor window
        self.setStyleSheet(SCROLLBAR_STYLE)

        # Add editor widget (includes title bar)
        self.editor = EditorWidget()
        
        # Create middle section with editor and console
        middle_container = QHBoxLayout()
        middle_container.setSpacing(1)  # Small gap between editor and console
        
        # Add editor (70% of width)
        middle_container.addWidget(self.editor, 70)
        
        # Add console (30% of width)
        self.console = ConsoleOutput()
        middle_container.addWidget(self.console, 30)
        
        # Create bottom button container
        bottom_container = QWidget()
        bottom_layout = QHBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(10, 10, 10, 10)
        bottom_layout.setSpacing(10)  # Add spacing between buttons
        
        # Add compile and run buttons
        self.compile_btn = QPushButton("Compile")
        self.run_btn = QPushButton("Run")
        
        # Style buttons
        button_style = f"""
            QPushButton {{
                background-color: {MATERIAL_COLORS['primary']};
                color: {MATERIAL_COLORS['text_primary']};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 120px;  /* Set minimum width */
            }}
            QPushButton:hover {{
                background-color: {MATERIAL_COLORS['surface_variant']};
            }}
        """
        self.compile_btn.setStyleSheet(button_style)
        self.run_btn.setStyleSheet(button_style)
        
        # Add buttons with stretch for equal width
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(self.compile_btn, 2)
        bottom_layout.addWidget(self.run_btn, 2)
        bottom_layout.addStretch(1)
        
        # Add all sections to main layout
        layout.addLayout(middle_container)
        layout.addWidget(bottom_container)
        
        # Connect signals
        self.compile_btn.clicked.connect(self.compile_code)
        self.run_btn.clicked.connect(self.run_code)

        # Update console style to include scrollbar
        self.console.setStyleSheet(SCROLLBAR_STYLE + f"""
            QWidget {{
                background-color: {MATERIAL_COLORS['surface']};
                color: {MATERIAL_COLORS['text_primary']};
            }}
        """)

    def compile_code(self):
        # TODO: Implement compilation logic
        self.console.displayOutput("Compiling...")

    def run_code(self):
        # TODO: Implement run logic
        self.console.displayOutput("Running...")
