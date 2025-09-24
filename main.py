import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea,
    QGridLayout, QSizePolicy, QTableWidgetItem,
    QToolButton, QHeaderView, QTableWidget
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QTimer

class TypeWidget(QWidget):

    def __init__(self, sizes, parent=None):
        super().__init__(parent)
        self.sizes = list(sizes) 
        self.base_col_width = 60  

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)

        # Top row: Type name + controls
        top_row = QHBoxLayout()
        top_row.setSpacing(6)

        self.toggle_btn = QToolButton()
        self.toggle_btn.setArrowType(Qt.RightArrow)
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(False)
        self.toggle_btn.clicked.connect(self.toggle_table)

        self.type_edit = QLineEdit()
        self.type_edit.setPlaceholderText("Type Name")

        self.delete_btn = QToolButton()
        self.delete_btn.setIcon(QIcon("media/delete.png"))
        self.delete_btn.clicked.connect(self.delete_self)

        top_row.addWidget(self.toggle_btn) 
        top_row.addWidget(self.type_edit)
        top_row.addStretch()
        top_row.addWidget(self.delete_btn)
        layout.addLayout(top_row)

        # --- Collapsible area (table)
        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(20, 0, 0, 0)
        table_and_buttons_layout = QHBoxLayout()
        table_and_buttons_layout.setSpacing(6)

        self.table = QTableWidget(2, len(self.sizes))
        self.table.setVerticalHeaderLabels(["Size", "Rate"])
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(30)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.table.setFixedHeight(self.table.verticalHeader().length() + self.table.horizontalHeader().height() + self.table.frameWidth() * 2)

        for col, size in enumerate(self.sizes):
            size_item = QTableWidgetItem(str(size))
            size_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(0, col, size_item)

            rate_item = QTableWidgetItem("0.0")
            rate_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(1, col, rate_item)
        
        btn_col = QVBoxLayout()
        btn_col.setSpacing(0)
        self.add_size_btn = QPushButton("+")
        self.add_size_btn.setObjectName("add_remove_btn")
        self.remove_size_btn = QPushButton("-")
        self.remove_size_btn.setObjectName("add_remove_btn")
        btn_col.addWidget(self.add_size_btn)
        btn_col.addWidget(self.remove_size_btn)
        btn_col.addStretch()

        table_and_buttons_layout.addWidget(self.table)
        table_and_buttons_layout.addLayout(btn_col)
        content_layout.addLayout(table_and_buttons_layout)
        
        layout.addWidget(self.content_widget)
        layout.addStretch()

        self.toggle_btn.setChecked(True)
        self.toggle_btn.setArrowType(Qt.DownArrow)
        self.content_widget.setVisible(True)

        self.add_size_btn.clicked.connect(self.add_size)
        self.remove_size_btn.clicked.connect(self.remove_size)
        QTimer.singleShot(0, self.adjust_column_sizes)

    def toggle_table(self):
        expanded = self.toggle_btn.isChecked()
        self.toggle_btn.setArrowType(Qt.DownArrow if expanded else Qt.RightArrow)
        self.content_widget.setVisible(expanded)

    def adjust_column_sizes(self):
        header = self.table.horizontalHeader()
        ncols = self.table.columnCount()
        total_req = ncols * self.base_col_width

        viewport_w = self.table.viewport().width()

        if total_req <= viewport_w:
            header.setSectionResizeMode(QHeaderView.Stretch)
        else:
            header.setSectionResizeMode(QHeaderView.Fixed)
        for col in range(ncols):
            self.table.setColumnWidth(col, self.base_col_width)
        self.table.setMinimumWidth(total_req)

    def add_size(self):
        new_size = (max(self.sizes) + 2) if self.sizes else 20
        self.sizes.append(new_size)
        col = self.table.columnCount()
        self.table.insertColumn(col)
        size_item = QTableWidgetItem(str(new_size))
        size_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(0, col, size_item)
        rate_item = QTableWidgetItem("0.0")
        rate_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(1, col, rate_item)
        QTimer.singleShot(0, self.adjust_column_sizes)

    def remove_size(self):
        if not self.sizes:
            return
        self.sizes.pop()
        last_col = self.table.columnCount() - 1
        if last_col >= 0:
            self.table.removeColumn(last_col)
        self.table.setMinimumWidth(0)
        QTimer.singleShot(0, self.adjust_column_sizes)

    def delete_self(self):
        self.setParent(None)
        self.deleteLater()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        QTimer.singleShot(0, self.adjust_column_sizes)


class ClothWidget(QWidget):
    def __init__(self, sizes, parent=None, toolbar_callback=None):
        super().__init__(parent)
        self.sizes = sizes
        self.toolbar_callback = toolbar_callback # Store the callback

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(6, 6, 6, 6)

        # Top row (cloth name + add type + delete)
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)

        self.toggle_btn = QToolButton()
        self.toggle_btn.setArrowType(Qt.RightArrow)
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(False)
        self.toggle_btn.clicked.connect(self.toggle_types)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Cloth name")
        #self.name_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.name_edit.setFixedWidth(360) 

        self.add_type_btn = QPushButton("✚ Add Type")
        self.add_type_btn.setObjectName("add_type_btn")
        self.add_type_btn.clicked.connect(self.add_type_table)

        self.delete_btn = QToolButton()
        self.delete_btn.setIcon(QIcon("media/delete.png"))
        self.delete_btn.setObjectName("delete_btn")
        self.delete_btn.clicked.connect(self.delete_self)

        top_layout.addWidget(self.toggle_btn)
        top_layout.addWidget(self.name_edit)
        top_layout.addWidget(self.add_type_btn)
        top_layout.addStretch()
        top_layout.addWidget(self.delete_btn)
        self.main_layout.addLayout(top_layout)
        
        # --- Collapsible container for types
        self.content_widget = QWidget()
        self.type_layout = QVBoxLayout(self.content_widget)
        self.type_layout.setContentsMargins(30, 0, 0, 0)
        self.type_layout.setSpacing(6)

        self.main_layout.addWidget(self.content_widget)

        self.toggle_btn.setChecked(True)
        self.toggle_btn.setArrowType(Qt.DownArrow)
        self.content_widget.setVisible(True)

    def toggle_types(self):
        expanded = self.toggle_btn.isChecked()
        self.toggle_btn.setArrowType(Qt.DownArrow if expanded else Qt.RightArrow)
        self.content_widget.setVisible(expanded)

    def add_type_table(self):
        print("Add Type button clicked.")
        type_widget = TypeWidget(self.sizes, parent=self)
        self.type_layout.addWidget(type_widget)
        if not self.toggle_btn.isChecked():
            self.toggle_btn.setChecked(True)
            self.toggle_types()
        if self.toolbar_callback:
            print("Disabling toolbar via callback...")
            self.toolbar_callback(False)
            # You'll also need to re-enable undo/save from here
            # This can get messy, so using signals is a better approach

    def delete_self(self):
        self.setParent(None)
        self.deleteLater()

class PriceListManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ERP — Price List Manager")
        self.setMinimumSize(1000, 600)
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.main_toolbar())

        # Connect the exit button's clicked signal to the window's close method
        self.buttons['exit_btn'].clicked.connect(self.close)

        name_row = QHBoxLayout()
        self.price_list_label = QLabel("Price List Name:")
        self.price_list_input = QLineEdit()
        self.price_list_input.setPlaceholderText("e.g. Summer 2026")
        self.price_list_input.setFixedWidth(800)         

        self.add_cloth_btn = QPushButton("✚ Add Cloth")
        self.add_cloth_btn.setObjectName("add_cloth_btn")
        self.add_cloth_btn.clicked.connect(self.add_cloth)
        name_row.addWidget(self.price_list_label)
        name_row.addWidget(self.price_list_input)
        name_row.addWidget(self.add_cloth_btn)
        name_row.addStretch(1)
        self.main_layout.addLayout(name_row)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scroll_area")
        self.cloth_container = QWidget()
        self.cloth_layout = QVBoxLayout(self.cloth_container)
        self.cloth_layout.addStretch()
        self.scroll_area.setWidget(self.cloth_container)
        self.main_layout.addWidget(self.scroll_area)

        btn_layout = QHBoxLayout()
        self.undo_btn = QPushButton("↶\nUndo")
        self.undo_btn.setObjectName("undo_btn")
        self.save_btn = QPushButton("💾\nSave")
        self.save_btn.setObjectName("save_btn")
        for btn in (self.undo_btn, self.save_btn):
            btn.setFixedSize(120, 60)
            
        btn_layout.addWidget(self.undo_btn)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addStretch()
        self.main_layout.addLayout(btn_layout)
        self.setLayout(self.main_layout)

        self.sizes = [20, 22, 24, 26, 28, 30]
        self.save_btn.clicked.connect(self.save_and_re_enable)

    def save_and_re_enable(self):
        print("Save button clicked.")
        self.set_toolbar_enabled(True)
        print("Toolbar re-enabled.")

    def add_cloth(self):
        print("Add Cloth button clicked.")
        cloth = ClothWidget(self.sizes, parent=self, toolbar_callback=self.set_toolbar_enabled)
        self.cloth_layout.insertWidget(self.cloth_layout.count() - 1, cloth)
        self.set_toolbar_enabled(False) 
        print("Toolbar disabled.")
        self.undo_btn.setEnabled(True)
        self.save_btn.setEnabled(True)

    def create_btn(self, text, shortcut=None):
        btn = QPushButton(text)
        if shortcut:
            btn.setShortcut(shortcut)
        return btn

    def main_toolbar(self):
        button_group = QWidget()
        button_group.setObjectName("toolbar_widget")
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(0)
        left_layout, mid_layout, right_layout = QHBoxLayout(), QHBoxLayout(), QHBoxLayout()
        for layout in (left_layout, mid_layout, right_layout):
            layout.setSpacing(1)
            layout.setContentsMargins(0, 0, 0, 0)

        buttons_config = [
            ("📄\nNew-Ctrl+N", "Ctrl+N", left_layout, "new_btn"),
            ("📝\nModify-Ctrl+O", "Ctrl+O", left_layout, "modify_btn"),
            ("🗑\nDelete-Ctrl+D", "Ctrl+D", left_layout, "delete_btn"),
            ("🔍\nSearch-Ctrl+F", "Ctrl+F", left_layout, "search_btn"),
            ("🖨\nPrint-Ctrl+P", "Ctrl+P", left_layout, "print_btn"),
            ("▲\nTop", None, mid_layout, "top_btn"),
            ("◀\nBack", "Alt+Left", mid_layout, "back_btn"),
            ("▶\nNext", "Alt+Right", mid_layout, "next_btn"),
            ("▼\nLast", None, mid_layout, "last_btn"),
            ("↩\nExit-Alt+F4", "Alt+F4", right_layout, "exit_btn"),
            ("❔\nTUTOR", None, right_layout, "tutor_btn"),
        ]

        self.buttons = {}
        for text, shortcut, layout, obj_name in buttons_config:
            btn = self.create_btn(text, shortcut)
            btn.setObjectName(obj_name)
            btn.setFixedSize(120, 60)
            layout.addWidget(btn)
            self.buttons[obj_name] = btn

        button_layout.addLayout(left_layout)
        button_layout.addStretch(1)
        button_layout.addLayout(mid_layout)
        button_layout.addStretch(1)
        button_layout.addLayout(right_layout)
        button_group.setLayout(button_layout)
        return button_group
    
    def set_toolbar_enabled(self, state):
        for button in self.buttons.values():
            button.setEnabled(state)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        with open("style.css", "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("style.css not found. Using default styles.")
    window = PriceListManager()
    window.show()
    sys.exit(app.exec_())