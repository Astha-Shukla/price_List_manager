import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea,
    QSizePolicy, QTableWidgetItem, 
    QToolButton, QHeaderView, QTableWidget,
    QInputDialog, QMessageBox
)
from PyQt5.QtGui import QIcon, QPainter, QFont
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QRect
from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog, QPrintDialog

class TypeWidget(QWidget):
    modification_started = pyqtSignal()

    def __init__(self, sizes, parent=None):
        super().__init__(parent)
        self.sizes = list(sizes) 
        self.base_col_width = 60 

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)

        top_row = QHBoxLayout()
        top_row.setSpacing(6)

        self.toggle_btn = QToolButton()
        self.toggle_btn.setArrowType(Qt.RightArrow)
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(False)
        self.toggle_btn.clicked.connect(self.toggle_table)

        self.type_edit = QLineEdit()
        self.type_edit.setPlaceholderText("Type Name")
        self.type_edit.textChanged.connect(self.modification_started.emit) # Emit signal on text change

        self.delete_btn = QToolButton()
        self.delete_btn.setIcon(QIcon("media/delete.png"))
        self.delete_btn.clicked.connect(self.delete_self)

        top_row.addWidget(self.toggle_btn) 
        top_row.addWidget(self.type_edit)
        top_row.addStretch()
        top_row.addWidget(self.delete_btn)
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
        self.table.itemChanged.connect(lambda: self.modification_started.emit()) # Emit signal on cell change

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

    def delete_self(self):
        self.setParent(None)
        self.deleteLater()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        QTimer.singleShot(0, self.adjust_column_sizes)

class ClothWidget(QWidget):
    modification_started = pyqtSignal()

    def __init__(self, sizes, parent=None):
        super().__init__(parent)
        self.sizes = sizes
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(6, 6, 6, 6)

        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)

        self.toggle_btn = QToolButton()
        self.toggle_btn.setArrowType(Qt.RightArrow)
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(False)
        self.toggle_btn.clicked.connect(self.toggle_types)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Cloth name")
        self.name_edit.setFixedWidth(360) 
        self.name_edit.textChanged.connect(self.modification_started.emit) # Emit signal on text change

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
        self.modification_started.emit()
        type_widget = TypeWidget(self.sizes, parent=self)
        self.type_layout.addWidget(type_widget)
        type_widget.modification_started.connect(self.modification_started.emit) # Propagate the signal
        if not self.toggle_btn.isChecked():
            self.toggle_btn.setChecked(True)
            self.toggle_types()

    def delete_self(self):
        self.setParent(None)
        self.deleteLater()

class PriceListWidget(QWidget):
    selected = pyqtSignal(QWidget)
    modification_started = pyqtSignal()

    def __init__(self, sizes, parent=None):
        super().__init__(parent)
        self.sizes = sizes
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(6, 6, 6, 6)
        self.main_layout.setSpacing(10)

        top_row = QHBoxLayout()
        top_row.setSpacing(10)
        
        self.toggle_btn = QToolButton()
        self.toggle_btn.setArrowType(Qt.RightArrow)
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(False)
        self.toggle_btn.clicked.connect(self.toggle_content)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Price List name")
        self.name_edit.setFixedWidth(800)
        self.name_edit.setObjectName("price_list_name_edit")
        self.name_edit.setCursor(Qt.PointingHandCursor)
        self.name_edit.setReadOnly(False) 
        self.name_edit.textChanged.connect(self.modification_started.emit) 
        self.name_edit.mousePressEvent = self.on_select
        
        self.add_cloth_btn = QPushButton("✚ Add Cloth")
        self.add_cloth_btn.setObjectName("add_cloth_btn")
        self.add_cloth_btn.clicked.connect(self.add_cloth_widget)
        self.add_cloth_btn.setFixedSize(120, 30)
        
        top_row.addWidget(self.toggle_btn)
        top_row.addWidget(self.name_edit)
        top_row.addWidget(self.add_cloth_btn)
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
        cloth_widget.modification_started.connect(self.modification_started.emit) # Propagate the signal up
        if not self.toggle_btn.isChecked():
            self.toggle_btn.setChecked(True)
            self.toggle_content()

    def delete_self(self):
        reply = QMessageBox.question(self, 'Delete Price List', 
                                     f"Are you sure you want to delete '{self.name_edit.text()}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.setParent(None)
            self.deleteLater()

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

    def show_print_preview(self):
        printer = QPrinter()
        preview_dialog = QPrintPreviewDialog(printer, self)
        preview_dialog.resize(1200, 800) 
        preview_dialog.paintRequested.connect(self.paint_price_lists)
        preview_dialog.exec_()

    def to_roman(self, n):
        """Converts an integer to a Roman numeral string."""
        if not 0 < n < 40: # Limiting for practicality
            return str(n)
        
        roman_map = {1: 'I', 4: 'IV', 5: 'V', 9: 'IX', 10: 'X'}
        values = [10, 9, 5, 4, 1]
        symbols = ['X', 'IX', 'V', 'IV', 'I']
        result = ""
        for i, value in enumerate(values):
            while n >= value:
                result += symbols[i]
                n -= value
        return result
    
    def draw_type_table(self, painter, type_widget, page_width, start_y, mm_to_units, line_height_mm, header_color):
        
        table = type_widget.table
        col_count = table.columnCount()
        row_count = table.rowCount()

        if col_count == 0 or row_count == 0:
            return start_y

        col_width = page_width / (col_count + 1)
        row_height = mm_to_units(line_height_mm)

        current_y = start_y
        
        painter.save()
        table_font = painter.font()
        table_font.setPointSizeF(8)
        table_font.setBold(False) 
        table_font.setWeight(QFont.Normal) 
        painter.setFont(table_font)
        
        painter.setBrush(header_color)
        painter.drawRect(0, int(current_y), int(col_width), int(row_height * 2))
        
        painter.setPen(Qt.black)
        
        painter.drawText(QRect(0, current_y, int(col_width), row_height), 
                         Qt.AlignCenter, "Size")
        painter.drawText(QRect(0, current_y + row_height, int(col_width), row_height), 
                         Qt.AlignCenter, "Rate")
        
        for col in range(col_count):

            x_pos = col_width * (col + 1)
            size_item = table.item(0, col)
            text = size_item.text() if size_item else ""
            
            painter.setBrush(header_color)
            painter.drawRect(int(x_pos), int(current_y), int(col_width), int(row_height))
            
            painter.drawText(QRect(int(x_pos), current_y, int(col_width), row_height), 
                             Qt.AlignCenter, text)
        
        current_y += row_height
        
        for col in range(col_count):
            x_pos = col_width * (col + 1)
            rate_item = table.item(1, col)
            text = rate_item.text() if rate_item else ""
            
            painter.setBrush(Qt.white)
            painter.drawRect(int(x_pos), int(current_y), int(col_width), int(row_height))
            
            painter.drawText(QRect(int(x_pos), current_y, int(col_width), row_height), 
                             Qt.AlignCenter, text)

        current_y += row_height
        
        painter.setBrush(Qt.NoBrush)
        painter.setPen(Qt.black)
        
        painter.drawRect(0, start_y, int(page_width), current_y - start_y)
        
        for col in range(col_count + 1):
            x_pos = col_width * col
            painter.drawLine(int(x_pos), start_y, int(x_pos), current_y)
        
        painter.drawLine(0, start_y + row_height, page_width, start_y + row_height)     
        painter.restore()
        return current_y

    def paint_price_lists(self, printer):
        painter = QPainter(printer)
        
        MARGIN_MM = 10
        LINE_HEIGHT_MM = 7
        TEXT_FONT_SIZE = 10
        TABLE_HEADER_COLOR = Qt.lightGray
        
        def mm_to_units(mm):
            return int(mm * printer.width() / printer.pageRect(QPrinter.Millimeter).width())

        y_offset_units = mm_to_units(MARGIN_MM)
        
        painter.setFont(painter.font()) 
        painter.font().setPointSizeF(TEXT_FONT_SIZE)
        
        price_list_widgets = []
        for i in range(self.price_list_layout.count() - 1):
            widget = self.price_list_layout.itemAt(i).widget()
            if isinstance(widget, PriceListWidget):
                price_list_widgets.append(widget)

        page_width = printer.width()
        
        for pl_idx, pl_widget in enumerate(price_list_widgets):
            pl_name = pl_widget.name_edit.text() or "Untitled Price List"
            pl_label = f"PRICE LIST-({pl_idx + 1}) {pl_name}"
            
            if y_offset_units + mm_to_units(LINE_HEIGHT_MM * 2) > printer.height() - mm_to_units(MARGIN_MM):
                printer.newPage()
                y_offset_units = mm_to_units(MARGIN_MM)

            pl_font = QFont(painter.font()) 
            pl_font.setBold(True)
            pl_font.setWeight(QFont.Black) 
            pl_font.setPointSizeF(TEXT_FONT_SIZE * 1.2) 
            painter.setFont(pl_font)
            
            pl_rect = painter.boundingRect(0, y_offset_units, page_width, mm_to_units(LINE_HEIGHT_MM * 1.5), 
                                          Qt.AlignCenter, pl_label)
            painter.drawText(pl_rect, Qt.AlignCenter, pl_label)
            y_offset_units += pl_rect.height() + mm_to_units(LINE_HEIGHT_MM * 0.5)
            painter.restore()

            cloth_widgets = []
            for i in range(pl_widget.cloth_layout.count()):
                widget = pl_widget.cloth_layout.itemAt(i).widget()
                if isinstance(widget, ClothWidget):
                    cloth_widgets.append(widget)

            for c_idx, c_widget in enumerate(cloth_widgets):
                cloth_name = c_widget.name_edit.text() or "Untitled Cloth"
                cloth_prefix = chr(65 + c_idx) # 'A'
                cloth_label = f"[{cloth_prefix}. {cloth_name}]"

                if y_offset_units + mm_to_units(LINE_HEIGHT_MM * 2) > printer.height() - mm_to_units(MARGIN_MM):
                    printer.newPage()
                    y_offset_units = mm_to_units(MARGIN_MM)
                    
                painter.save()
                c_font = QFont(painter.font())
                c_font.setBold(True)
                c_font.setWeight(QFont.Black) 
                c_font.setPointSizeF(TEXT_FONT_SIZE * 1.1) 
                painter.setFont(c_font)
                
                left_indent = mm_to_units(20)
                available_width = page_width - left_indent

                c_rect = painter.boundingRect(left_indent, y_offset_units, available_width, mm_to_units(LINE_HEIGHT_MM), 
                                              Qt.AlignLeft, cloth_label)
                painter.drawText(c_rect, Qt.AlignLeft, cloth_label)
                y_offset_units += c_rect.height() + mm_to_units(LINE_HEIGHT_MM * 0.3)
                painter.restore()

                type_widgets = []
                for i in range(c_widget.type_layout.count()):
                    widget = c_widget.type_layout.itemAt(i).widget()
                    if isinstance(widget, TypeWidget):
                        type_widgets.append(widget)

                for t_idx, t_widget in enumerate(type_widgets):
                    type_name = t_widget.type_edit.text() or "Untitled Type"
                    type_label = f"{t_idx + 1}) {type_name}" 
                    
                    table_height_mm = LINE_HEIGHT_MM * 3 
                    if y_offset_units + mm_to_units(LINE_HEIGHT_MM) + mm_to_units(table_height_mm) > printer.height() - mm_to_units(MARGIN_MM):
                        printer.newPage()
                        y_offset_units = mm_to_units(MARGIN_MM)

                    painter.save()
                    t_font = QFont(painter.font())
                    t_font.setBold(True)
                    t_font.setWeight(QFont.Black) 
                    t_font.setPointSizeF(TEXT_FONT_SIZE * 1.0) 
                    painter.setFont(t_font)
                    
                    
                    left_indent = mm_to_units(25)
                    available_width = page_width - left_indent
                    
                    t_rect = painter.boundingRect(left_indent, y_offset_units, available_width, mm_to_units(LINE_HEIGHT_MM), 
                                                 Qt.AlignLeft, type_label)
                    painter.drawText(t_rect, Qt.AlignLeft, type_label)
                    y_offset_units += t_rect.height()
                    painter.restore()
                    
                    y_offset_units += mm_to_units(LINE_HEIGHT_MM * 0.3)
                    
                    painter.save()
                    table_indent = mm_to_units(25)
                    table_width = page_width - table_indent - mm_to_units(MARGIN_MM) 
                    painter.translate(table_indent, 0)
                    
                    y_offset_units = self.draw_type_table(
                        painter, t_widget, table_width, y_offset_units, 
                        mm_to_units, LINE_HEIGHT_MM, TABLE_HEADER_COLOR 
                    )
                    
                    painter.restore() 
                    
                    y_offset_units += mm_to_units(LINE_HEIGHT_MM) 

    def add_new_price_list(self):
        price_list_widget = PriceListWidget(self.sizes, parent=self)
        self.price_list_layout.insertWidget(self.price_list_layout.count() - 1, price_list_widget)
        price_list_widget.selected.connect(self.select_price_list)
        price_list_widget.modification_started.connect(self.enter_edit_mode)
        self.select_price_list(price_list_widget)
        self.enter_edit_mode()

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
    
    def delete_selected_price_list(self):
        if self.current_price_list:
            reply = QMessageBox.question(self, 'Delete Price List', 
                                         f"Are you sure you want to delete '{self.current_price_list.name_edit.text()}'?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.current_price_list.deleteLater()
                self.current_price_list = None
                self.exit_edit_mode()

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