from PyQt6.QtCore import QRect


class Rectangle:
    def __init__(self, width, height, x=0, y=0):
        self.width = width
        self.height = height
        self.x = x
        self.y = y

    def to_qrect(self):
        return QRect(self.x, self.y, self.width, self.height)

    def area(self):
        return self.width * self.height

    def intersects(self, other):
        return self.to_qrect().intersects(other.to_qrect())
