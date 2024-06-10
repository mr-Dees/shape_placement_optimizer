from config import BL_FILL, BEST_FIT, ANT_COLONY, LINEAR_PROGRAMMING
import placement_algorithms as pas


class AlgorithmSelector:
    def __init__(self, canvas_width, canvas_height):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

    def calculate_placement(self, algorithm, placed_rectangles_list, new_rectangles_list, allow_flip, margin):
        if algorithm == BL_FILL:
            return pas.bl_fill(self.canvas_width, self.canvas_height, placed_rectangles_list, new_rectangles_list,
                               allow_flip, margin)
        elif algorithm == BEST_FIT:
            return pas.best_fit(self.canvas_width, self.canvas_height, placed_rectangles_list, new_rectangles_list,
                                allow_flip, margin)
        elif algorithm == ANT_COLONY:
            return pas.ant_colony_optimization(self.canvas_width, self.canvas_height, placed_rectangles_list,
                                               new_rectangles_list, allow_flip=allow_flip, margin=margin)
        elif algorithm == LINEAR_PROGRAMMING:
            return pas.solve_packing_problem(self.canvas_width, self.canvas_height, placed_rectangles_list,
                                             new_rectangles_list, allow_flip, margin)
        else:
            raise ValueError("Неизвестный алгоритм")
