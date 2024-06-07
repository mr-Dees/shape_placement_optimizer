from PyQt6.QtWidgets import QListWidgetItem
from PyQt6.QtCore import Qt
from rectangle import Rectangle


class RectangleManager:
    def __init__(self):
        self.new_rectangles_list = []
        self.placed_rectangles_list = []

    def add_rectangle(self, width, height, quantity, list_widget):
        for _ in range(quantity):
            new_rect = Rectangle(width, height)
            self.new_rectangles_list.append(new_rect)
            item = QListWidgetItem(f"Прямоугольник: {width}x{height}")
            item.setData(Qt.ItemDataRole.UserRole, new_rect.id)
            list_widget.addItem(item)

    def clear_all(self, new_list_widget, placed_list_widget):
        self.placed_rectangles_list.clear()
        self.new_rectangles_list.clear()
        new_list_widget.clear()
        placed_list_widget.clear()

    def update_placed_rectangles_list(self, list_widget):
        list_widget.clear()
        for rect in self.placed_rectangles_list:
            item = QListWidgetItem(f"Прямоугольник: {rect.width}x{rect.height}")
            item.setData(Qt.ItemDataRole.UserRole, rect.id)
            list_widget.addItem(item)

    def delete_rectangle(self, rect, list_widget):
        self.placed_rectangles_list.remove(rect)
        index = list_widget.findItems(f"Прямоугольник: {rect.width}x{rect.height}", Qt.MatchFlag.MatchExactly)
        if index:
            list_widget.takeItem(list_widget.row(index[0]))
