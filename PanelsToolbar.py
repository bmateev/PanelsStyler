from PySide import QtCore, QtGui
import FreeCADGui as Gui
import FreeCAD

class PanelsToolbar(QtGui.QToolBar):
    def __init__(self, parent=None):
        super(PanelsToolbar, self).__init__("Panels", parent)
        self.setObjectName("PanelsToolbar")
        self.setMovable(True)

        self.param = FreeCAD.ParamGet("User parameter:BaseApp/FontStyler")
        self.mw = Gui.getMainWindow()

        self.setup_ui()
        self.load_last_settings()

    def setup_ui(self):
        # Add label "Panels:" before the combo box
        label = QtGui.QLabel("Panel: ")
        self.addWidget(label)
    
        # Panel dropdown - using windowTitle()
        self.panel_combo = QtGui.QComboBox()
        dock_widgets = self.mw.findChildren(QtGui.QDockWidget)
        print(f"🔍 Found {len(dock_widgets)} dock widgets")

        panel_names = []
        for dock in dock_widgets:
            title = dock.windowTitle()
            print(f"Title: '{title}'")
            if title:
                panel_names.append(title)
                print(f"Adding panel to combo: '{title}'")  # Debug print

        panel_names = sorted(panel_names)
        self.panel_combo.addItems(panel_names)
        self.addWidget(self.panel_combo)

        # Connect signals
        self.panel_combo.currentIndexChanged.connect(self.load_panel_settings)
        self.panel_combo.currentIndexChanged.connect(self.on_panel_selected)

        # Font selector
        self.font_combo = QtGui.QFontComboBox()
        self.addWidget(self.font_combo)

        # Font size selector
        self.size_combo = QtGui.QComboBox()
        self.size_combo.addItems([str(i) for i in range(6, 25)])
        self.addWidget(self.size_combo)

        # Apply button
        self.apply_btn = QtGui.QPushButton("Apply")
        self.addWidget(self.apply_btn)
        self.apply_btn.clicked.connect(self.apply_font)

        # Reset button
        self.reset_btn = QtGui.QPushButton("Reset")
        self.addWidget(self.reset_btn)
        self.reset_btn.clicked.connect(self.reset2Defaults)

    def reset2Defaults(self):
        reply = QtGui.QMessageBox.question(
            self,
            "Reset Fonts",
            "Do you also want to delete all saved font settings?",
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
        )

        mw = Gui.getMainWindow()
        dock_widgets = mw.findChildren(QtGui.QDockWidget)

        for dock in dock_widgets:
            dock.setStyleSheet("")  # Remove applied styles
            panel_name = dock.objectName()

            FreeCAD.Console.PrintMessage(
                f"🔁 Reset font for panel: {panel_name} ({dock.windowTitle()})\n"
            )

            if reply == QtGui.QMessageBox.Yes and panel_name:
                self.param.RemString(f"{panel_name}/fontFamily")
                self.param.RemInt(f"{panel_name}/fontSize")

                FreeCAD.Console.PrintMessage(
                    f"🗑 Removed saved settings for '{panel_name}'\n"
                )

    def load_last_settings(self):
        last_panel = self.param.GetString("lastPanel", "")
        if last_panel:
            idx = self.panel_combo.findText(last_panel)
            if idx >= 0:
                self.panel_combo.setCurrentIndex(idx)

        # Load settings for initial panel
        if self.panel_combo.count() > 0:
            self.load_panel_settings(self.panel_combo.currentIndex())

    def load_panel_settings(self, index):
        panel_name = self.panel_combo.itemText(index)
        if not panel_name:
            return

        self.param.SetString("lastPanel", panel_name)

        font_family = self.param.GetString(f"{panel_name}/fontFamily", "")
        font_size = self.param.GetInt(f"{panel_name}/fontSize", 10)

        if font_family:
            idx_font = self.font_combo.findText(font_family, QtCore.Qt.MatchFixedString)
            if idx_font >= 0:
                self.font_combo.setCurrentIndex(idx_font)
            else:
                self.font_combo.setCurrentIndex(0)
        else:
            self.font_combo.setCurrentIndex(0)

        idx_size = self.size_combo.findText(str(font_size), QtCore.Qt.MatchFixedString)
        if idx_size >= 0:
            self.size_combo.setCurrentIndex(idx_size)
        else:
            self.size_combo.setCurrentIndex(4)  # Default 10pt

    def apply_font(self):
        panel_title = self.panel_combo.currentText()
        font_family = self.font_combo.currentFont().family()
        font_size = int(self.size_combo.currentText())

        print(f"Trying to find panel: '{panel_title}'")  # Debug

        dock_widgets = self.mw.findChildren(QtGui.QDockWidget)
        panel = None
        for dock in dock_widgets:
            print(f"Checking dock with windowTitle: '{dock.windowTitle()}'")  # Debug
            if dock.windowTitle() == panel_title:
                panel = dock
                print(f"Found panel '{panel_title}'!")  # Debug
                break

        if panel:
            css = f"""
                * {{
                    font-family: '{font_family}';
                    font-size: {font_size}pt;
                }}
            """
            panel.setStyleSheet(css)

            self.param.SetString(f"{panel_title}/fontFamily", font_family)
            self.param.SetInt(f"{panel_title}/fontSize", font_size)

            FreeCAD.Console.PrintMessage(f"✅ Applied '{font_family}', {font_size}pt to '{panel_title}'\n")
        else:
            FreeCAD.Console.PrintError(f"❌ Panel '{panel_title}' not found\n")

    def on_panel_selected(self, index):
        panel_title = self.panel_combo.itemText(index)

        print(f"Trying to show panel: '{panel_title}'")  # Debug

        dock_widgets = self.mw.findChildren(QtGui.QDockWidget)
        panel = None
        for dock in dock_widgets:
            print(f"Checking dock with windowTitle: '{dock.windowTitle()}'")  # Debug
            if dock.windowTitle() == panel_title:
                panel = dock
                print(f"Found panel '{panel_title}'!")  # Debug
                break

        if panel:
            panel.show()
            panel.raise_()
        else:
            FreeCAD.Console.PrintError(f"❌ Panel '{panel_title}' not found\n")
