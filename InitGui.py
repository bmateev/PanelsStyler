import FreeCAD
import FreeCADGui as Gui

from PySide import QtCore, QtGui
import os

print("✅ QtGui is imported:", QtGui)
print("✅ PanelsStyler InitGui loaded successfully")

global apply_fonts_fn
apply_fonts_fn = None  # Placeholder to hold the function reference


USE_PANELS_TOOLBAR = True  # Set False for simple button toolbar

def apply_saved_fonts_on_startup():


    EXPECTED_PANELS = {
        "Tree view",
        "Property view",
        "Selection view",
        "Python console",
        "Report view",
        "Tasks"
    }
    from PySide import QtCore, QtGui
    mw = Gui.getMainWindow()
    param = FreeCAD.ParamGet("User parameter:BaseApp/PanelsStyler")
    dock_widgets = mw.findChildren(QtGui.QDockWidget)

    found_panels = {dock.objectName() for dock in dock_widgets if dock.objectName()}
    missing = EXPECTED_PANELS - found_panels

    if missing:
        FreeCAD.Console.PrintMessage(f"⏳ Waiting for panels to load: {', '.join(missing)}\n")
        QtCore.QTimer.singleShot(1000, lambda: apply_fonts_fn())  # <-- Direct reference here
        return

    FreeCAD.Console.PrintMessage("✅ All panels loaded. Applying saved fonts...\n")

    for dock in dock_widgets:
        panel_name = dock.objectName()
        if not panel_name:
            continue

        font_family = param.GetString(f"{panel_name}/fontFamily", "")
        font_size = param.GetInt(f"{panel_name}/fontSize", 0)

        if font_family and font_size > 0:
            css = f"""
                * {{
                    font-family: '{font_family}';
                    font-size: {font_size}pt;
                }}
            """
            dock.setStyleSheet(css)
            FreeCAD.Console.PrintMessage(
                f"✅ Applied font '{font_family}', {font_size}pt to panel '{panel_name}'\n"
            )

#global apply_fonts_fn
apply_fonts_fn = apply_saved_fonts_on_startup

class PanelsStylerCommand:
    def GetResources(self):
        return {
            'MenuText': "Panels Styler",
            'ToolTip': "Open the font styling dialog",
            'Pixmap': ""  # Optionally: add icon path
        }

    def Activated(self):
        import PanelsStyler
        PanelsStyler.show_font_styler()

    def IsActive(self):
        return True

Gui.addCommand("Open_Font_Styler", PanelsStylerCommand())


# Panels we expect to see (by objectName)
EXPECTED_PANELS = {
    "Tree view",
    "Property view",
    "Selection view",
    "Python console",
    "Report view",
    "Tasks"
}


def add_simple_toolbar_button():
    from PySide import QtCore, QtGui  # Import here to avoid issues

    mw = Gui.getMainWindow()
    tb = mw.findChild(QtGui.QToolBar, "PanelsStylerToolbar")

    if not tb:
        tb = QtGui.QToolBar("Panels Styler")
        tb.setObjectName("PanelsStylerToolbar")
        tb.setMovable(True)  # ✅ Make toolbar movable

        # 🔍 Attempt to place it near the "File" toolbar
        file_tb = mw.findChild(QtGui.QToolBar, "File")
        if file_tb:
            mw.insertToolBar(file_tb, tb)
            FreeCAD.Console.PrintMessage("✅ Inserted PanelsStyler toolbar before 'File'\n")
        else:
            mw.addToolBar(QtCore.Qt.TopToolBarArea, tb)
            FreeCAD.Console.PrintMessage("⚠️ File toolbar not found, added to top\n")

    # ✅ Load custom icon
    icon_path = os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "PanelsStyler", "panel-styler.png")
    icon = QtGui.QIcon(icon_path) if os.path.exists(icon_path) else QtGui.QIcon()

    if icon.isNull():
        FreeCAD.Console.PrintError(f"❌ Icon not found: {icon_path}\n")
    else:
        FreeCAD.Console.PrintMessage(f"✅ Loaded icon from: {icon_path}\n")

    # ✅ Create the action and add to toolbar
    action = QtGui.QAction(icon, "Panels Styler", mw)
    action.setToolTip("Open the Panels Styler dialog")
    action.triggered.connect(lambda: Gui.runCommand("Open_Font_Styler"))
    tb.addAction(action)


def add_panels_toolbar():
    mw = Gui.getMainWindow()
    from PanelsToolbar import PanelsToolbar  # Your modular toolbar class
    from PySide import QtCore, QtGui  # Import here to avoid issues
    
    tb = mw.findChild(QtGui.QToolBar, "PanelsToolbar")
    if tb:
        return  # Already added

    toolbar = PanelsToolbar(mw)
    mw.addToolBar(QtCore.Qt.TopToolBarArea, toolbar)
    FreeCAD.Console.PrintMessage("✅ Added Panels toolbar\n")


# Schedule functions based on the variable
QtCore.QTimer.singleShot(1000, apply_saved_fonts_on_startup)

if USE_PANELS_TOOLBAR:
    QtCore.QTimer.singleShot(4000, add_panels_toolbar)
else:
    QtCore.QTimer.singleShot(2000, add_simple_toolbar_button)
