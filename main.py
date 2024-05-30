import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, \
    QPushButton, QMessageBox, QComboBox, QMenu, QListWidget, QInputDialog
from PyQt6.QtGui import QPainter, QPen, QPixmap, QAction
from PyQt6.QtCore import Qt, QRect
from constants import *
import placement_algorithms_dynamic as pad
import placement_algorithms_static as pas


class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Главное меню")
        self.setGeometry(WINDOW_X, WINDOW_Y, WINDOW_WIDTH, WINDOW_HEIGHT)

        self.menu_bar = self.menuBar()
        self.mode_menu = self.menu_bar.addMenu("Режимы")

        self.dynamic_action = QAction("Динамическое", self)
        self.dynamic_action.triggered.connect(self.open_dynamic_mode)
        self.mode_menu.addAction(self.dynamic_action)

        self.static_action = QAction("Статическое", self)
        self.static_action.triggered.connect(self.open_static_mode)
        self.mode_menu.addAction(self.static_action)

    def open_dynamic_mode(self):
        self.dynamic_window = DynamicMode()
        self.dynamic_window.show()

    def open_static_mode(self):
        self.static_window = StaticMode()
        self.static_window.show()


class DynamicMode(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.rectangles = []
        self.canvas_pixmap = QPixmap(self.canvas.size())
        self.canvas_pixmap.fill(Qt.GlobalColor.white)

    def init_ui(self):
        self.setWindowTitle("Динамическое размещение")
        self.setGeometry(WINDOW_X, WINDOW_Y, WINDOW_WIDTH, WINDOW_HEIGHT)

        layout = QVBoxLayout()
        control_layout = QHBoxLayout()

        self.canvas = QLabel()
        self.canvas.setStyleSheet(f"background-color: {CANVAS_BACKGROUND_COLOR};")
        self.canvas.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self.width_input = QLineEdit()
        self.height_input = QLineEdit()
        self.add_button = QPushButton("Добавить прямоугольник")
        self.add_button.clicked.connect(self.add_rectangle)

        self.algorithm_selector = QComboBox()
        self.algorithm_selector.addItems([BL_FILL, BEST_FIT, ANT_COLONY])

        control_layout.addWidget(QLabel("Ширина:"))
        control_layout.addWidget(self.width_input)
        control_layout.addWidget(QLabel("Высота:"))
        control_layout.addWidget(self.height_input)
        control_layout.addWidget(self.algorithm_selector)
        control_layout.addWidget(self.add_button)
        layout.addLayout(control_layout)
        layout.addWidget(self.canvas)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def add_rectangle(self):
        width, height = self.get_input_dimensions()
        if width is None or height is None:
            return

        try:
            algorithm = self.algorithm_selector.currentText()
            if algorithm == BL_FILL:
                new_rects = pad.bl_fill(self.canvas.width(), self.canvas.height(), self.rectangles, width, height)
            elif algorithm == BEST_FIT:
                new_rects = pad.best_fit(self.canvas.width(), self.canvas.height(), self.rectangles, width, height)
            elif algorithm == ANT_COLONY:
                new_rects = pad.ant_colony_optimization(self.canvas.width(), self.canvas.height(), self.rectangles,
                                                        width, height)
            else:
                raise ValueError("Неизвестный алгоритм")

            if new_rects:
                self.rectangles.extend(new_rects)
                self.update_canvas()
            else:
                QMessageBox.warning(self, "Ошибка", "Невозможно добавить прямоугольник. Недостаточно места.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при добавлении прямоугольника: {str(e)}")

    def get_input_dimensions(self):
        try:
            width_text = self.width_input.text().strip()
            height_text = self.height_input.text().strip()
            if not width_text or not height_text:
                raise ValueError("Введите значения ширины и высоты.")
            width = int(width_text)
            height = int(height_text)
            if width <= 0 or height <= 0:
                raise ValueError("Ширина и высота должны быть положительными числами.")
            return width, height
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
            return None, None

    def update_canvas(self):
        pixmap = QPixmap(self.canvas.size())
        pixmap.fill(Qt.GlobalColor.white)
        painter = QPainter(pixmap)
        painter.setPen(QPen(PEN_COLOR, PEN_WIDTH))

        for rect in self.rectangles:
            painter.setBrush(RECTANGLE_COLOR)
            painter.drawRect(rect)

        if self.rectangles:
            last_rect = self.rectangles[-1]
            painter.setBrush(LAST_RECTANGLE_COLOR)
            painter.drawRect(last_rect)

        painter.end()
        self.canvas.setPixmap(pixmap)
        self.canvas_pixmap = pixmap


class StaticMode(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.rectangles = []
        self.new_rectangles = []
        self.highlighted_rect = None  # Переменная для хранения прямоугольника, на который наведена мышь

    def init_ui(self):
        self.setWindowTitle("Статическое размещение")
        self.setGeometry(WINDOW_X, WINDOW_Y, WINDOW_WIDTH, WINDOW_HEIGHT)

        layout = QHBoxLayout()
        control_layout = QVBoxLayout()

        self.canvas = QLabel()
        self.canvas.setStyleSheet(f"background-color: {CANVAS_BACKGROUND_COLOR};")
        self.canvas.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.canvas.setMouseTracking(True)  # Включаем отслеживание мыши
        self.canvas.mouseMoveEvent = self.on_mouse_move  # Привязываем обработчик события движения мыши

        self.width_input = QLineEdit()
        self.height_input = QLineEdit()
        self.add_button = QPushButton("Добавить прямоугольник")
        self.add_button.clicked.connect(self.add_rectangle)

        self.algorithm_selector = QComboBox()
        self.algorithm_selector.addItems([BL_FILL, BEST_FIT, ANT_COLONY])

        self.calculate_button = QPushButton("Рассчитать")
        self.calculate_button.clicked.connect(self.calculate_placement)

        self.rect_list = QListWidget()
        self.rect_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.rect_list.customContextMenuRequested.connect(self.show_context_menu)

        control_layout.addWidget(QLabel("Ширина:"))
        control_layout.addWidget(self.width_input)
        control_layout.addWidget(QLabel("Высота:"))
        control_layout.addWidget(self.height_input)
        control_layout.addWidget(self.algorithm_selector)
        control_layout.addWidget(self.add_button)
        control_layout.addWidget(self.calculate_button)
        control_layout.addWidget(QLabel("Список прямоугольников:"))
        control_layout.addWidget(self.rect_list)
        layout.addLayout(control_layout)
        layout.addWidget(self.canvas)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def add_rectangle(self):
        width, height = self.get_input_dimensions()
        if width is None or height is None:
            return

        self.new_rectangles.append((width, height))
        self.rect_list.addItem(f"Прямоугольник: {width}x{height}")

    def calculate_placement(self):
        try:
            algorithm = self.algorithm_selector.currentText()
            if algorithm == BL_FILL:
                new_rects = pas.bl_fill(self.canvas.width(), self.canvas.height(), self.rectangles, self.new_rectangles)
            elif algorithm == BEST_FIT:
                new_rects = pas.best_fit(self.canvas.width(), self.canvas.height(), self.rectangles,
                                         self.new_rectangles)
            elif algorithm == ANT_COLONY:
                new_rects = pas.ant_colony_optimization(self.canvas.width(), self.canvas.height(), self.rectangles,
                                                        self.new_rectangles)
            else:
                raise ValueError("Неизвестный алгоритм")

            if new_rects:
                self.rectangles = new_rects
                self.update_canvas()
            else:
                QMessageBox.warning(self, "Ошибка", "Невозможно разместить прямоугольники. Недостаточно места.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при размещении прямоугольников: {str(e)}")

    def get_input_dimensions(self):
        try:
            width_text = self.width_input.text().strip()
            height_text = self.height_input.text().strip()
            if not width_text or not height_text:
                raise ValueError("Введите значения ширины и высоты.")
            width = int(width_text)
            height = int(height_text)
            if width <= 0 or height <= 0:
                raise ValueError("Ширина и высота должны быть положительными числами.")
            return width, height
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
            return None, None

    def update_canvas(self):
        pixmap = QPixmap(self.canvas.size())
        pixmap.fill(Qt.GlobalColor.white)
        painter = QPainter(pixmap)
        painter.setPen(QPen(PEN_COLOR, PEN_WIDTH))

        for rect in self.rectangles:
            if rect == self.highlighted_rect:
                painter.setBrush(Qt.GlobalColor.yellow)  # Подсветка прямоугольника
            else:
                painter.setBrush(RECTANGLE_COLOR)
            painter.drawRect(rect)

        painter.end()
        self.canvas.setPixmap(pixmap)

    def on_mouse_move(self, event):
        cursor_pos = event.pos()
        self.highlighted_rect = None
        for rect in self.rectangles:
            if rect.contains(cursor_pos):
                self.highlighted_rect = rect
                break
        self.update_canvas()

    def show_context_menu(self, position):
        context_menu = QMenu(self)
        edit_action = QAction("Изменить", self)
        delete_action = QAction("Удалить", self)

        edit_action.triggered.connect(self.edit_rectangle)
        delete_action.triggered.connect(self.delete_rectangle)

        context_menu.addAction(edit_action)
        context_menu.addAction(delete_action)
        context_menu.exec(self.rect_list.mapToGlobal(position))

    def edit_rectangle(self):
        current_row = self.rect_list.currentRow()
        if current_row < 0:
            return

        width, height = self.new_rectangles[current_row]
        new_width, ok1 = QInputDialog.getInt(self, "Изменить ширину", "Ширина:", width, 1, 10000, 1)
        new_height, ok2 = QInputDialog.getInt(self, "Изменить высоту", "Высота:", height, 1, 10000, 1)

        if ok1 and ok2:
            self.new_rectangles[current_row] = (new_width, new_height)
            self.rect_list.item(current_row).setText(f"Прямоугольник: {new_width}x{new_height}")

    def delete_rectangle(self):
        current_row = self.rect_list.currentRow()
        if current_row < 0:
            return

        del self.new_rectangles[current_row]
        self.rect_list.takeItem(current_row)
        self.update_canvas()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_menu = MainMenu()
    main_menu.show()
    sys.exit(app.exec())
