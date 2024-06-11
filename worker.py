from PyQt6.QtCore import QThread, pyqtSignal, QObject


class Worker(QObject):
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, algorithm_selector, algorithm, placed_rectangles_list, new_rectangles_list, allow_flip, margin):
        super().__init__()
        self.algorithm_selector = algorithm_selector
        self.algorithm = algorithm
        self.placed_rectangles_list = placed_rectangles_list
        self.new_rectangles_list = new_rectangles_list
        self.allow_flip = allow_flip
        self.margin = margin

    def run(self):
        try:
            new_rects = self.algorithm_selector.calculate_placement(
                self.algorithm, self.placed_rectangles_list, self.new_rectangles_list, self.allow_flip, self.margin,
                self.update_progress
            )
            self.finished.emit(new_rects)
        except Exception as e:
            self.error.emit(str(e))

    def update_progress(self, value):
        self.progress.emit(value)
