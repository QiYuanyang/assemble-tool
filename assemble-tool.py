from OCC.Display.backend import load_backend
load_backend("qt-pyqt5")

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, QFileDialog, QVBoxLayout, QWidget, QListWidget, QHBoxLayout
)
from OCC.Display.qtDisplay import qtViewer3d
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.StlAPI import StlAPI_Reader
from OCC.Core.BRep import BRep_Builder
from OCC.Core.TopoDS import TopoDS_Shape

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple CAD Assembler")
        self.resize(1200, 800)

        # Central widget and main layout
        self.widget = QWidget()
        self.setCentralWidget(self.widget)
        self.main_layout = QHBoxLayout(self.widget)

        # List of loaded components
        self.list_widget = QListWidget()
        self.list_widget.setContextMenuPolicy(3)  # Qt.CustomContextMenu
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)
        self.main_layout.addWidget(self.list_widget, 1)  # 1 = stretch factor

        # 3D Viewer
        self.display = qtViewer3d(self)
        self.main_layout.addWidget(self.display, 4)  # 4 = stretch factor

        # Store loaded shapes and their names
        self.shapes = []
        self.shape_names = []

        # Menu
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        import_action = QAction("Import CAD...", self)
        import_action.triggered.connect(self.import_cad)
        file_menu.addAction(import_action)

        self.statusBar().showMessage("Ready")

    def import_cad(self):
        self.statusBar().showMessage("Loading CAD file...")
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open CAD File", "", "CAD Files (*.step *.stp *.stl)"
        )
        if not file_path:
            self.statusBar().showMessage("Ready")
            return

        name = os.path.basename(file_path)
        if file_path.lower().endswith(('.step', '.stp')):
            shape = self.load_step_shape(file_path)
            if shape:
                self.shapes.append(shape)
                self.shape_names.append(name)
                self.list_widget.addItem(name)
                self.redraw_shapes()
                self.statusBar().showMessage(f"Loaded: {name}")
            else:
                self.statusBar().showMessage("Failed to load file.")
        elif file_path.lower().endswith('.stl'):
            shape = TopoDS_Shape()
            builder = BRep_Builder()
            stl_reader = StlAPI_Reader()
            stl_reader.Read(shape, file_path)
            if shape:
                self.shapes.append(shape)
                self.shape_names.append(name)
                self.list_widget.addItem(name)
                self.redraw_shapes()
                self.statusBar().showMessage(f"Loaded: {name}")
            else:
                self.statusBar().showMessage("Failed to load file.")
        else:
            self.statusBar().showMessage("Ready")
            return

    def load_step_shape(self, file_path):
        step_reader = STEPControl_Reader()
        status = step_reader.ReadFile(file_path)
        if status == 1:
            step_reader.TransferRoots()
            return step_reader.Shape()
        return None

    def redraw_shapes(self):
        self.display._display.EraseAll()
        for shp in self.shapes:
            self.display._display.DisplayShape(shp, update=False)
        self.display._display.FitAll()
        self.display._display.Repaint()

    def show_context_menu(self, pos):
        from PyQt5.QtWidgets import QMenu
        item = self.list_widget.itemAt(pos)
        if item is not None:
            menu = QMenu()
            delete_action = menu.addAction("Delete")
            action = menu.exec_(self.list_widget.mapToGlobal(pos))
            if action == delete_action:
                row = self.list_widget.row(item)
                self.list_widget.takeItem(row)
                del self.shapes[row]
                del self.shape_names[row]
                self.redraw_shapes()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())