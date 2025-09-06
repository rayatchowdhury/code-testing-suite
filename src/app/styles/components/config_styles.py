from src.app.styles.constants.colors import MATERIAL_COLORS
from src.app.styles.components.scrollbar import SCROLLBAR_STYLE

CONFIG_DIALOG_STYLE = f"""
    QDialog {{
        background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(18, 18, 20, 0.98),
            stop:0.3 rgba(22, 22, 24, 0.95),
            stop:0.7 rgba(18, 18, 20, 0.98),
            stop:1 rgba(22, 22, 24, 0.95));
        color: {MATERIAL_COLORS['on_surface']};
        font-family: 'Segoe UI', system-ui;
        font-size: 14px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }}
    
    QScrollArea {{
        background: transparent;
        border: none;
        outline: none;
    }}
    
    QScrollArea > QWidget {{
        background: transparent;
    }}
    
    QScrollArea > QWidget > QWidget {{
        background: transparent;
    }}
    
    QWidget#button_container {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                   stop:0 rgba(255, 255, 255, 0.02),
                   stop:1 rgba(255, 255, 255, 0.01));
        border-top: 1px solid rgba(255, 255, 255, 0.06);
    }}
    
    QWidget#section_frame {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                   stop:0 rgba(255, 255, 255, 0.06),
                   stop:1 rgba(255, 255, 255, 0.03));
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        margin: 2px 0px;
        padding: 6px;
    }}
    
    QWidget#section_frame:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                   stop:0 rgba(100, 181, 246, 0.1),
                   stop:1 rgba(255, 255, 255, 0.08));
        border: 1px solid rgba(100, 181, 246, 0.2);
    }}
    
    QLabel#section_title {{
        color: rgba(100, 181, 246, 0.87);
        font-size: 12px;
        font-weight: 600;
        padding: 8px 12px;
        background: transparent;
        border: none;
        margin: 2px 0px;
    }}
    
    QWidget#section_content {{
        padding: 12px;
        background: transparent;
        border: none;
    }}
    
    QComboBox, QLineEdit, QSpinBox {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                   stop:0 rgba(20, 24, 28, 0.8),
                   stop:1 rgba(14, 17, 20, 0.8));
        border: 1px solid {MATERIAL_COLORS['outline']};
        border-radius: 8px;
        color: {MATERIAL_COLORS['on_surface']};
        padding: 6px 12px;
        min-height: 20px;
        font-size: 14px;
        font-family: 'Segoe UI', system-ui;
        font-weight: 500;
        selection-background-color: {MATERIAL_COLORS['primary']}40;
        selection-color: {MATERIAL_COLORS['on_primary']};
    }}
    
    QComboBox:hover, QLineEdit:hover, QSpinBox:hover {{
        border: 1px solid {MATERIAL_COLORS['primary']};
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                   stop:0 {MATERIAL_COLORS['primary']}10,
                   stop:1 rgba(255, 255, 255, 0.08));
    }}
    
    QComboBox:focus, QLineEdit:focus, QSpinBox:focus {{
        border: 2px solid {MATERIAL_COLORS['primary']};
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                   stop:0 {MATERIAL_COLORS['primary']}15,
                   stop:1 rgba(255, 255, 255, 0.08));
        outline: none;
    }}
    
    QComboBox:disabled, QLineEdit:disabled, QSpinBox:disabled {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                   stop:0 rgba(20, 24, 28, 0.3),
                   stop:1 rgba(14, 17, 20, 0.3));
        border: 1px solid rgba(255, 255, 255, 0.02);
        color: {MATERIAL_COLORS['on_surface_disabled']};
    }}
    
    QComboBox::drop-down {{
        border: none;
        padding-right: 16px;
        background: transparent;
        width: 20px;
    }}
    
    QComboBox::down-arrow {{
        image: url(resources/icons/dropdown.png);
        width: 12px;
        height: 12px;
    }}
    
    QComboBox QAbstractItemView {{
        background: {MATERIAL_COLORS['surface']};
        border: 1px solid {MATERIAL_COLORS['outline']};
        border-radius: 8px;
        color: {MATERIAL_COLORS['on_surface']};
        selection-background-color: {MATERIAL_COLORS['primary']};
        selection-color: {MATERIAL_COLORS['on_primary']};
        outline: none;
    }}
    
    QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                   stop:0 rgba(255, 255, 255, 0.06),
                   stop:1 rgba(255, 255, 255, 0.03));
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        color: {MATERIAL_COLORS['on_surface']};
        padding: 10px 20px;
        min-height: 18px;
        font-weight: 500;
        font-size: 14px;
        font-family: 'Segoe UI', system-ui;
    }}
    
    QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                   stop:0 rgba(255, 255, 255, 0.06),
                   stop:1 rgba(255, 255, 255, 0.03));
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        color: {MATERIAL_COLORS['on_surface']};
        padding: 8px 16px;
        min-height: 18px;
        font-weight: 500;
        font-size: 14px;
        font-family: 'Segoe UI', system-ui;
    }}
    
    QPushButton#small_button {{
        padding: 4px;
        border-radius: 6px;
        font-size: 14px;
        min-width: 28px;
        min-height: 28px;
    }}
    
    QPushButton#small_button:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                   stop:0 rgba(100, 181, 246, 0.2),
                   stop:1 rgba(255, 255, 255, 0.1));
        border: 1px solid rgba(100, 181, 246, 0.4);
    }}
    
    QPushButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                   stop:0 rgba(100, 181, 246, 0.25),
                   stop:1 rgba(255, 255, 255, 0.08));
        border: 1px solid rgba(100, 181, 246, 0.60);
        color: {MATERIAL_COLORS['on_surface']};
    }}
    
    QPushButton:pressed {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                   stop:0 rgba(100, 181, 246, 0.20),
                   stop:1 rgba(255, 255, 255, 0.05));
        border: 1px solid rgba(100, 181, 246, 0.80);
    }}
    
    QPushButton#save_button {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                   stop:0 rgba(63, 131, 248, 0.8),
                   stop:1 rgba(37, 99, 235, 0.8));
        color: rgba(255, 255, 255, 0.95);
        border: 1px solid rgba(63, 131, 248, 0.6);
        font-weight: 600;
    }}
    
    QPushButton#save_button:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                   stop:0 rgba(63, 131, 248, 0.9),
                   stop:1 rgba(37, 99, 235, 0.9));
        border: 1px solid rgba(63, 131, 248, 0.8);
        color: rgba(255, 255, 255, 1.0);
    }}
    
    QPushButton#save_button:pressed {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                   stop:0 rgba(63, 131, 248, 0.7),
                   stop:1 rgba(37, 99, 235, 0.7));
    }}
    
    QPushButton#cancel_button {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                   stop:0 rgba(220, 38, 38, 0.15),
                   stop:1 rgba(185, 28, 28, 0.15));
        border: 1px solid rgba(220, 38, 38, 0.3);
        color: #FECACA;
    }}
    
    QPushButton#cancel_button:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                   stop:0 rgba(220, 38, 38, 0.25),
                   stop:1 rgba(185, 28, 28, 0.25));
        border: 1px solid rgba(220, 38, 38, 0.5);
        color: #FEF2F2;
    }}
    
    QPushButton#reset_button {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                   stop:0 rgba(251, 146, 60, 0.15),
                   stop:1 rgba(245, 101, 101, 0.15));
        border: 1px solid rgba(251, 146, 60, 0.3);
        color: #FED7AA;
    }}
    
    QPushButton#reset_button:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                   stop:0 rgba(251, 146, 60, 0.25),
                   stop:1 rgba(245, 101, 101, 0.25));
        border: 1px solid rgba(251, 146, 60, 0.5);
        color: #FFF7ED;
    }}
    
    QPushButton#save_button {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                   stop:0 {MATERIAL_COLORS['primary']},
                   stop:1 {MATERIAL_COLORS['primary_dark']});
        border: 1px solid {MATERIAL_COLORS['primary']};
        color: {MATERIAL_COLORS['on_primary']};
        font-weight: 600;
    }}
    
    QPushButton#save_button:hover {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                   stop:0 {MATERIAL_COLORS['primary']}E6,
                   stop:1 {MATERIAL_COLORS['primary_dark']}E6);
        border: 1px solid {MATERIAL_COLORS['primary']}E6;
    }}
    
    QPushButton#save_button:pressed {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                   stop:0 {MATERIAL_COLORS['primary']}CC,
                   stop:1 {MATERIAL_COLORS['primary_dark']}CC);
    }}
    
    QCheckBox {{
        color: {MATERIAL_COLORS['on_surface']};
        spacing: 8px;
        min-height: 24px;
        font-size: 14px;
        font-family: 'Segoe UI', system-ui;
        font-weight: 500;
        padding: 2px;
    }}
    
    QCheckBox:disabled {{
        color: {MATERIAL_COLORS['on_surface_disabled']};
    }}
    
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 1px solid {MATERIAL_COLORS['outline']};
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                   stop:0 rgba(20, 24, 28, 0.8),
                   stop:1 rgba(14, 17, 20, 0.8));
    }}
    
    QCheckBox::indicator:hover {{
        border: 1px solid {MATERIAL_COLORS['primary']};
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                   stop:0 {MATERIAL_COLORS['primary']}10,
                   stop:1 rgba(255, 255, 255, 0.08));
    }}
    
    QCheckBox::indicator:checked {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                   stop:0 {MATERIAL_COLORS['primary']},
                   stop:1 {MATERIAL_COLORS['primary_dark']});
        border: 1px solid {MATERIAL_COLORS['primary']};
        image: url(resources/icons/check.png);
    }}
    
    QCheckBox::indicator:checked:hover {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                   stop:0 {MATERIAL_COLORS['primary']}E6,
                   stop:1 {MATERIAL_COLORS['primary_dark']}E6);
    }}
    
    QCheckBox::indicator:disabled {{
        border: 1px solid rgba(255, 255, 255, 0.02);
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                   stop:0 rgba(20, 24, 28, 0.3),
                   stop:1 rgba(14, 17, 20, 0.3));
    }}
    
    QLabel {{
        color: {MATERIAL_COLORS['on_surface']};
        font-size: 14px;
        font-family: 'Segoe UI', system-ui;
        font-weight: 500;
    }}
    
    QSpinBox::up-button, QSpinBox::down-button {{
        border-radius: 4px;
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                   stop:0 rgba(255, 255, 255, 0.05),
                   stop:1 rgba(255, 255, 255, 0.02));
        min-width: 20px;
        border: 1px solid {MATERIAL_COLORS['outline']};
    }}
    
    QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                   stop:0 {MATERIAL_COLORS['primary']}30,
                   stop:1 rgba(255, 255, 255, 0.1));
        border: 1px solid {MATERIAL_COLORS['primary']};
    }}
    
    /* Database Management Button Styles */
    QPushButton#secondary_button {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                   stop:0 rgba(255, 255, 255, 0.08),
                   stop:1 rgba(255, 255, 255, 0.04));
        color: {MATERIAL_COLORS['on_surface']};
        border: 1px solid rgba(255, 255, 255, 0.12);
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 500;
        font-size: 13px;
    }}
    
    QPushButton#secondary_button:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                   stop:0 {MATERIAL_COLORS['primary']}40,
                   stop:1 {MATERIAL_COLORS['primary']}20);
        border: 1px solid {MATERIAL_COLORS['primary']};
    }}
    
    QPushButton#danger_button {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                   stop:0 {MATERIAL_COLORS['error']}80,
                   stop:1 {MATERIAL_COLORS['error']}60);
        color: white;
        border: 1px solid {MATERIAL_COLORS['error']};
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 13px;
    }}
    
    QPushButton#danger_button:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                   stop:0 {MATERIAL_COLORS['error']},
                   stop:1 {MATERIAL_COLORS['error']}90);
        border: 1px solid {MATERIAL_COLORS['error']};
    }}
    
    QLabel#info_label {{
        color: {MATERIAL_COLORS['on_surface_variant']};
        font-size: 13px;
        font-style: italic;
        padding: 8px;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 6px;
    }}
    
    QLabel#warning_label {{
        color: {MATERIAL_COLORS['error']};
        font-size: 12px;
        font-weight: 500;
        padding: 6px;
        background: rgba(244, 67, 54, 0.1);
        border: 1px solid rgba(244, 67, 54, 0.3);
        border-radius: 6px;
    }}
""" + SCROLLBAR_STYLE