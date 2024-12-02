CONFIG_DIALOG_STYLE = """
    QDialog {
        background-color: #1e1e1e;
        color: #e0e0e0;
    }
    #section_frame {
        background-color: #252525;
        border-radius: 4px;
        border: 1px solid #383838;
        margin: 2px;
    }
    #section_frame:hover {
        border: 1px solid #454545;
        background-color: #2a2a2a;
    }
    #section_title {
        color: #58a6ff;
        font-size: 13px;
        font-weight: bold;
        padding: 6px 8px;
        background-color: #2d2d2d;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        border-bottom: 1px solid #383838;
    }
    #section_content {
        padding: 8px;
    }
    QComboBox, QLineEdit, QSpinBox {
        background-color: #2d2d2d;
        border: 1px solid #404040;
        border-radius: 3px;
        color: #e0e0e0;
        padding: 3px 5px;
        min-height: 18px;
        font-size: 12px;
    }
    QComboBox:hover, QLineEdit:hover, QSpinBox:hover {
        border: 1px solid #0096C7;
        background-color: #333333;
    }
    QComboBox::drop-down {
        border: none;
        padding-right: 15px;
    }
    QComboBox::down-arrow {
        image: url(resources/icons/dropdown.png);
        width: 12px;
        height: 12px;
    }
    QPushButton {
        background-color: #323232;
        border: 1px solid #404040;
        border-radius: 3px;
        color: #e0e0e0;
        padding: 4px 8px;
        min-height: 22px;
        font-weight: bold;
        font-size: 12px;
    }
    QPushButton:hover {
        background-color: #383838;
        border: 1px solid #4a4a4a;
    }
    QPushButton#save_button {
        background-color: #264F78;
        border: none;
    }
    QPushButton#save_button:hover {
        background-color: #2D5F91;
    }
    QCheckBox {
        color: #e0e0e0;
        spacing: 4px;
        min-height: 16px;
        font-size: 12px;
    }
    QCheckBox::indicator {
        width: 14px;
        height: 14px;
        border-radius: 2px;
        border: 1px solid #404040;
        background-color: #2d2d2d;
    }
    QCheckBox::indicator:checked {
        background-color: #264F78;
        border: 1px solid #264F78;
        image: url(resources/icons/check.png);
        padding: 0px;
        margin: 0px;
    }
    QCheckBox::indicator:hover {
        border: 1px solid #0096C7;
    }
    QLabel {
        color: #e0e0e0;
        font-size: 12px;
    }
    QSpinBox::up-button, QSpinBox::down-button {
        border-radius: 2px;
        background-color: #323232;
        min-width: 18px;
    }
    QSpinBox::up-button:hover, QSpinBox::down-button:hover {
        background-color: #0096C7;
    }
"""