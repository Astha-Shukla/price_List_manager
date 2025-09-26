import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea,
    QSizePolicy, QTableWidgetItem, 
    QToolButton, QHeaderView, QTableWidget,
    QMessageBox
)
from PyQt5.QtGui import QIcon, QPainter
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog

class TypeWidget(QWidget):
    modification_started = pyqtSignal()

    def __init__(self, sizes, parent=None):
        super().__init__(parent)
        self.sizes = list(sizes) 
        self.base_col_width = 60 
        self._type_name = "" 

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)

        top_row = QHBoxLayout()
        top_row.setSpacing(6)
        
        center_group = QHBoxLayout()
        center_group.setSpacing(6)

        self.toggle_btn = QToolButton()
        self.toggle_btn.setArrowType(Qt.RightArrow)
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(False)
        self.toggle_btn.clicked.connect(self.toggle_table)

        self.number_label = QLabel("")
        self.number_label.setFixedWidth(20) 
        self.number_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.type_edit = QLineEdit()
        self.type_edit.setPlaceholderText("Type Name")
        self.type_edit.textChanged.connect(self._update_name_and_emit) 

        self.delete_btn = QToolButton()
        self.delete_btn.setIcon(QIcon("media/delete.png"))
        self.delete_btn.clicked.connect(self.delete_self)

        center_group.addWidget(self.toggle_btn) 
        center_group.addWidget(self.number_label) 
        center_group.addWidget(self.type_edit)
        center_group.addWidget(self.delete_btn)
        
        top_row.addStretch() 
        top_row.addLayout(center_group)
        top_row.addStretch() 
        
        layout.addLayout(top_row)

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
        self.table.itemChanged.connect(lambda: self.modification_started.emit()) 

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
        
        self.modification_started.emit()

    def _update_name_and_emit(self):
        self._type_name = self.type_edit.text()
        self.modification_started.emit()

    def set_name_text(self, text):
        self.number_label.setText(f"{text}.")

    def get_name(self):
        return self._type_name

    def set_name_text(self, text):
        self.number_label.setText(f"{text}.") 
    
    def delete_self(self):
        cloth_widget = self.parent().parent() 
        pl_manager = None
        if isinstance(cloth_widget, ClothWidget):
            pl_manager = cloth_widget._find_price_list_manager()
        self.setParent(None)
        self.deleteLater()
        
        if pl_manager:
            pl_manager.renumber_all()

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
        self.modification_started.emit()
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
        self.modification_started.emit()
        self.sizes.pop()
        last_col = self.table.columnCount() - 1
        if last_col >= 0:
            self.table.removeColumn(last_col)
        self.table.setMinimumWidth(0)
        QTimer.singleShot(0, self.adjust_column_sizes)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        QTimer.singleShot(0, self.adjust_column_sizes)


class ClothWidget(QWidget):
    modification_started = pyqtSignal()

    def __init__(self, sizes, parent=None):
        super().__init__(parent)
        self.sizes = sizes
        self._cloth_name = "" 
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(6, 6, 6, 6)

        top_row = QHBoxLayout()
        top_row.setSpacing(10)
        
        center_group = QHBoxLayout()
        center_group.setSpacing(10)

        self.toggle_btn = QToolButton()
        self.toggle_btn.setArrowType(Qt.RightArrow)
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(False)
        self.toggle_btn.clicked.connect(self.toggle_types)

        self.letter_label = QLabel("A.") 
        self.letter_label.setFixedWidth(20) 
        self.letter_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Cloth name")
        self.name_edit.textChanged.connect(self._update_name_and_emit) 

        self.add_type_btn = QPushButton("✚ Add Type")
        self.add_type_btn.setObjectName("add_type_btn")
        self.add_type_btn.clicked.connect(self.add_type_table)

        self.delete_btn = QToolButton()
        self.delete_btn.setIcon(QIcon("media/delete.png"))
        self.delete_btn.setObjectName("delete_btn")
        self.delete_btn.clicked.connect(self.delete_self)

        center_group.addWidget(self.toggle_btn)
        center_group.addWidget(self.letter_label) 
        center_group.addWidget(self.name_edit)
        center_group.addWidget(self.add_type_btn)
        center_group.addWidget(self.delete_btn)

        top_row.addStretch()
        top_row.addLayout(center_group)
        top_row.addStretch()
        
        self.main_layout.addLayout(top_row)
        
        self.content_widget = QWidget()
        self.type_layout = QVBoxLayout(self.content_widget)
        self.type_layout.setContentsMargins(30, 0, 0, 0)
        self.type_layout.setSpacing(6)

        self.main_layout.addWidget(self.content_widget)

        self.toggle_btn.setChecked(True)
        self.toggle_btn.setArrowType(Qt.DownArrow)
        self.content_widget.setVisible(True)

    def _find_price_list_manager(self):
        widget = self
        while widget is not None:
            if isinstance(widget, PriceListManager):
                return widget
            widget = widget.parent()
        return None

    def _update_name_and_emit(self):
        self._cloth_name = self.name_edit.text()
        self.modification_started.emit()

    def set_name_text(self, text):
        self.letter_label.setText(f"{text}.")

    def get_name(self):
        return self._cloth_name 

    def toggle_types(self):
        expanded = self.toggle_btn.isChecked()
        self.toggle_btn.setArrowType(Qt.DownArrow if expanded else Qt.RightArrow)
        self.content_widget.setVisible(expanded)

    def add_type_table(self):
        self.modification_started.emit()
        type_widget = TypeWidget(self.sizes, parent=self)
        self.type_layout.addWidget(type_widget)
        type_widget.modification_started.connect(self.modification_started.emit)
        
        pl_manager = self._find_price_list_manager()
        if pl_manager:
            pl_manager.renumber_all() 

        if not self.toggle_btn.isChecked():
            self.toggle_btn.setChecked(True)
            self.toggle_types()

    def delete_self(self):
        pl_manager = self._find_price_list_manager() 
        self.setParent(None)
        self.deleteLater()
        
        if pl_manager:
            pl_manager.renumber_all() 

class PriceListWidget(QWidget):
    selected = pyqtSignal(QWidget)
    modification_started = pyqtSignal()

    def __init__(self, sizes, parent=None):
        super().__init__(parent)
        self.sizes = sizes
        self._price_list_name = "" 
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(6, 6, 6, 6)
        self.main_layout.setSpacing(10)

        top_row = QHBoxLayout()
        top_row.setSpacing(10)
        
        center_group = QHBoxLayout()
        center_group.setSpacing(10)
        
        self.toggle_btn = QToolButton()
        self.toggle_btn.setArrowType(Qt.RightArrow)
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(False)
        self.toggle_btn.clicked.connect(self.toggle_content)

        self.number_label = QLabel("1.") 
        self.number_label.setFixedWidth(20)
        self.number_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Price List name")
        self.name_edit.setObjectName("price_list_name_edit")
        self.name_edit.setCursor(Qt.PointingHandCursor)
        self.name_edit.setReadOnly(False) 
        self.name_edit.textChanged.connect(self._update_name_and_emit)
        self.name_edit.mousePressEvent = self.on_select
        
        self.add_cloth_btn = QPushButton("✚ Add Cloth")
        self.add_cloth_btn.setObjectName("add_cloth_btn")
        self.add_cloth_btn.clicked.connect(self.add_cloth_widget)
        self.add_cloth_btn.setFixedSize(120, 30)
        
        center_group.addWidget(self.toggle_btn)
        center_group.addWidget(self.number_label) 
        center_group.addWidget(self.name_edit)
        center_group.addWidget(self.add_cloth_btn)
        
        top_row.addStretch()
        top_row.addLayout(center_group)
        top_row.addStretch()
        
        self.main_layout.addLayout(top_row)
        
        self.content_widget = QWidget()
        self.cloth_layout = QVBoxLayout(self.content_widget)
        self.cloth_layout.setContentsMargins(30, 0, 0, 0)
        self.cloth_layout.setSpacing(6)
        
        self.main_layout.addWidget(self.content_widget)
        
        self.toggle_btn.setChecked(True)
        self.toggle_btn.setArrowType(Qt.DownArrow)
        self.content_widget.setVisible(True)

    def _find_price_list_manager(self):
        widget = self
        while widget is not None:
            if isinstance(widget, PriceListManager):
                return widget
            widget = widget.parent()
        return None

    def _update_name_and_emit(self):
        self._price_list_name = self.name_edit.text()
        self.modification_started.emit()

    def set_name_text(self, text):
        self.number_label.setText(f"{text}.")

    def get_name(self):
        return self._price_list_name 
        
    def on_select(self, event):
        self.selected.emit(self)
        QLineEdit.mousePressEvent(self.name_edit, event)

    def set_selected(self, state):
        if state:
            self.name_edit.setStyleSheet("border: 2px solid #5d81d2;")
        else:
            self.name_edit.setStyleSheet("")

    def toggle_content(self):
        expanded = self.toggle_btn.isChecked()
        self.toggle_btn.setArrowType(Qt.DownArrow if expanded else Qt.RightArrow)
        self.content_widget.setVisible(expanded)
        
    def add_cloth_widget(self):
        self.modification_started.emit()
        cloth_widget = ClothWidget(self.sizes, parent=self)
        self.cloth_layout.addWidget(cloth_widget)
        cloth_widget.modification_started.connect(self.modification_started.emit) 
        
        pl_manager = self._find_price_list_manager()
        if pl_manager:
            pl_manager.renumber_all() 
            
        if not self.toggle_btn.isChecked():
            self.toggle_btn.setChecked(True)
            self.toggle_content()

    def delete_self(self):
        reply = QMessageBox.question(self, 'Delete Price List', 
                                     f"Are you sure you want to delete '{self.name_edit.text()}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            pl_manager = self._find_price_list_manager()
            self.setParent(None)
            self.deleteLater()

            if pl_manager:
                pl_manager.renumber_all()

class PriceListManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ERP — Price List Manager")
        self.setMinimumSize(1000, 600)
        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        self.main_layout.addWidget(self.main_toolbar())
        self.buttons['new_btn'].clicked.connect(self.add_new_price_list)
        self.buttons['print_btn'].clicked.connect(self.show_print_preview)
        self.buttons['delete_btn'].clicked.connect(self.delete_selected_price_list)
        self.buttons['exit_btn'].clicked.connect(self.close)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.price_list_container = QWidget()
        self.price_list_layout = QVBoxLayout(self.price_list_container)
        self.price_list_layout.setContentsMargins(0, 0, 0, 0)
        self.price_list_layout.addStretch()
        self.scroll_area.setWidget(self.price_list_container)
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

        self.sizes = [20, 22, 24, 26, 28, 30]

        self.current_price_list = None
        self.save_btn.clicked.connect(self.exit_edit_mode)
        self.undo_btn.clicked.connect(self.exit_edit_mode)
        self.set_toolbar_state(True)
        
        self.renumber_all() 

    def to_roman(self, num):
        if not (0 < num < 4000):
            return str(num) 
        
        mapping = {
            1000: 'm', 900: 'cm', 500: 'd', 400: 'cd', 100: 'c', 90: 'xc', 
            50: 'l', 40: 'xl', 10: 'x', 9: 'ix', 5: 'v', 4: 'iv', 1: 'i'
        }
        roman_numeral = ""
        for value, symbol in mapping.items():
            while num >= value:
                roman_numeral += symbol
                num -= value
        return roman_numeral

    def renumber_all(self):
        price_list_counter = 0

        for i in range(self.price_list_layout.count() - 1):
            layout_item = self.price_list_layout.itemAt(i)
            if layout_item:
                pl_widget = layout_item.widget()
                if isinstance(pl_widget, PriceListWidget):
                    price_list_counter += 1
                    pl_widget.set_name_text(str(price_list_counter)) 
                    
                    cloth_counter = 0
                    for j in range(pl_widget.cloth_layout.count()):
                        cloth_item = pl_widget.cloth_layout.itemAt(j)
                        if cloth_item:
                            cloth_widget = cloth_item.widget()
                            if isinstance(cloth_widget, ClothWidget):
                                cloth_counter += 1
                                cloth_numeral = chr(ord('A') + cloth_counter - 1)
                                cloth_widget.set_name_text(cloth_numeral) 
                                
                                type_counter = 0
                                for k in range(cloth_widget.type_layout.count()):
                                    type_item = cloth_widget.type_layout.itemAt(k)
                                    if type_item:
                                        type_widget = type_item.widget()
                                        if isinstance(type_widget, TypeWidget):
                                            type_counter += 1

                                            type_numeral = self.to_roman(type_counter)
                                            type_widget.set_name_text(str(type_numeral)) # Correctly calls the method to set label text
                                            
    def add_new_price_list(self):
        price_list_widget = PriceListWidget(self.sizes, parent=self)
        self.price_list_layout.insertWidget(self.price_list_layout.count() - 1, price_list_widget)
        price_list_widget.selected.connect(self.select_price_list)
        price_list_widget.modification_started.connect(self.enter_edit_mode)
        self.select_price_list(price_list_widget)
        self.enter_edit_mode()
        self.renumber_all()

    def delete_selected_price_list(self):
        if self.current_price_list:
            reply = QMessageBox.question(self, 'Delete Price List', 
                                         f"Are you sure you want to delete '{self.current_price_list.name_edit.text()}'?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                list_to_delete = self.current_price_list
                
                list_to_delete.setParent(None)
                list_to_delete.deleteLater()
                self.current_price_list = None
                self.exit_edit_mode()
                self.renumber_all()  

    def show_print_preview(self):
        printer = QPrinter()
        preview_dialog = QPrintPreviewDialog(printer, self)
        preview_dialog.resize(1200, 800) 
        preview_dialog.paintRequested.connect(self.paint_price_lists)
        preview_dialog.exec_()
        
    def paint_price_lists(self, printer):
        painter = QPainter(printer)
        
        page_rect = printer.pageRect(QPrinter.Millimeter) 
        
        printable_width_mm = page_rect.width()
        
        y_offset = 10 
        spacing_mm = 5 

        price_list_widgets = []
        for i in range(self.price_list_layout.count() - 1):
            widget = self.price_list_layout.itemAt(i).widget()
            if isinstance(widget, PriceListWidget):
                price_list_widgets.append(widget)

        max_widget_pixel_width = 0
        for widget in price_list_widgets:
            max_widget_pixel_width = max(max_widget_pixel_width, widget.width())
        
        scale_factor = printer.width() / max_widget_pixel_width if max_widget_pixel_width > 0 else 1.0
        
        if scale_factor > 1.0:
            scale_factor = 1.0
        
        for widget in price_list_widgets:
            widget_pixel_height = widget.sizeHint().height() 
            scaled_widget_height = widget_pixel_height * scale_factor
            
            if y_offset + scaled_widget_height > printer.height(): 
                printer.newPage()
                y_offset = 10  
                
            painter.save()           
            painter.translate(0, y_offset)            
            painter.scale(scale_factor, scale_factor)            
            widget.render(painter)             
            painter.restore()
            y_offset += scaled_widget_height + (spacing_mm * scale_factor)

    def select_price_list(self, price_list_widget):
        if self.current_price_list:
            self.current_price_list.set_selected(False)
            self.current_price_list.add_cloth_btn.hide()
        
        self.current_price_list = price_list_widget
        self.current_price_list.set_selected(True)
        self.current_price_list.add_cloth_btn.show()

        self.current_price_list.modification_started.connect(self.enter_edit_mode)
        for i in range(self.current_price_list.cloth_layout.count()):
            cloth_widget = self.current_price_list.cloth_layout.itemAt(i).widget()
            if cloth_widget:
                cloth_widget.modification_started.connect(self.enter_edit_mode)
                for j in range(cloth_widget.type_layout.count()):
                    type_widget = cloth_widget.type_layout.itemAt(j).widget()
                    if type_widget:
                        type_widget.modification_started.connect(self.enter_edit_mode)

    def set_toolbar_state(self, enabled):
        for name, btn in self.buttons.items():
            btn.setEnabled(enabled)
            
    def enter_edit_mode(self):
        self.set_toolbar_state(False)
        self.undo_btn.setEnabled(True)
        self.save_btn.setEnabled(True)

    def exit_edit_mode(self):
        self.set_toolbar_state(True)

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
            ("📄\nNew", "Ctrl+N", left_layout, "new_btn"),
            ("📝\nModify", "Ctrl+O", left_layout, "modify_btn"),
            ("🗑\nDelete", "Ctrl+D", left_layout, "delete_btn"),
            ("🔍\nSearch", "Ctrl+F", left_layout, "search_btn"),
            ("🖨\nPrint", "Ctrl+P", left_layout, "print_btn"),
            ("▲\nTop", None, mid_layout, "top_btn"),
            ("◀\nBack", "Alt+Left", mid_layout, "back_btn"),
            ("▶\nNext", "Alt+Right", mid_layout, "next_btn"),
            ("▼\nLast", None, mid_layout, "last_btn"),
            ("↩\nExit", "Alt+F4", right_layout, "exit_btn"),
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