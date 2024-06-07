from rectangle import Rectangle


def bl_fill(canvas_width, canvas_height, rectangles, new_rectangles, allow_flip=False, margin=0):
    placed_rectangles = rectangles.copy()
    new_rectangles.sort(key=lambda r: r.area(), reverse=True)

    for rect in new_rectangles:
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

        if best_rect:
            placed_rectangles.append(best_rect)
        else:
            return None

    return placed_rectangles


def best_fit(canvas_width, canvas_height, rectangles, new_rectangles, allow_flip=False, margin=0):
    placed_rectangles = rectangles.copy()
    new_rectangles.sort(key=lambda r: r.area(), reverse=True)

    for rect in new_rectangles:
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

        if best_rect:
            placed_rectangles.append(best_rect)
        else:
            return None

    return placed_rectangles


def ant_colony_optimization(canvas_width, canvas_height, rectangles, new_rectangles, num_ants=10, num_iterations=100,
                            alpha=1.0, beta=2.0, evaporation_rate=0.5, pheromone_deposit=1.0, allow_flip=False,
                            margin=0):
    pheromones = [[1.0 for _ in range(canvas_width)] for _ in range(canvas_height)]
    placed_rectangles = rectangles.copy()
    new_rectangles.sort(key=lambda r: r.area(), reverse=True)

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
