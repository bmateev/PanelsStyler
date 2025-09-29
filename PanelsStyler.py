from PySide import QtGui, QtCore
import FreeCADGui as Gui
import FreeCAD

def show_font_styler():
    class PanelsStylerDialog(QtGui.QDialog):
        def __init__(self):
            super(PanelsStylerDialog, self).__init__()
            self.setWindowTitle("Font Styler")

            layout = QtGui.QVBoxLayout()

            self.param = FreeCAD.ParamGet("User parameter:BaseApp/PanelsStyler")

            # Panel selector
            self.panel_combo = QtGui.QComboBox()
            self.update_panel_list()
            layout.addWidget(QtGui.QLabel("Panel:"))
            layout.addWidget(self.panel_combo)

            # Font selector
            self.font_combo = QtGui.QFontComboBox()
            layout.addWidget(QtGui.QLabel("Font:"))
            layout.addWidget(self.font_combo)

            # Font size selector
            self.size_combo = QtGui.QComboBox()
            self.size_combo.addItems([str(i) for i in range(6, 25)])
            layout.addWidget(QtGui.QLabel("Font Size:"))
            layout.addWidget(self.size_combo)

            # Apply button
            apply_btn = QtGui.QPushButton("Apply Font")
            apply_btn.clicked.connect(self.apply_font)
            layout.addWidget(apply_btn)

            self.setLayout(layout)

            # Connect panel change signal to update font & size combos
            self.panel_combo.currentIndexChanged.connect(self.load_panel_settings)

            # Load last selected panel or first panel and apply saved font/size
            last_panel = self.param.GetString("lastPanel", "")
            idx = self.panel_combo.findText(last_panel)
            if idx >= 0:
                self.panel_combo.setCurrentIndex(idx)
            else:
                self.panel_combo.setCurrentIndex(0)
            # Load font and size for the selected panel
            self.load_panel_settings()

        def update_panel_list(self):
            mw = Gui.getMainWindow()
            dock_widgets = mw.findChildren(QtGui.QDockWidget)
            for dock in sorted(dock_widgets, key=lambda x: x.objectName()):
                name = dock.objectName()
                if name:
                    self.panel_combo.addItem(name)

        def load_panel_settings(self):
            panel_name = self.panel_combo.currentText()
            if not panel_name:
                return

            # Save last selected panel so next dialog open can restore it
            self.param.SetString("lastPanel", panel_name)

            font_family = self.param.GetString(f"{panel_name}/fontFamily", "")
            font_size = self.param.GetInt(f"{panel_name}/fontSize", 10)

            if font_family:
                idx_font = self.font_combo.findText(font_family, QtCore.Qt.MatchFixedString)
                if idx_font >= 0:
                    self.font_combo.setCurrentIndex(idx_font)
            else:
                self.font_combo.setCurrentIndex(0)  # default to first font

            idx_size = self.size_combo.findText(str(font_size), QtCore.Qt.MatchFixedString)
            if idx_size >= 0:
                self.size_combo.setCurrentIndex(idx_size)
            else:
                self.size_combo.setCurrentIndex(4)  # default to 10pt (index)

        def apply_font(self):
            font_family = self.font_combo.currentFont().family()
            font_size = int(self.size_combo.currentText())
            panel_name = self.panel_combo.currentText()

            mw = Gui.getMainWindow()
            panel = mw.findChild(QtGui.QDockWidget, panel_name)

            if panel:
                css = f"""
                * {{
                    font-family: '{font_family}';
                    font-size: {font_size}pt;
                }}
                """
                panel.setStyleSheet(css)

                # Save settings for this panel
                self.param.SetString(f"{panel_name}/fontFamily", font_family)
                self.param.SetInt(f"{panel_name}/fontSize", font_size)

                FreeCAD.Console.PrintMessage(
                    f"✅ Applied {font_family}, {font_size}pt to '{panel_name}' and saved settings.\n"
                )
            else:
                FreeCAD.Console.PrintError(f"❌ Panel '{panel_name}' not found\n")

    dialog = PanelsStylerDialog()
    dialog.exec_()
