from stack import Stack          
from queue import PriorityQueue, Queue

from constants import *
# from nodes import * # import các hàm trong file nodes.py

def depth_first_search(start_node, pellet_node):
    stack = Stack()
    visited = set()

    stack.push((start_node, []))  # (current_node, path)
    while not stack.isEmpty():
        current_node, path = stack.pop()
        if current_node in visited:
            continue

        visited.add(current_node)

        if current_node == pellet_node:
            return path

        # Thêm tất cả các hàng xóm chưa được thăm vào stack
        for direction, neighbor in current_node.neighbors.items():
            if neighbor is not None and neighbor not in visited:
                stack.push((neighbor, path + [direction]))

    # Nếu hàm chạy đến đây, có nghĩa là không thể đến được pellet_node
    return None
        
def breadth_first_search(start_node, pellet_node):
    queue = Queue()
    visited = set()

    queue.put((start_node, []))  # (current_node, path)
    while not queue.empty():
        current_node, path = queue.get()
        if current_node in visited:
            continue

        visited.add(current_node)

        if current_node == pellet_node:
            return path

        # Thêm tất cả các hàng xóm chưa được thăm vào hàng đợi
        for direction, neighbor in current_node.neighbors.items():
            if neighbor is not None and neighbor not in visited:
                queue.put((neighbor, path + [direction]))
                
    # Nếu hàm chạy đến đây, có nghĩa là không thể đến được pellet_node
    return None
                                
def calculate_heuristic(current_position, target_position):
    dx = current_position.x - target_position.x
    dy = current_position.y - target_position.y
    return dx**2 + dy**2  # Euclidean distance squared

def greedy_search(start_node, pellet_node):
    priority_queue = PriorityQueue()
    visited = set()

    priority_queue.put((0, start_node, []))  # (heuristic, current_node, path)

    while not priority_queue.empty():
        _, current_node, path = priority_queue.get()
        
        if current_node in visited:
            continue

        visited.add(current_node)

        # Check if the position of the current node is in the list of pellet positions
        if current_node == pellet_node:
            return path

        # Thêm tất cả các hàng xóm chưa được thăm vào hàng đợi với ưu tiên dựa trên heuristic
        for direction, neighbor in current_node.neighbors.items():
            if neighbor is not None and neighbor not in visited:
                # In Greedy search, the priority is based on a heuristic function
                heuristic = calculate_heuristic(neighbor.position, pellet_node.position)
                priority_queue.put((heuristic, neighbor, path + [direction]))

    # Nếu hàm chạy đến đây, có nghĩa là không thể đến được pellet_node
    return None

def depth_first_search_D(start_node, pellet_node, max_depth ):
    
    stack = Stack()
    visited = set()

    stack.push((start_node, []))  # (current_node, path)
    while not stack.isEmpty():
        current_node, path = stack.pop()
        if current_node in visited or len(path) > max_depth:
            continue

        visited.add(current_node)

        if current_node == pellet_node:
            return path

        # Thêm tất cả các hàng xóm chưa được thăm vào stack
        for direction, neighbor in current_node.neighbors.items():
            if neighbor is not None and neighbor not in visited:
                stack.push((neighbor, path + [direction]))

    # Nếu hàm chạy đến đây, có nghĩa là không thể đến được pellet_node với độ sâu tối đa
    return None

def dfs_with_iterative_deepening(start_node, pellet_node):
    max_depth = 1
    while True:
        result = depth_first_search_D(start_node, pellet_node, max_depth)
        if result is not None:
            return result
        max_depth += 1

