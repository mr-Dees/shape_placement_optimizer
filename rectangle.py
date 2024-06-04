from PyQt6.QtCore import QRect


class Rectangle:
    _id_counter = 0

    def __init__(self, width, height, x=0, y=0):
        self.id = Rectangle._id_counter
        Rectangle._id_counter += 1
        self.width = width
        self.height = height
        self.x = x
        self.y = y

    def to_qrect(self):
        return QRect(self.x, self.y, self.width, self.height)

    def area(self):
        return self.width * self.height

    def intersects(self, other, margin=0):
        return QRect(self.x - margin, self.y - margin, self.width + 2 * margin, self.height + 2 * margin).intersects(
            QRect(other.x - margin, other.y - margin, other.width + 2 * margin, other.height + 2 * margin))
