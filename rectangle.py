from PyQt6.QtCore import QRect


class Rectangle:
    _id_counter = 0

    def __init__(self, width, height, x=0, y=0, canvas_width=None, canvas_height=None):
        if width <= 0 or height <= 0:
            raise ValueError("Ширина и высота прямоугольника должны быть больше нуля")

        self.id = Rectangle._id_counter
        Rectangle._id_counter += 1
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

    def to_qrect(self):
        if self.canvas_width is None or self.canvas_height is None:
            return QRect(self.x, self.y, self.width, self.height)
        else:
            return QRect(self.x, self.canvas_height - self.y - self.height, self.width, self.height)

    def area(self):
        return self.width * self.height

    def _get_qrect(self, margin):
        if self.canvas_width is None or self.canvas_height is None:
            return QRect(self.x - margin, self.y - margin, self.width + 2 * margin, self.height + 2 * margin)
        else:
            return QRect(self.x - margin, self.canvas_height - self.y - self.height - margin,
                         self.width + 2 * margin, self.height + 2 * margin)

    def intersects(self, other, margin=0):
        if not isinstance(other, Rectangle):
            raise TypeError("Аргумент other должен быть экземпляром класса Rectangle")
        return self._get_qrect(margin).intersects(other._get_qrect(margin))
