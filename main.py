import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, \
    QPushButton, QMessageBox, QComboBox, QMenu, QListWidget, QInputDialog, QCheckBox, QProgressDialog
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QRect
from algorithm_selector import AlgorithmSelector
from rectangle_manager import RectangleManager
from rectangle import Rectangle
from canvas import Canvas
from config import *


class UIManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.canvas_width, self.canvas_height = self.get_canvas_dimensions()
        self.init_ui()
        self.rectangle_manager = RectangleManager()
        self.algorithm_selector = AlgorithmSelector(self.canvas_width, self.canvas_height)

    def get_canvas_dimensions(self):
        width, ok1 = QInputDialog.getInt(self, "Размер полотна", "Ширина:", DEFAULT_CANVAS_WIDTH, 1, 10000, 1)
        if not ok1:
            sys.exit()

        height, ok2 = QInputDialog.getInt(self, "Размер полотна", "Высота:", DEFAULT_CANVAS_HEIGHT, 1, 10000, 1)
        if ok2:
            return width, height
        else:
            sys.exit()

    def init_ui(self):
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(WINDOW_X, WINDOW_Y, self.canvas_width, self.canvas_height)
        main_layout = QVBoxLayout()

        buttons_layout = QHBoxLayout()
        self.clear_all_button = QPushButton("Очистить все")
        self.clear_all_button.clicked.connect(self.clear_all)
        buttons_layout.addWidget(self.clear_all_button)

        self.recalculate_all_button = QPushButton("Пересчитать все полотно")
        self.recalculate_all_button.clicked.connect(
            lambda: self.calculate_placement(recalculate_confirm=True, placement_mode=QMessageBox.StandardButton.Yes))
        buttons_layout.addWidget(self.recalculate_all_button)

        self.resize_canvas_button = QPushButton("Изменить размер полотна")
        self.resize_canvas_button.clicked.connect(self.resize_canvas)
        buttons_layout.addWidget(self.resize_canvas_button)
        main_layout.addLayout(buttons_layout)

        content_layout = QHBoxLayout()
        control_elements_layout = QVBoxLayout()

        input_layout = QHBoxLayout()
        self.width_input = QLineEdit()
        self.height_input = QLineEdit()
        self.quantity_input = QLineEdit()
        self.quantity_input.setText("1")
        self.width_input.setMinimumWidth(MINIMUM_WIDTH_ENTRY)
        self.height_input.setMinimumWidth(MINIMUM_WIDTH_ENTRY)
        self.quantity_input.setMinimumWidth(MINIMUM_WIDTH_ENTRY)
        input_layout.addWidget(QLabel("Ширина:"))
        input_layout.addWidget(self.width_input)
        input_layout.addWidget(QLabel("Высота:"))
        input_layout.addWidget(self.height_input)
        control_elements_layout.addLayout(input_layout)

        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(QLabel("Кол-во: "))
        quantity_layout.addWidget(self.quantity_input)
        control_elements_layout.addLayout(quantity_layout)

        self.add_button = QPushButton("Добавить прямоугольник")
        self.add_button.clicked.connect(self.add_rectangle)
        control_elements_layout.addWidget(self.add_button)

        self.new_rectangles_list_widget = QListWidget()
        self.new_rectangles_list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.new_rectangles_list_widget.customContextMenuRequested.connect(self.show_new_rectangles_list_context_menu)
        control_elements_layout.addWidget(QLabel("Список прямоугольников для размещения:"))
        control_elements_layout.addWidget(self.new_rectangles_list_widget)

        algorithm_layout = QHBoxLayout()
        algorithm_label = QLabel("Алгоритм:")
        algorithm_layout.addWidget(algorithm_label)
        self.algorithm_selector_widget = QComboBox()
        self.algorithm_selector_widget.addItems([BL_FILL, BEST_FIT, ANT_COLONY, LINEAR_PROGRAMMING])
        self.algorithm_selector_widget.currentTextChanged.connect(self.on_algorithm_changed)
        algorithm_layout.addWidget(self.algorithm_selector_widget)
        algorithm_layout.setStretch(0, 1)
        algorithm_layout.setStretch(1, 3)
        control_elements_layout.addLayout(algorithm_layout)

        self.flip_checkbox = QCheckBox("Искать позицию с переворотом")
        self.flip_checkbox.stateChanged.connect(self.on_flip_checkbox_state_changed)
        control_elements_layout.addWidget(self.flip_checkbox)

        self.margin_checkbox = QCheckBox("Отступ")
        self.margin_checkbox.stateChanged.connect(self.toggle_margin_input)
        self.margin_input = QLineEdit()
        self.margin_input.setText("5")
        self.margin_input.setEnabled(False)
        margin_layout = QHBoxLayout()
        margin_layout.addWidget(self.margin_checkbox)
        margin_layout.addWidget(self.margin_input)
        control_elements_layout.addLayout(margin_layout)

        self.calculate_button = QPushButton("Разместить")
        self.calculate_button.clicked.connect(lambda: self.calculate_placement(placement_confirm=True))
        control_elements_layout.addWidget(self.calculate_button)

        self.placed_rectangles_list_widget = QListWidget()
        self.placed_rectangles_list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.placed_rectangles_list_widget.itemClicked.connect(self.on_placed_rectangle_item_clicked)
        self.placed_rectangles_list_widget.customContextMenuRequested.connect(
            self.show_placed_rectangles_list_context_menu)
        control_elements_layout.addWidget(QLabel("Текущие прямоугольники на полотне:"))
        control_elements_layout.addWidget(self.placed_rectangles_list_widget)

        content_layout.addLayout(control_elements_layout)
        self.canvas = Canvas(self.canvas_width, self.canvas_height)
        self.canvas.setMouseTracking(True)
        self.canvas.mouseMoveEvent = self.on_mouse_move
        self.canvas.mousePressEvent = self.on_mouse_press
        content_layout.addWidget(self.canvas)

        main_layout.addLayout(content_layout)
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def toggle_margin_input(self, state):
        self.margin_input.setEnabled(state == Qt.CheckState.Checked.value)
        if state == Qt.CheckState.Checked.value and len(self.rectangle_manager.placed_rectangles_list) > 1:
            QMessageBox.information(self, "Внимание",
                                    "На полотне уже находится несколько прямоугольников.\n"
                                    "Обратите внимание, что для корректного отображения реза "
                                    "может потребоваться пересчитать решение.")
        margin = int(self.margin_input.text().strip()) if state == Qt.CheckState.Checked.value else 0
        self.canvas.update_canvas(self.rectangle_manager.placed_rectangles_list, margin, self.canvas.highlighted_rect)

    def on_flip_checkbox_state_changed(self, state):
        if state == Qt.CheckState.Checked.value:
            QMessageBox.information(self, "Предупреждение", "Из-за режима поиска позиции с переворотом, "
                                                            "длительность расчета может увеличиться до двух раз.")

    def on_algorithm_changed(self, algorithm):
        if algorithm == LINEAR_PROGRAMMING:
            self.flip_checkbox.blockSignals(True)
            self.flip_checkbox.setChecked(True)
            self.flip_checkbox.setEnabled(False)
            self.flip_checkbox.blockSignals(False)
            QMessageBox.information(self, "Информация",
                                    "Данный алгоритм всегда ищет решение с переворотом фигуры "
                                    "и полностью пересчитывает размещение на полотне.\n"
                                    "Пожалуйста, учтите это при добавлении фигур на полотно.")
        else:
            self.flip_checkbox.setEnabled(True)

    def add_rectangle(self):
        width, height = self.get_input_dimensions()
        if width is None or height is None:
            return
        try:
            quantity = int(self.quantity_input.text().strip())
            if quantity <= 0:
                raise ValueError("Количество должно быть положительным числом.")
            self.rectangle_manager.add_rectangle(width, height, quantity, self.new_rectangles_list_widget)
            self.width_input.clear()
            self.height_input.clear()
            self.quantity_input.setText("1")
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка ввода", f"Ошибка ввода количества: {str(e)}")

    def calculate_placement(self, recalculate_confirm=False, placement_confirm=False, placement_mode=None):
        if recalculate_confirm:
            if not self.rectangle_manager.placed_rectangles_list:
                QMessageBox.information(self, "Нет размещенных фигур",
                                        "В данный момент нет прямоугольников доступных для перерасчета их позиции.")
                return

            algorithm, ok1 = QInputDialog.getItem(self, "Выбор алгоритма", "Алгоритм:",
                                                  [BL_FILL, BEST_FIT, ANT_COLONY, LINEAR_PROGRAMMING], 0, False)
            if not ok1:
                return

            allow_cut = QMessageBox.question(self, "Отступ на рез", "Необходим ли отступ на рез?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            allow_cut = allow_cut == QMessageBox.StandardButton.Yes
            if allow_cut:
                current_margin = int(self.margin_input.text().strip()) if self.margin_input.text().strip() else 5
                margin, ok2 = QInputDialog.getInt(self, "Отступ на рез", "Введите значение отступа:", current_margin, 0,
                                                  10000, 1)
                if not ok2:
                    return
            else:
                margin = int(self.margin_input.text().strip()) if self.margin_input.text().strip() else 0

            if algorithm == LINEAR_PROGRAMMING:
                confirm_dialog = QMessageBox.question(self, "Подтверждение пересчета",
                                                      f"Вы действительно хотите пересчитать все поле с помощью:\n"
                                                      f"алгоритма {algorithm}.\nУчтите, что данный алгоритм всегда "
                                                      f"ищет решение с функцией переворота.\n"
                                                      f"{'Отступ ' if allow_cut else 'без отступа'}"
                                                      f"{margin if allow_cut else ''} на рез\n",
                                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            else:
                allow_flip = QMessageBox.question(self, "Переворот фигуры", "Необходим ли поиск позиции с переворотом?",
                                                  QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                allow_flip = allow_flip == QMessageBox.StandardButton.Yes

                confirm_dialog = QMessageBox.question(self, "Подтверждение пересчета",
                                                      f"Вы действительно хотите пересчитать все поле с помощью:\n"
                                                      f"алгоритма {algorithm}.\n"
                                                      f"{'с отступом ' if allow_cut else 'без отступа'}"
                                                      f"{margin if allow_cut else ''} на рез\n"
                                                      f"и {'с функцией' if allow_flip else 'без функции'} переворота?",
                                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm_dialog == QMessageBox.StandardButton.No:
                return

            # Отключаем сигналы перед изменением состояния чекбоксов
            self.algorithm_selector_widget.blockSignals(True)
            self.margin_checkbox.blockSignals(True)
            self.margin_input.blockSignals(True)
            self.flip_checkbox.blockSignals(True)

            self.algorithm_selector_widget.setCurrentText(algorithm)
            self.margin_checkbox.setChecked(allow_cut)
            self.margin_input.setEnabled(allow_cut)
            self.margin_input.setText(str(margin))
            self.flip_checkbox.setChecked(allow_flip if algorithm != LINEAR_PROGRAMMING else True)
            self.flip_checkbox.setEnabled(algorithm != LINEAR_PROGRAMMING)

            # Включаем сигналы после изменения состояния чекбоксов
            self.algorithm_selector_widget.blockSignals(False)
            self.margin_checkbox.blockSignals(False)
            self.margin_input.blockSignals(False)
            self.flip_checkbox.blockSignals(False)

        try:
            if placement_confirm:
                if not self.rectangle_manager.new_rectangles_list:
                    raise ValueError("Нет новых прямоугольников для добавления.")

                algorithm = self.algorithm_selector_widget.currentText()
                if algorithm == LINEAR_PROGRAMMING:
                    placement_mode = QMessageBox.question(self, "Рассчитать размещение",
                                                          f"Нажмите Yes для перерасчета всех размещенных фигур\n"
                                                          f"или Cancel для отмены.\nРазмещение произойдет в "
                                                          f"соответствии с алгоритмом Linear Programming",
                                                          QMessageBox.StandardButton.Yes |
                                                          QMessageBox.StandardButton.Cancel,
                                                          QMessageBox.StandardButton.Cancel)
                    if placement_mode == QMessageBox.StandardButton.Cancel:
                        return
                else:
                    placement_mode = QMessageBox.question(self, "Рассчитать размещение",
                                                          f"Нажмите Yes для перерасчета всех размещенных фигур\n"
                                                          f"Или No для дополнения уже размещенных.\nРазмещение "
                                                          f"произойдет в соответствии с алгоритмом {algorithm}",
                                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                                                          | QMessageBox.StandardButton.Cancel,
                                                          QMessageBox.StandardButton.Cancel)
                    if placement_mode == QMessageBox.StandardButton.Cancel:
                        return

            progress_dialog = QProgressDialog("Выполняется расчет...", "Отмена", 0, 100, self)
            progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
            progress_dialog.setAutoClose(True)
            progress_dialog.setAutoReset(True)
            progress_dialog.setValue(0)
            progress_dialog.show()

            def progress_callback(progress):
                if progress_dialog.wasCanceled():
                    raise RuntimeError("Расчет отменен пользователем")
                progress_dialog.setValue(progress)
                QApplication.processEvents()

            algorithm = self.algorithm_selector_widget.currentText()
            allow_flip = self.flip_checkbox.isChecked()
            margin = int(self.margin_input.text().strip()) if self.margin_checkbox.isChecked() else 0

            if placement_mode == QMessageBox.StandardButton.Yes:
                new_rects = self.algorithm_selector.calculate_placement(algorithm, [],
                                                                        self.rectangle_manager.new_rectangles_list + [
                                                                            Rectangle(rect.width, rect.height) for rect
                                                                            in
                                                                            self.rectangle_manager.placed_rectangles_list],
                                                                        allow_flip, margin, progress_callback)
            else:
                new_rects = self.algorithm_selector.calculate_placement(algorithm,
                                                                        self.rectangle_manager.placed_rectangles_list,
                                                                        self.rectangle_manager.new_rectangles_list,
                                                                        allow_flip, margin, progress_callback)

            if new_rects:
                self.rectangle_manager.placed_rectangles_list = new_rects
                self.canvas.update_canvas(self.rectangle_manager.placed_rectangles_list, margin,
                                          self.canvas.highlighted_rect)
                self.rectangle_manager.new_rectangles_list.clear()
                self.new_rectangles_list_widget.clear()
            else:
                raise ValueError("Недостаточно места на холсте.")
            self.rectangle_manager.update_placed_rectangles_list(self.placed_rectangles_list_widget)
        except RuntimeError as e:
            QMessageBox.warning(self, "Ошибка", f"Произошла ошибка в алгоритме размещения: {str(e)}")
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", f"Произошла ошибка при размещении прямоугольников: {str(e)}")
        except Exception as e:
            QMessageBox.warning(self, "Неизвестная ошибка", f"Произошла неизвестная ошибка: {str(e)}")

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
            QMessageBox.warning(self, "Ошибка ввода", f"Произошла ошибка при вводе данных: {str(e)}")
            return None, None

    def clear_all(self):
        confirm = QMessageBox.question(self, "Подтверждение очистки", "Вы действительно хотите очистить все?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            self.rectangle_manager.clear_all(self.new_rectangles_list_widget, self.placed_rectangles_list_widget)
            self.canvas.update_canvas(self.rectangle_manager.placed_rectangles_list, 0, None)

    def resize_canvas(self):
        try:
            width, ok1 = QInputDialog.getInt(self, "Изменить размер полотна", "Ширина:",
                                             self.canvas_width, 1, 10000, 1)
            if not ok1:
                return
            height, ok2 = QInputDialog.getInt(self, "Изменить размер полотна", "Высота:",
                                              self.canvas_height, 1, 10000, 1)
            if ok2:
                confirm = QMessageBox.question(self, "Подтверждение изменения размера",
                                               "Все данные будут очищены. Вы уверены?",
                                               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if confirm == QMessageBox.StandardButton.Yes:
                    self.canvas_width = width
                    self.canvas_height = height
                    self.canvas.setFixedSize(self.canvas_width, self.canvas_height)
                    self.rectangle_manager.clear_all(self.new_rectangles_list_widget,
                                                     self.placed_rectangles_list_widget)
                    self.algorithm_selector.canvas_width = self.canvas_width
                    self.algorithm_selector.canvas_height = self.canvas_height
                    self.canvas.update_canvas(self.rectangle_manager.placed_rectangles_list, 0, None)
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка ввода", f"Произошла ошибка при вводе данных: {str(e)}")

    def on_placed_rectangle_item_clicked(self, item):
        rect_text = item.text()
        width, height = map(int, rect_text.split(":")[1].split("x"))
        rect_id = item.data(Qt.ItemDataRole.UserRole)
        self.canvas.highlighted_rect = next((rect for rect in self.rectangle_manager.placed_rectangles_list if
                                             rect.width == width and rect.height == height and rect.id == rect_id),
                                            None)
        self.canvas.update_canvas(self.rectangle_manager.placed_rectangles_list,
                                  int(self.margin_input.text().strip()) if self.margin_checkbox.isChecked() else 0,
                                  self.canvas.highlighted_rect)

    def on_mouse_move(self, event):
        cursor_pos = event.pos()
        self.canvas.highlighted_rect = None
        for rect in self.rectangle_manager.placed_rectangles_list:
            if QRect(rect.x, rect.y, rect.width, rect.height).contains(cursor_pos):
                self.canvas.highlighted_rect = rect
                break
        self.canvas.update_canvas(self.rectangle_manager.placed_rectangles_list,
                                  int(self.margin_input.text().strip()) if self.margin_checkbox.isChecked() else 0,
                                  self.canvas.highlighted_rect)

    def on_mouse_press(self, event):
        cursor_pos = event.pos()
        if event.button() == Qt.MouseButton.RightButton:
            for rect in self.rectangle_manager.placed_rectangles_list:
                if QRect(rect.x, rect.y, rect.width, rect.height).contains(cursor_pos):
                    self.canvas.highlighted_rect = rect
                    self.canvas.update_canvas(self.rectangle_manager.placed_rectangles_list,
                                              int(self.margin_input.text().strip())
                                              if self.margin_checkbox.isChecked() else 0,
                                              self.canvas.highlighted_rect)
                    self.show_context_menu(event.pos())
                    return
            self.canvas.highlighted_rect = None
            self.canvas.update_canvas(self.rectangle_manager.placed_rectangles_list,
                                      int(self.margin_input.text().strip()) if self.margin_checkbox.isChecked() else 0,
                                      self.canvas.highlighted_rect)
            self.show_context_menu(event.pos())
        elif event.button() == Qt.MouseButton.LeftButton:
            for rect in self.rectangle_manager.placed_rectangles_list:
                if QRect(rect.x, rect.y, rect.width, rect.height).contains(cursor_pos):
                    self.canvas.highlighted_rect = rect
                    self.select_rectangle_in_list(rect)
                    break
            self.canvas.update_canvas(self.rectangle_manager.placed_rectangles_list,
                                      int(self.margin_input.text().strip()) if self.margin_checkbox.isChecked() else 0,
                                      self.canvas.highlighted_rect)

    def show_context_menu(self, position):
        if self.canvas.highlighted_rect is None:
            return
        global_pos = self.canvas.mapToGlobal(position)
        context_menu = QMenu(self)
        edit_action = QAction("Изменить", self)
        edit_action.triggered.connect(lambda: self.edit_rectangle(rect=None))
        context_menu.addAction(edit_action)
        delete_action = QAction("Удалить", self)
        delete_action.triggered.connect(lambda: self.delete_rectangle(rect=None))
        context_menu.addAction(delete_action)
        context_menu.exec(global_pos)

    def show_new_rectangles_list_context_menu(self, position):
        item = self.new_rectangles_list_widget.itemAt(position)
        if item is not None:
            context_menu = QMenu(self)
            delete_action = QAction("Удалить", self)
            delete_action.triggered.connect(self.delete_new_rectangle_list_item)
            context_menu.addAction(delete_action)
            context_menu.exec(self.new_rectangles_list_widget.mapToGlobal(position))

    def show_placed_rectangles_list_context_menu(self, position):
        item = self.placed_rectangles_list_widget.itemAt(position)
        if item is not None:
            context_menu = QMenu(self)
            edit_action = QAction("Изменить", self)
            delete_action = QAction("Удалить", self)
            edit_action.triggered.connect(self.edit_rectangle)
            delete_action.triggered.connect(self.delete_rectangle)
            context_menu.addAction(edit_action)
            context_menu.addAction(delete_action)
            context_menu.exec(self.placed_rectangles_list_widget.mapToGlobal(position))

    def delete_new_rectangle_list_item(self):
        current_row = self.new_rectangles_list_widget.currentRow()
        if current_row >= 0:
            self.new_rectangles_list_widget.takeItem(current_row)
            del self.rectangle_manager.new_rectangles_list[current_row]

    def select_rectangle_in_list(self, rect):
        for index in range(self.placed_rectangles_list_widget.count()):
            item = self.placed_rectangles_list_widget.item(index)
            if item.data(Qt.ItemDataRole.UserRole) == rect.id:
                self.placed_rectangles_list_widget.setCurrentItem(item)
                break

    def edit_rectangle(self, rect=None):
        if rect is None:
            if self.canvas.highlighted_rect is None:
                return
            rect = self.canvas.highlighted_rect
        else:
            item = self.placed_rectangles_list_widget.currentItem()
            if item is None:
                return
            rect_text = item.text()
            width, height = map(int, rect_text.split(":")[1].split("x"))
            rect_id = item.data(Qt.ItemDataRole.UserRole)
            rect = next((r for r in self.rectangle_manager.placed_rectangles_list if
                         r.width == width and r.height == height and r.id == rect_id), None)
            if rect is None:
                return

        width, height = rect.width, rect.height
        try:
            new_width, ok1 = QInputDialog.getInt(self, "Изменить ширину", "Ширина:", width, 1, 10000, 1)
            if not ok1:
                return

            new_height, ok2 = QInputDialog.getInt(self, "Изменить высоту", "Высота:", height, 1, 10000, 1)
            if ok2:
                algorithm, ok3 = QInputDialog.getItem(self, "Выбор алгоритма", "Алгоритм:",
                                                      [BL_FILL, BEST_FIT, ANT_COLONY, LINEAR_PROGRAMMING], 0, False)
                if ok3:
                    confirm = QMessageBox.question(self, "Подтверждение изменений",
                                                   f"Изменить прямоугольник на {new_width}x{new_height} "
                                                   f"и пересчитать поле с использованием алгоритма {algorithm}?",
                                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    if confirm == QMessageBox.StandardButton.Yes:
                        rect.width = new_width
                        rect.height = new_height
                        self.calculate_placement(placement_mode=QMessageBox.StandardButton.Yes)
                        self.canvas.update_canvas(self.rectangle_manager.placed_rectangles_list,
                                                  int(self.margin_input.text().strip())
                                                  if self.margin_checkbox.isChecked() else 0,
                                                  self.canvas.highlighted_rect)
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка ввода", f"Произошла ошибка при вводе данных: {str(e)}")

    def delete_rectangle(self, rect=None):
        if rect is None:
            if self.canvas.highlighted_rect is None:
                return
            rect = self.canvas.highlighted_rect
        else:
            item = self.placed_rectangles_list_widget.currentItem()
            if item is None:
                return
            rect_text = item.text()
            width, height = map(int, rect_text.split(":")[1].split("x"))
            rect_id = item.data(Qt.ItemDataRole.UserRole)
            rect = next((r for r in self.rectangle_manager.placed_rectangles_list if
                         r.width == width and r.height == height and r.id == rect_id), None)
            if rect is None:
                return

        width, height = rect.width, rect.height
        recalculate_choice = QMessageBox.question(self, "Выбор режима удаления",
                                                  "Нажмите Yes для удаления с перерасчетом всех размещенных фигур\n"
                                                  "Или No для удаления без перерасчета.",
                                                  QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                                  defaultButton=QMessageBox.StandardButton.Yes)

        if recalculate_choice == QMessageBox.StandardButton.Yes:
            algorithm, ok = QInputDialog.getItem(self, "Выбор алгоритма", "Алгоритм:",
                                                 [BL_FILL, BEST_FIT, ANT_COLONY, LINEAR_PROGRAMMING], 0, False)
            if ok:
                confirm = QMessageBox.question(self, "Подтверждение удаления",
                                               f"Вы хотите удалить прямоугольник {width}x{height} " 
                                               f"с пересчетом всех размещенных фигур?",
                                               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if confirm == QMessageBox.StandardButton.Yes:
                    self.rectangle_manager.delete_rectangle(rect, self.placed_rectangles_list_widget)
                    if self.rectangle_manager.placed_rectangles_list:  # Проверка на наличие фигур
                        self.calculate_placement(placement_mode=QMessageBox.StandardButton.Yes)
                    else:   # Обновление холста с пустым списком фигур
                        self.canvas.update_canvas([], 0, None)
        elif recalculate_choice == QMessageBox.StandardButton.No:
            confirm = QMessageBox.question(self, "Подтверждение удаления",
                                           f"Вы хотите удалить прямоугольник {width}x{height} "
                                           f"без пересчета всех размещенных фигур?",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                self.rectangle_manager.delete_rectangle(rect, self.placed_rectangles_list_widget)
                self.canvas.update_canvas(self.rectangle_manager.placed_rectangles_list,
                                          int(self.margin_input.text().strip()) if self.margin_checkbox.isChecked() else 0,
                                          self.canvas.highlighted_rect)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui_manager = UIManager()
    ui_manager.show()
    sys.exit(app.exec())
