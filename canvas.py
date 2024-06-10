from PyQt6.QtGui import QPixmap, QPainter, QPen
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QRect
from rectangle import Rectangle
from config import *


class Canvas(QLabel):
    def __init__(self, width, height):
        super().__init__()
        self.setFixedSize(width, height)
        self.setStyleSheet(f"background-color: white;")
        self.highlighted_rect = None

    def update_canvas(self, placed_rectangles_list, margin, highlighted_rect):
        pixmap = QPixmap(self.size())
        pixmap.fill(WHITE_COLOR)
        painter = QPainter(pixmap)
        painter.setPen(QPen(BLACK_COLOR, PEN_WIDTH))

        for rect in placed_rectangles_list:
            if not isinstance(rect, Rectangle):
                raise TypeError(f"Ожидался объект Rectangle, но получен {type(rect)}")

            qrect = rect.to_qrect()
            painter.setBrush(YELLOW_COLOR if rect == highlighted_rect else LIGHT_GRAY_COLOR)
            painter.drawRect(qrect)

            if margin > 0:
                margin_rect = QRect(qrect.x() - margin, qrect.y() - margin, qrect.width() + 2 * margin,
                                    qrect.height() + 2 * margin)
                painter.setPen(QPen(LIGHT_GRAY_COLOR, 1, Qt.PenStyle.SolidLine))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRect(margin_rect)
                painter.setPen(QPen(BLACK_COLOR, PEN_WIDTH))

        painter.end()
        self.setPixmap(pixmap)
