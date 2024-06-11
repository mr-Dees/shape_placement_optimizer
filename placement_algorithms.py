import threading
import time
import random
from rectangle import Rectangle
import functools
import pulp


def catch_exceptions(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise RuntimeError(f"Произошло исключение в функции {func.__name__}: {str(e)}") from e

    return wrapper


@catch_exceptions
def bl_fill(canvas_width, canvas_height, rectangles, new_rectangles, allow_flip=False, margin=0,
            progress_callback=None):
    placed_rectangles = rectangles.copy()
    new_rectangles.sort(key=lambda r: r.area(), reverse=True)
    total_rectangles = len(new_rectangles)

    for i, rect in enumerate(new_rectangles):
        best_rect = None

        for y in range(canvas_height - 1, -1, -1):
            for x in range(canvas_width - rect.height + 1):
                # Проверка исходной фигуры
                if x + rect.width <= canvas_width and y + rect.height <= canvas_height:
                    candidate = Rectangle(rect.width, rect.height, x, y)
                    if not any(candidate.intersects(r, margin) for r in placed_rectangles):
                        best_rect = candidate
                        break

                # Проверка перевернутой фигуры
                if allow_flip and x + rect.height <= canvas_width and y + rect.width <= canvas_height:
                    flipped_candidate = Rectangle(rect.height, rect.width, x, y)
                    if not any(flipped_candidate.intersects(r, margin) for r in placed_rectangles):
                        best_rect = flipped_candidate
                        break

            if best_rect:
                break

        if progress_callback:
            progress = int((i + 1) / total_rectangles * 100)
            progress_callback(progress)

        if best_rect:
            placed_rectangles.append(best_rect)
        else:
            return None

    return placed_rectangles


@catch_exceptions
def best_fit(canvas_width, canvas_height, rectangles, new_rectangles, allow_flip=False, margin=0,
             progress_callback=None):
    placed_rectangles = rectangles.copy()
    new_rectangles.sort(key=lambda r: r.area(), reverse=True)
    total_rectangles = len(new_rectangles)

    for i, rect in enumerate(new_rectangles):
        best_rect = None
        best_area = float('inf')

        for y in range(canvas_height - 1, -1, -1):
            for x in range(canvas_width - rect.height + 1):
                # Проверка исходной фигуры
                if x + rect.width <= canvas_width and y + rect.height <= canvas_height:
                    candidate = Rectangle(rect.width, rect.height, x, y)
                    if not any(candidate.intersects(r, margin) for r in placed_rectangles):
                        area = calculate_wasted_area(canvas_width, canvas_height, placed_rectangles, candidate)
                        if area < best_area:
                            best_rect = candidate
                            best_area = area

                # Проверка перевернутой фигуры
                if allow_flip and x + rect.height <= canvas_width and y + rect.width <= canvas_height:
                    flipped_candidate = Rectangle(rect.height, rect.width, x, y)
                    if not any(flipped_candidate.intersects(r, margin) for r in placed_rectangles):
                        area = calculate_wasted_area(canvas_width, canvas_height, placed_rectangles, flipped_candidate)
                        if area < best_area:
                            best_rect = flipped_candidate
                            best_area = area

        if progress_callback:
            progress = int((i + 1) / total_rectangles * 100)
            progress_callback(progress)

        if best_rect:
            placed_rectangles.append(best_rect)
        else:
            return None

    return placed_rectangles


@catch_exceptions
def ant_colony_optimization(canvas_width, canvas_height, rectangles, new_rectangles, num_ants=10, num_iterations=10,
                            alpha=1.0, beta=2.0, evaporation_rate=0.5, pheromone_deposit=1.0, allow_flip=False,
                            margin=0, progress_callback=None):
    pheromones = [[1.0 for _ in range(canvas_width)] for _ in range(canvas_height)]
    placed_rectangles = rectangles.copy()
    new_rectangles.sort(key=lambda r: r.area(), reverse=True)
    total_iterations = num_iterations * len(new_rectangles)
    current_iteration = 0

    for rect in new_rectangles:
        best_rect = None
        best_area = float('inf')

        for iteration in range(num_iterations):
            results = []
            for y in range(canvas_height - 1, -1, -1):
                for x in range(canvas_width):
                    # Проверка исходной фигуры
                    if x + rect.width <= canvas_width and y + rect.height <= canvas_height:
                        candidate = Rectangle(rect.width, rect.height, x, y)
                        if not any(candidate.intersects(r, margin) for r in placed_rectangles):
                            results.append(candidate)

                    # Проверка перевернутой фигуры
                    if allow_flip and x + rect.height <= canvas_width and y + rect.width <= canvas_height:
                        flipped_candidate = Rectangle(rect.height, rect.width, x, y)
                        if not any(flipped_candidate.intersects(r, margin) for r in placed_rectangles):
                            results.append(flipped_candidate)

            for candidate in results:
                if candidate:
                    area = calculate_wasted_area(canvas_width, canvas_height, placed_rectangles, candidate)
                    if area < best_area:
                        best_rect = candidate
                        best_area = area

            if best_rect is not None:
                update_pheromones(pheromones, best_rect, pheromone_deposit)
                evaporate_pheromones(pheromones, evaporation_rate)

            current_iteration += 1
            if progress_callback:
                progress = int(current_iteration / total_iterations * 100)
                progress_callback(progress)

        if best_rect:
            placed_rectangles.append(best_rect)
        else:
            return None

    return placed_rectangles


def update_pheromones(pheromones, rect, pheromone_deposit):
    if rect is None:
        return
    for y in range(max(0, rect.y), min(len(pheromones), rect.y + rect.height)):
        for x in range(max(0, rect.x), min(len(pheromones[y]), rect.x + rect.width)):
            pheromones[y][x] += pheromone_deposit


def evaporate_pheromones(pheromones, evaporation_rate):
    for y in range(len(pheromones)):
        for x in range(len(pheromones[y])):
            pheromones[y][x] *= (1 - evaporation_rate)


def calculate_wasted_area(canvas_width, canvas_height, rectangles, rect):
    total_area = canvas_width * canvas_height
    used_area = sum([r.width * r.height for r in rectangles]) + rect.width * rect.height
    return total_area - used_area


@catch_exceptions
def solve_packing_problem(canvas_width, canvas_height, placed_rectangles, new_rectangles, allow_flip=False, margin=0,
                          progress_callback=None):
    # Создаем задачу линейного программирования
    problem = pulp.LpProblem("PackingProblem", pulp.LpMinimize)

    # Создаем переменные
    x = pulp.LpVariable.dicts("x", range(len(new_rectangles)), 0, canvas_width, cat='Integer')
    y = pulp.LpVariable.dicts("y", range(len(new_rectangles)), 0, canvas_height, cat='Integer')
    r = pulp.LpVariable.dicts("r", range(len(new_rectangles)), 0, 1, cat='Binary')
    l = pulp.LpVariable.dicts("l", [(i, j) for i in range(len(new_rectangles)) for j in range(len(new_rectangles))], 0,
                              1, cat='Binary')
    b = pulp.LpVariable.dicts("b", [(i, j) for i in range(len(new_rectangles)) for j in range(len(new_rectangles))], 0,
                              1, cat='Binary')

    B = sum(max(rect.width, rect.height) for rect in new_rectangles)  # Большое число

    # Целевая функция: минимизация высоты полосы H_max и минимизация координат x
    H_max = pulp.LpVariable("H_max", 0, canvas_height, cat='Integer')
    problem += H_max + 0.001 * pulp.lpSum([x[i] for i in range(len(new_rectangles))]), "MinimizeStripHeightAndLeftmost"

    # Ограничения на размещение прямоугольников внутри полосы
    for i in range(len(new_rectangles)):
        width_i, height_i = new_rectangles[i].width, new_rectangles[i].height

        # Ограничения на размещение внутри холста без учета отступов от краев
        problem += x[i] + width_i * (1 - r[i]) + height_i * r[i] <= canvas_width
        problem += y[i] + height_i * (1 - r[i]) + width_i * r[i] <= H_max

        for j in range(i + 1, len(new_rectangles)):
            width_j, height_j = new_rectangles[j].width, new_rectangles[j].height

            # Ограничения на размещение с учетом удвоенных отступов между фигурами
            problem += x[i] + width_i * (1 - r[i]) + height_i * r[i] + 2 * margin <= x[j] + (1 - l[i, j]) * B
            problem += x[j] + width_j * (1 - r[j]) + height_j * r[j] + 2 * margin <= x[i] + (1 - l[j, i]) * B
            problem += y[i] + height_i * (1 - r[i]) + width_i * r[i] + 2 * margin <= y[j] + (1 - b[i, j]) * B
            problem += y[j] + height_j * (1 - r[j]) + width_j * r[j] + 2 * margin <= y[i] + (1 - b[j, i]) * B

            problem += l[i, j] + l[j, i] + b[i, j] + b[j, i] >= 1

    # Ограничение на неотрицательность H_max
    problem += H_max >= 0

    # Решаем задачу в отдельном потоке
    def solve_problem():
        solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=60, gapRel=0.01)  # Ограничение времени и относительного зазора
        problem.solve(solver)

    solve_thread = threading.Thread(target=solve_problem)
    solve_thread.start()

    # Обновляем прогресс пока задача решается
    progress = 0
    start_time = time.time()
    while solve_thread.is_alive():
        elapsed_time = time.time() - start_time
        if progress_callback:
            if elapsed_time <= 10:
                progress = min(progress + random.randint(1, 3), 98)
            elif 10 < elapsed_time <= 60:
                progress = min(progress + random.randint(0, 2), 98)
            else:
                progress = min(progress + random.randint(0, 1), 98)
            progress_callback(progress)
        time.sleep(1)  # Ждем 1 секунду перед следующей проверкой

    solve_thread.join()

    # Проверка на успешное размещение всех фигур
    if pulp.LpStatus[problem.status] != 'Optimal':
        return None

    # Возвращаем результаты
    results = []
    for i in range(len(new_rectangles)):
        width = new_rectangles[i].width if not pulp.value(r[i]) else new_rectangles[i].height
        height = new_rectangles[i].height if not pulp.value(r[i]) else new_rectangles[i].width
        results.append(Rectangle(
            width,
            height,
            int(pulp.value(x[i])),
            canvas_height - int(pulp.value(y[i])) - height,  # Учитываем высоту фигуры
            None,
            None
        ))

        # Обновляем прогресс до 100% с небольшими случайными задержками и изменениями
        if progress_callback:
            while progress < 100:
                progress = min(progress + random.randint(1, 3), 100)
                progress_callback(progress)
                time.sleep(random.uniform(0.05, 0.2))  # Небольшие случайные задержки

    return results
