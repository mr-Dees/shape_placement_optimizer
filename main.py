import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, \
    QPushButton, QMessageBox, QComboBox, QMenu, QListWidget, QInputDialog, QListWidgetItem
from PyQt6.QtGui import QPainter, QPen, QPixmap, QAction
from PyQt6.QtCore import Qt, QRect
from constants import *
import placement_algorithms as pas
from rectangle import Rectangle


class StaticMode(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.new_rectangles_list = []
        self.placed_rectangles_list = []
        self.highlighted_rect = None

    def init_ui(self):
        self.setWindowTitle("Статическое размещение")
        self.setGeometry(WINDOW_X, WINDOW_Y, WINDOW_WIDTH, WINDOW_HEIGHT)

        layout = QHBoxLayout()
        control_layout = QVBoxLayout()

        self.canvas = QLabel()
        self.canvas.setStyleSheet(f"background-color: {CANVAS_BACKGROUND_COLOR};")
        self.canvas.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.canvas.setMouseTracking(True)
        self.canvas.mouseMoveEvent = self.on_mouse_move
        self.canvas.mousePressEvent = self.on_mouse_press

        self.width_input = QLineEdit()
        self.height_input = QLineEdit()
        self.add_button = QPushButton("Добавить прямоугольник")
        self.add_button.clicked.connect(self.add_rectangle)

        self.algorithm_selector = QComboBox()
        self.algorithm_selector.addItems([BL_FILL, BEST_FIT, ANT_COLONY])

        self.calculate_button = QPushButton("Рассчитать")
        self.calculate_button.clicked.connect(self.calculate_placement)

        self.new_rectangles_list_widget = QListWidget()
        self.new_rectangles_list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.new_rectangles_list_widget.customContextMenuRequested.connect(self.show_new_rectangles_list_context_menu)

        self.placed_rectangles_list_widget = QListWidget()
        self.placed_rectangles_list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.placed_rectangles_list_widget.customContextMenuRequested.connect(
            self.show_placed_rectangles_list_context_menu)
        self.placed_rectangles_list_widget.itemClicked.connect(self.highlight_rectangle_from_list)

        control_layout.addWidget(QLabel("Ширина:"))
        control_layout.addWidget(self.width_input)
        control_layout.addWidget(QLabel("Высота:"))
        control_layout.addWidget(self.height_input)
        control_layout.addWidget(self.algorithm_selector)
        control_layout.addWidget(self.add_button)
        control_layout.addWidget(self.calculate_button)
        control_layout.addWidget(QLabel("Список прямоугольников для добавления:"))
        control_layout.addWidget(self.new_rectangles_list_widget)
        control_layout.addWidget(QLabel("Текущие прямоугольники на холсте:"))
        control_layout.addWidget(self.placed_rectangles_list_widget)

        layout.addLayout(control_layout)
        layout.addWidget(self.canvas)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def add_rectangle(self):
        width, height = self.get_input_dimensions()
        if width is None or height is None:
            return

        new_rect = Rectangle(width, height)
        self.new_rectangles_list.append(new_rect)
        item = QListWidgetItem(f"Прямоугольник: {width}x{height}")
        item.setData(Qt.ItemDataRole.UserRole, new_rect.id)
        self.new_rectangles_list_widget.addItem(item)

    def calculate_placement(self):
        if not self.new_rectangles_list:
            QMessageBox.warning(self, "Ошибка", "Нет новых прямоугольников для добавления.")
            return

        confirm = QMessageBox.question(
            self,
            "Рассчитать размещение",
            "Нажмите Yes для перерасчета всех размещенных фигур\n"
            "Или No для дополнения уже размещенных.\n"
            "Добавление произойдет в соответствии с выбранным режимом",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            self.recalculate_all()
        else:
            self.add_new_rectangles()

        self.update_placed_rectangles_list()

    def recalculate_all(self):
        try:
            algorithm = self.algorithm_selector.currentText()
            if algorithm == BL_FILL:
                new_rects = pas.bl_fill(
                    self.canvas.width(),
                    self.canvas.height(),
                    [],
                    self.new_rectangles_list + [Rectangle(rect.width, rect.height) for rect in
                                                self.placed_rectangles_list]
                )
            elif algorithm == BEST_FIT:
                new_rects = pas.best_fit(
                    self.canvas.width(),
                    self.canvas.height(),
                    [],
                    self.new_rectangles_list + [Rectangle(rect.width, rect.height) for rect in
                                                self.placed_rectangles_list]
                )
            elif algorithm == ANT_COLONY:
                new_rects = pas.ant_colony_optimization(
                    self.canvas.width(),
                    self.canvas.height(),
                    [],
                    self.new_rectangles_list + [Rectangle(rect.width, rect.height) for rect in
                                                self.placed_rectangles_list]
                )
            else:
                raise ValueError("Неизвестный алгоритм")

            if new_rects:
                self.placed_rectangles_list = new_rects
                self.update_canvas()
                self.new_rectangles_list.clear()
                self.new_rectangles_list_widget.clear()
                self.update_placed_rectangles_list()
            else:
                QMessageBox.warning(self, "Ошибка",
                                    "Невозможно разместить прямоугольники размером {width}x{height}. "
                                    "Недостаточно места на холсте.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при размещении прямоугольников: {str(e)}")

    def add_new_rectangles(self):
        try:
            algorithm = self.algorithm_selector.currentText()
            if algorithm == BL_FILL:
                new_rects = pas.bl_fill(
                    self.canvas.width(),
                    self.canvas.height(),
                    self.placed_rectangles_list,
                    self.new_rectangles_list
                )
            elif algorithm == BEST_FIT:
                new_rects = pas.best_fit(
                    self.canvas.width(),
                    self.canvas.height(),
                    self.placed_rectangles_list,
                    self.new_rectangles_list
                )
            elif algorithm == ANT_COLONY:
                new_rects = pas.ant_colony_optimization(
                    self.canvas.width(),
                    self.canvas.height(),
                    self.placed_rectangles_list,
                    self.new_rectangles_list
                )
            else:
                raise ValueError("Неизвестный алгоритм")

            if new_rects:
                self.placed_rectangles_list = new_rects
                self.update_canvas()
                self.new_rectangles_list.clear()
                self.new_rectangles_list_widget.clear()
                self.update_placed_rectangles_list()
            else:
                QMessageBox.warning(self, "Ошибка",
                                    "Невозможно разместить прямоугольники размером {width}x{height}. "
                                    "Недостаточно места на холсте.")
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

        for rect in self.placed_rectangles_list:
            qrect = QRect(rect.x, rect.y, rect.width, rect.height)
            painter.setBrush(Qt.GlobalColor.yellow if rect == self.highlighted_rect else RECTANGLE_COLOR)
            painter.drawRect(qrect)

        painter.end()
        self.canvas.setPixmap(pixmap)

    def update_placed_rectangles_list(self):
        self.placed_rectangles_list_widget.clear()
        for rect in self.placed_rectangles_list:
            item = QListWidgetItem(f"Прямоугольник: {rect.width}x{rect.height}")
            item.setData(Qt.ItemDataRole.UserRole, rect.id)
            self.placed_rectangles_list_widget.addItem(item)

    def on_mouse_move(self, event):
        cursor_pos = event.pos()
        self.highlighted_rect = None
        for rect in self.placed_rectangles_list:
            if QRect(rect.x, rect.y, rect.width, rect.height).contains(cursor_pos):
                self.highlighted_rect = rect
                break
        self.update_canvas()

    def on_mouse_press(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            cursor_pos = event.pos()
            for rect in self.placed_rectangles_list:
                if QRect(rect.x, rect.y, rect.width, rect.height).contains(cursor_pos):
                    self.highlighted_rect = rect
                    self.show_context_menu(event.pos())
                    break

    def show_context_menu(self, position):
        if self.highlighted_rect is None:
            return

        global_pos = self.canvas.mapToGlobal(position)
        context_menu = QMenu(self)
        edit_action = QAction("Изменить", self)
        delete_action = QAction("Удалить", self)
        edit_action.triggered.connect(self.edit_rectangle)
        delete_action.triggered.connect(self.delete_rectangle)
        context_menu.addAction(edit_action)
        context_menu.addAction(delete_action)
        context_menu.exec(global_pos)

    def show_new_rectangles_list_context_menu(self, position):
        context_menu = QMenu(self)
        delete_action = QAction("Удалить", self)
        delete_action.triggered.connect(self.delete_new_rectangle_list_item)
        context_menu.addAction(delete_action)
        context_menu.exec(self.new_rectangles_list_widget.mapToGlobal(position))

    def show_placed_rectangles_list_context_menu(self, position):
        context_menu = QMenu(self)
        edit_action = QAction("Изменить", self)
        delete_action = QAction("Удалить", self)
        edit_action.triggered.connect(self.edit_rectangle_from_list)
        delete_action.triggered.connect(self.delete_rectangle_from_list)
        context_menu.addAction(edit_action)
        context_menu.addAction(delete_action)
        context_menu.exec(self.placed_rectangles_list_widget.mapToGlobal(position))

    def delete_new_rectangle_list_item(self):
        current_row = self.new_rectangles_list_widget.currentRow()
        if current_row >= 0:
            self.new_rectangles_list_widget.takeItem(current_row)
            del self.new_rectangles_list[current_row]

    def edit_rectangle(self):
        if self.highlighted_rect is None:
            return

        width, height = self.highlighted_rect.width, self.highlighted_rect.height
        new_width, ok1 = QInputDialog.getInt(self, "Изменить ширину", "Ширина:", width, 1, 10000, 1)
        new_height, ok2 = QInputDialog.getInt(self, "Изменить высоту", "Высота:", height, 1, 10000, 1)

        if ok1 and ok2:
            algorithm, ok3 = QInputDialog.getItem(self, "Выбор алгоритма", "Алгоритм:", [BL_FILL, BEST_FIT, ANT_COLONY],
                                                  0, False)
            if ok3:
                confirm = QMessageBox.question(
                    self,
                    "Подтверждение изменений",
                    f"Изменить прямоугольник на {new_width}x{new_height} "
                    f"и пересчитать поле с использованием алгоритма {algorithm}?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if confirm == QMessageBox.StandardButton.Yes:
                    self.highlighted_rect.width = new_width
                    self.highlighted_rect.height = new_height
                    self.recalculate_all()
                    self.update_canvas()

    def delete_rectangle(self):
        if self.highlighted_rect is None:
            return

        width, height = self.highlighted_rect.width, self.highlighted_rect.height

        recalculate_choice = QMessageBox.question(
            self,
            "Выбор режима удаления",
            "Нажмите Yes для удаления с перерасчетом всех размещенных фигур\n"
            "Или No для удаления без перерасчета.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            defaultButton=QMessageBox.StandardButton.Yes
        )

        if recalculate_choice == QMessageBox.StandardButton.Yes:
            algorithm, ok = QInputDialog.getItem(
                self,
                "Выбор алгоритма",
                "Алгоритм:",
                [BL_FILL, BEST_FIT, ANT_COLONY],
                0,
                False
            )
            if ok:
                confirm = QMessageBox.question(
                    self,
                    "Подтверждение удаления",
                    f"Вы действительно хотите удалить прямоугольник {width}x{height} с пересчетом всех размещенных фигур?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if confirm == QMessageBox.StandardButton.Yes:
                    self.placed_rectangles_list.remove(self.highlighted_rect)
                    if self.highlighted_rect in self.new_rectangles_list:
                        self.new_rectangles_list.remove(self.highlighted_rect)
                    index = self.placed_rectangles_list_widget.findItems(f"Прямоугольник: {width}x{height}",
                                                                         Qt.MatchFlag.MatchExactly)
                    if index:
                        self.placed_rectangles_list_widget.takeItem(self.placed_rectangles_list_widget.row(index[0]))
                    self.recalculate_all()

        elif recalculate_choice == QMessageBox.StandardButton.No:
            confirm = QMessageBox.question(
                self,
                "Подтверждение удаления",
                f"Вы действительно хотите удалить прямоугольник {width}x{height} без пересчета всех размещенных фигур?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if confirm == QMessageBox.StandardButton.Yes:
                self.placed_rectangles_list.remove(self.highlighted_rect)
                if self.highlighted_rect in self.new_rectangles_list:
                    self.new_rectangles_list.remove(self.highlighted_rect)
                index = self.placed_rectangles_list_widget.findItems(f"Прямоугольник: {width}x{height}",
                                                                     Qt.MatchFlag.MatchExactly)
                if index:
                    self.placed_rectangles_list_widget.takeItem(self.placed_rectangles_list_widget.row(index[0]))
                self.update_canvas()
                self.update_placed_rectangles_list()

    def highlight_rectangle_from_list(self, item):
        rect_text = item.text()
        width, height = map(int, rect_text.split(":")[1].split("x"))
        rect_id = item.data(Qt.ItemDataRole.UserRole)
        self.highlighted_rect = next(
            (rect for rect in self.placed_rectangles_list if
             rect.width == width and rect.height == height and rect.id == rect_id),
            None
        )
        self.update_canvas()

    def edit_rectangle_from_list(self):
        current_item = self.placed_rectangles_list_widget.currentItem()
        if current_item is None:
            return

        rect_text = current_item.text()
        width, height = map(int, rect_text.split(":")[1].split("x"))
        rect_id = current_item.data(Qt.ItemDataRole.UserRole)
        rect_to_edit = next(
            (rect for rect in self.placed_rectangles_list if
             rect.width == width and rect.height == height and rect.id == rect_id),
            None
        )

        if rect_to_edit is None:
            return

        new_width, ok1 = QInputDialog.getInt(self, "Изменить ширину", "Ширина:", width, 1, 10000, 1)
        new_height, ok2 = QInputDialog.getInt(self, "Изменить высоту", "Высота:", height, 1, 10000, 1)

        if ok1 and ok2:
            algorithm, ok3 = QInputDialog.getItem(
                self,
                "Выбор алгоритма",
                "Алгоритм:",
                [BL_FILL, BEST_FIT, ANT_COLONY],
                0,
                False
            )
            if ok3:
                confirm = QMessageBox.question(
                    self,
                    "Подтверждение изменений",
                    f"Изменить прямоугольник на {new_width}x{new_height} "
                    f"и пересчитать поле с использованием алгоритма {algorithm}?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if confirm == QMessageBox.StandardButton.Yes:
                    rect_to_edit.width = new_width
                    rect_to_edit.height = new_height
                    self.recalculate_all()
                    self.update_canvas()

    def delete_rectangle_from_list(self):
        current_item = self.placed_rectangles_list_widget.currentItem()
        if current_item is None:
            return

        rect_text = current_item.text()
        width, height = map(int, rect_text.split(":")[1].split("x"))
        rect_id = current_item.data(Qt.ItemDataRole.UserRole)
        rect_to_delete = next(
            (rect for rect in self.placed_rectangles_list if
             rect.width == width and rect.height == height and rect.id == rect_id),
            None
        )

        if rect_to_delete is None:
            return

        recalculate_choice = QMessageBox.question(
            self,
            "Выбор режима удаления",
            "Нажмите Yes для удаления с перерасчетом всех размещенных фигур\n"
            "Или No для удаления без перерасчета.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            defaultButton=QMessageBox.StandardButton.Yes
        )

        if recalculate_choice == QMessageBox.StandardButton.Yes:
            algorithm, ok = QInputDialog.getItem(
                self,
                "Выбор алгоритма",
                "Алгоритм:",
                [BL_FILL, BEST_FIT, ANT_COLONY],
                0,
                False
            )
            if ok:
                confirm = QMessageBox.question(
                    self,
                    "Подтверждение удаления",
                    f"Вы хотите удалить прямоугольник {width}x{height} с пересчетом всех размещенных фигур?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if confirm == QMessageBox.StandardButton.Yes:
                    self.placed_rectangles_list.remove(rect_to_delete)
                    if rect_to_delete in self.new_rectangles_list:
                        self.new_rectangles_list.remove(rect_to_delete)
                    index = self.placed_rectangles_list_widget.currentRow()
                    self.placed_rectangles_list_widget.takeItem(index)
                    self.recalculate_all()

        elif recalculate_choice == QMessageBox.StandardButton.No:
            confirm = QMessageBox.question(
                self,
                "Подтверждение удаления",
                f"Вы хотите удалить прямоугольник {width}x{height} без пересчета всех размещенных фигур?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if confirm == QMessageBox.StandardButton.Yes:
                self.placed_rectangles_list.remove(rect_to_delete)
                if rect_to_delete in self.new_rectangles_list:
                    self.new_rectangles_list.remove(rect_to_delete)
                index = self.placed_rectangles_list_widget.currentRow()
                self.placed_rectangles_list_widget.takeItem(index)
                self.update_canvas()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    static_mode = StaticMode()
    static_mode.show()
    sys.exit(app.exec())
