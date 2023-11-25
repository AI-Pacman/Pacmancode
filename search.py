from collections import deque
from queue import PriorityQueue

from constants import *

ALGORITHMS = ["ALGORITHMS", "BFS", "DFS", "IDDFS", "GREEDY", "A*"]


def depth_first_search(start_node, pellet_node):
    stack = deque()
    visited = set()

    stack.append((start_node, []))  # (current_node, path)
    while stack:
        current_node, path = stack.pop()
        if current_node in visited:
            continue

        visited.add(current_node)

        if current_node == pellet_node:
            return path

        # Thêm tất cả các hàng xóm chưa được thăm vào stack
        for direction, neighbor in current_node.neighbors.items():
            if neighbor is not None and neighbor not in visited:
                stack.append((neighbor, path + [direction]))

    # Nếu hàm chạy đến đây, có nghĩa là không thể đến được pellet_node
    return None


def breadth_first_search(start_node, pellet_node):
    queue = deque()
    visited = set()

    queue.append((start_node, []))  # (current_node, path)
    while queue:
        current_node, path = queue.popleft()
        if current_node in visited:
            continue

        visited.add(current_node)

        if current_node == pellet_node:
            return path

        # Thêm tất cả các hàng xóm chưa được thăm vào hàng đợi
        for direction, neighbor in current_node.neighbors.items():
            if neighbor is not None and neighbor not in visited:
                queue.append((neighbor, path + [direction]))

    # Nếu hàm chạy đến đây, có nghĩa là không thể đến được pellet_node
    return None


def calculate_heuristic(current_position, target_position):
    dx = current_position.x - target_position.x
    dy = current_position.y - target_position.y
    return abs(dx) + abs(dy)


# Ý tưởng greedy search là tới đâu tìm tới đó nên dùng stack + priority queue sẽ tối ưu
def greedy_search(start_node, pellet_node):
    counter = 0
    visited = set()
    stack = [(start_node, [])]
    while stack:
        (current_node, path) = stack.pop()
        if current_node == pellet_node:
            return path

        if current_node in visited:
            continue

        visited.add(current_node)
        priority_queue = PriorityQueue()
        # Thêm tất cả các hàng xóm chưa được thăm vào hàng đợi với ưu tiên dựa trên heuristic
        for direction, neighbor in current_node.neighbors.items():
            if neighbor is not None and neighbor not in visited:
                # In Greedy search, the priority is based on a heuristic function
                heuristic = calculate_heuristic(neighbor.position, pellet_node.position)
                f_value = -heuristic  # Để priority queue nó sắp xếp từ cao đến thấp để làm việc với stack.
                counter += 1  # Tránh trường hợp các neighbors có cùng 1 giá trị heuristics
                priority_queue.put((f_value, counter, neighbor, path + [direction]))
        while not priority_queue.empty():
            item = priority_queue.get()
            current_node, path = item[2], item[3]
            stack.append((current_node, path))


def a_star_search(start_node, pellet_node):
    counter = 0
    priority_queue = PriorityQueue()
    priority_queue.put((0, counter, start_node, []))
    g_value = {start_node: 0}
    while not priority_queue.empty():
        item = priority_queue.get()
        f_value, current_node, path = item[0], item[2], item[3]
        if current_node == pellet_node:
            return path
        for direction, neighbor in current_node.neighbors.items():
            if neighbor is not None:
                new_g_value = g_value[start_node] + 1
                if neighbor not in g_value or new_g_value < g_value[neighbor]:
                    g_value[neighbor] = new_g_value
                    h_value = calculate_heuristic(neighbor.position, pellet_node.position)
                    f_value = new_g_value + h_value
                    counter += 1
                    priority_queue.put(
                        (
                            f_value,
                            counter,
                            neighbor,
                            path + [direction],
                        )
                    )


def depth_first_search_iterative_deepening(start_node, pellet_node):
    max_depth = 10
    stack = [(start_node, [])]
    visited = set()
    while True:
        while stack:
            (current_node, path) = stack.pop()
            if current_node in visited or len(path) > max_depth:
                continue

            visited.add(current_node)

            if current_node == pellet_node:
                return path

            # Thêm tất cả các hàng xóm chưa được thăm vào stack
            for direction, neighbor in current_node.neighbors.items():
                if neighbor is not None:
                    stack.append((neighbor, path + [direction]))

        max_depth += 10
        stack = [(start_node, [])]  # Reset the stack
        visited = set()
