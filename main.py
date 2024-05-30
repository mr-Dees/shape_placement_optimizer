import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, \
	QPushButton, QMessageBox, QComboBox, QMenu, QListWidget, QInputDialog
from PyQt6.QtGui import QPainter, QPen, QPixmap, QAction
from PyQt6.QtCore import Qt, QRect
from constants import *
import placement_algorithms_dynamic as pad
import placement_algorithms_static as pas
from rectangle import Rectangle


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

	def init_ui(self):
		self.setWindowTitle("Динамическое размещение")
		self.setGeometry(WINDOW_X, WINDOW_Y, WINDOW_WIDTH, WINDOW_HEIGHT)

		layout = QVBoxLayout()
		label = QLabel("Заглушка для динамического режима")
		layout.addWidget(label)

		central_widget = QWidget()
		central_widget.setLayout(layout)
		self.setCentralWidget(central_widget)


class StaticMode(QMainWindow):
	def __init__(self):
		super().__init__()
		self.init_ui()
		self.rectangles = []
		self.new_rectangles = []
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

		self.rect_list = QListWidget()
		self.rect_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
		self.rect_list.customContextMenuRequested.connect(self.show_context_menu)

		self.current_rect_list = QListWidget()

		control_layout.addWidget(QLabel("Ширина:"))
		control_layout.addWidget(self.width_input)
		control_layout.addWidget(QLabel("Высота:"))
		control_layout.addWidget(self.height_input)
		control_layout.addWidget(self.algorithm_selector)
		control_layout.addWidget(self.add_button)
		control_layout.addWidget(self.calculate_button)
		control_layout.addWidget(QLabel("Список прямоугольников для добавления:"))
		control_layout.addWidget(self.rect_list)
		control_layout.addWidget(QLabel("Текущие прямоугольники на холсте:"))
		control_layout.addWidget(self.current_rect_list)
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
		self.new_rectangles.append(new_rect)
		self.rect_list.addItem(f"Прямоугольник: {width}x{height}")

	def calculate_placement(self):
		if not self.new_rectangles:
			QMessageBox.warning(self, "Ошибка", "Нет новых прямоугольников для добавления.")
			return

		confirm = QMessageBox.question(self, "Рассчитать размещение",
									   "Хотите пересчитать все фигуры или добавить новые без пересчета?",
									   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
									   QMessageBox.StandardButton.No)
		if confirm == QMessageBox.StandardButton.Yes:
			self.recalculate_all()
		else:
			self.add_new_rectangles()

	def recalculate_all(self):
		try:
			algorithm = self.algorithm_selector.currentText()
			if algorithm == BL_FILL:
				new_rects = pas.bl_fill(self.canvas.width(), self.canvas.height(), [],
										self.new_rectangles + [Rectangle(rect.width, rect.height) for rect in
															   self.rectangles])
			elif algorithm == BEST_FIT:
				new_rects = pas.best_fit(self.canvas.width(), self.canvas.height(), [],
										 self.new_rectangles + [Rectangle(rect.width, rect.height) for rect in
																self.rectangles])
			elif algorithm == ANT_COLONY:
				new_rects = pas.ant_colony_optimization(self.canvas.width(), self.canvas.height(), [],
														self.new_rectangles + [Rectangle(rect.width, rect.height) for
																			   rect in self.rectangles])
			else:
				raise ValueError("Неизвестный алгоритм")

			if new_rects:
				self.rectangles = new_rects
				self.update_canvas()

				self.new_rectangles.clear()
				self.rect_list.clear()
				self.current_rect_list.clear()
				for rect in self.rectangles:
					self.current_rect_list.addItem(f"Прямоугольник: {rect.width}x{rect.height}")
			else:
				QMessageBox.warning(self, "Ошибка", "Невозможно разместить прямоугольники. Недостаточно места.")
		except Exception as e:
			QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при размещении прямоугольников: {str(e)}")

	def add_new_rectangles(self):
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
				self.rectangles.extend(new_rects)
				self.update_canvas()

				self.new_rectangles.clear()
				self.rect_list.clear()
				self.current_rect_list.clear()
				for rect in self.rectangles:
					self.current_rect_list.addItem(f"Прямоугольник: {rect.width}x{rect.height}")
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
			qrect = QRect(rect.x, rect.y, rect.width, rect.height)
			painter.setBrush(Qt.GlobalColor.yellow if rect == self.highlighted_rect else RECTANGLE_COLOR)
			painter.drawRect(qrect)

		painter.end()
		self.canvas.setPixmap(pixmap)

	def on_mouse_move(self, event):
		cursor_pos = event.pos()
		self.highlighted_rect = None
		for rect in self.rectangles:
			if QRect(rect.x, rect.y, rect.width, rect.height).contains(cursor_pos):
				self.highlighted_rect = rect
				break
		self.update_canvas()

	def on_mouse_press(self, event):
		if event.button() == Qt.MouseButton.RightButton:
			cursor_pos = event.pos()
			for rect in self.rectangles:
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

	def edit_rectangle(self):
		if self.highlighted_rect is None:
			return

		width, height = self.highlighted_rect.width, self.highlighted_rect.height
		new_width, ok1 = QInputDialog.getInt(self, "Изменить ширину", "Ширина:", width, 1, 10000, 1)
		new_height, ok2 = QInputDialog.getInt(self, "Изменить высоту", "Высота:", height, 1, 10000, 1)

		if ok1 and ok2:
			algorithm, ok3 = QInputDialog.getItem(self, "Выбор алгоритма", "Алгоритм:",
												  [BL_FILL, BEST_FIT, ANT_COLONY], 0, False)
			if ok3:
				confirm = QMessageBox.question(self, "Подтверждение изменений",
											   f"Изменить прямоугольник на {new_width}x{new_height} и пересчитать поле с использованием алгоритма {algorithm}?",
											   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
				if confirm == QMessageBox.StandardButton.Yes:
					# Удаляем старый прямоугольник из списка rectangles
					self.rectangles.remove(self.highlighted_rect)

					# Обновляем или добавляем новый прямоугольник в список new_rectangles
					index = next((i for i, rect in enumerate(self.new_rectangles) if
								  rect.width == width and rect.height == height), None)
					if index is not None:
						self.new_rectangles[index] = Rectangle(new_width, new_height)
					else:
						self.new_rectangles.append(Rectangle(new_width, new_height))

					# Обновляем список прямоугольников в rect_liДst
					self.rect_list.clear()
					for rect in self.new_rectangles:
						self.rect_list.addItem(f"Прямоугольник: {rect.width}x{rect.height}")

					# Пересчитываем размещение всех прямоугольников
					self.recalculate_all()
					self.update_canvas()

	def delete_rectangle(self):
		if self.highlighted_rect is None:
			return

		width, height = self.highlighted_rect.width, self.highlighted_rect.height
		confirm = QMessageBox.question(self, "Подтверждение удаления", f"Удалить прямоугольник {width}x{height}?",
									   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
		if confirm == QMessageBox.StandardButton.Yes:
			self.rectangles.remove(self.highlighted_rect)
			if self.highlighted_rect in self.new_rectangles:
				self.new_rectangles.remove(self.highlighted_rect)

			index = self.rect_list.currentRow()
			self.rect_list.takeItem(index)

			recalculate = QMessageBox.question(self, "Пересчитать поле", "Хотите пересчитать все поле?",
											   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
			if recalculate == QMessageBox.StandardButton.Yes:
				algorithm, ok = QInputDialog.getItem(self, "Выбор алгоритма", "Алгоритм:",
													 [BL_FILL, BEST_FIT, ANT_COLONY], 0, False)
				if ok:
					self.recalculate_all()
			else:
				self.update_canvas()


if __name__ == "__main__":
	app = QApplication(sys.argv)
	main_menu = MainMenu()
	main_menu.show()
	sys.exit(app.exec())
