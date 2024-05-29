import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, \
    QPushButton, QMessageBox, QComboBox
from PyQt6.QtGui import QPainter, QPen, QPixmap
from PyQt6.QtCore import Qt, QRect
from constants import *
import placement_algorithms as pa


class PackingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.rectangles = []
        self.canvas_pixmap = QPixmap(self.canvas.size())
        self.canvas_pixmap.fill(Qt.GlobalColor.white)

    def init_ui(self):
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(WINDOW_X, WINDOW_Y, WINDOW_WIDTH, WINDOW_HEIGHT)

        self.canvas = QLabel()
        self.canvas.setStyleSheet(f"background-color: {CANVAS_BACKGROUND_COLOR};")
        self.canvas.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self.width_input = QLineEdit()
        self.height_input = QLineEdit()
        self.add_button = QPushButton("Добавить прямоугольник")
        self.add_button.clicked.connect(self.add_rectangle)

        self.algorithm_selector = QComboBox()
        self.algorithm_selector.addItems([BL_FILL, BEST_FIT, ANT_COLONY])

        layout = QVBoxLayout()
        control_layout = QHBoxLayout()
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
                new_rects = pa.bl_fill(self.canvas.width(), self.canvas.height(), self.rectangles, width, height)
            elif algorithm == BEST_FIT:
                new_rects = pa.best_fit(self.canvas.width(), self.canvas.height(), self.rectangles, width, height)
            elif algorithm == ANT_COLONY:
                new_rects = pa.ant_colony_optimization(self.canvas.width(), self.canvas.height(), self.rectangles,
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

    def closeEvent(self, event):
        reply = QMessageBox.question(self, "Выход", "Вы уверены, что хотите выйти?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PackingWindow()
    window.show()
    sys.exit(app.exec())
