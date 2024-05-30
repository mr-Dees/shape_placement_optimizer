from PyQt6.QtCore import QRect
import random
from multiprocessing import Pool


def bl_fill(canvas_width, canvas_height, rectangles, new_rectangles):
    placed_rectangles = rectangles.copy()
    # Сортировка новых прямоугольников по площади (объем)
    new_rectangles.sort(key=lambda r: r[0] * r[1], reverse=True)

    for width, height in new_rectangles:
        best_rect = None
        best_area = float('inf')

        for y in range(canvas_height - height, -1, -1):
            for x in range(canvas_width - width + 1):
                rect = QRect(x, y, width, height)
                if not any(rect.intersects(r) for r in placed_rectangles):
                    area = calculate_wasted_area(canvas_width, canvas_height, placed_rectangles, rect)
                    if area < best_area:
                        best_rect = rect
                        best_area = area
                        break  # Прерывание при нахождении первой подходящей позиции
            if best_rect:
                break  # Прерывание внешнего цикла, если подходящая позиция найдена

        if best_rect:
            placed_rectangles.append(best_rect)
        else:
            return None  # Если хотя бы один прямоугольник не удалось разместить, возвращаем None

    return placed_rectangles


def best_fit(canvas_width, canvas_height, rectangles, new_rectangles):
    placed_rectangles = rectangles.copy()
    # Сортировка новых прямоугольников по площади (объем)
    new_rectangles.sort(key=lambda r: r[0] * r[1], reverse=True)

    for width, height in new_rectangles:
        best_rect = None
        best_area = float('inf')

        for y in range(canvas_height - height, -1, -1):
            for x in range(canvas_width - width + 1):
                rect = QRect(x, y, width, height)
                if not any(rect.intersects(r) for r in placed_rectangles):
                    area = calculate_wasted_area(canvas_width, canvas_height, placed_rectangles, rect)
                    if area < best_area:
                        best_rect = rect
                        best_area = area

        if best_rect:
            placed_rectangles.append(best_rect)
        else:
            return None  # Если хотя бы один прямоугольник не удалось разместить, возвращаем None

    return placed_rectangles


def ant_colony_optimization(canvas_width, canvas_height, rectangles, new_rectangles, num_ants=10, num_iterations=100,
                            alpha=1.0, beta=2.0, evaporation_rate=0.5, pheromone_deposit=1.0):
    pheromones = [[1.0 for _ in range(canvas_width)] for _ in range(canvas_height)]
    placed_rectangles = rectangles.copy()
    # Сортировка новых прямоугольников по площади (объем)
    new_rectangles.sort(key=lambda r: r[0] * r[1], reverse=True)

    for width, height in new_rectangles:
        best_rect = None
        best_area = float('inf')

        for iteration in range(num_iterations):
            with Pool(processes=num_ants) as pool:
                results = pool.starmap(build_route, [
                    (canvas_width, canvas_height, placed_rectangles, width, height, pheromones, alpha, beta) for _ in
                    range(num_ants)])

            for rect in results:
                if rect:
                    area = calculate_wasted_area(canvas_width, canvas_height, placed_rectangles, rect)
                    if area < best_area:
                        best_rect = rect
                        best_area = area
                    update_pheromones(pheromones, rect, pheromone_deposit)

            evaporate_pheromones(pheromones, evaporation_rate)

        if best_rect:
            placed_rectangles.append(best_rect)
        else:
            return None  # Если хотя бы один прямоугольник не удалось разместить, возвращаем None

    return placed_rectangles


def build_route(canvas_width, canvas_height, rectangles, width, height, pheromones, alpha, beta):
    for y in range(canvas_height - height, -1, -1):
        for x in range(canvas_width - width + 1):
            rect = QRect(x, y, width, height)
            if not any(rect.intersects(r) for r in rectangles):
                return rect
    return None


def update_pheromones(pheromones, rect, pheromone_deposit):
    for y in range(rect.top(), rect.bottom() + 1):
        for x in range(rect.left(), rect.right() + 1):
            pheromones[y][x] += pheromone_deposit


def evaporate_pheromones(pheromones, evaporation_rate):
    for y in range(len(pheromones)):
        for x in range(len(pheromones[y])):
            pheromones[y][x] *= (1 - evaporation_rate)


def calculate_wasted_area(canvas_width, canvas_height, rectangles, rect):
    total_area = canvas_width * canvas_height
    used_area = sum([r.width() * r.height() for r in rectangles]) + rect.width() * rect.height()
    return total_area - used_area
