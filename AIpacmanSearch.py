from stack import Stack          
from queue import PriorityQueue, Queue

from constants import *
# from nodes import * # import các hàm trong file nodes.py
def DFS( start_node, pellet_node_list):
        def dfs_recursive(current_node, path, path_node):
            if current_node in visited:
                return None  # Node đã được thăm, quay lui
            visited.add(current_node)
            if current_node in pellet_node_list and current_node != start_node:
                return path, path_node  # Pellet được tìm thấy trong cây con
            for direction, neighbor in current_node.neighbors.items():
                if neighbor is not None:
                    result = dfs_recursive(neighbor, path + [direction], path_node + [neighbor])
                    if result is not None:
                        return result  # Pellet được tìm thấy trong cây con
            return None

        stack = Stack()
        visited = set()

        stack.push((start_node, [], []))  # Reset stack cho mỗi pellet
        while not stack.isEmpty():
            current_node, path, path_node = stack.pop()
            result = dfs_recursive(current_node, path, path_node)
            if result is not None:
                return result  # Pellet được tìm thấy

        return None  # Pellet không được tìm thấy

def depth_first_search_D(start_node, pellet_node_list, max_depth ):
    
    def dfs_recursive(current_node, path, path_node, depth):
        if current_node in visited or depth > max_depth:
            return None  # Node đã được thăm hoặc đạt đến độ sâu tối đa, quay lui
        visited.add(current_node)
        
        if current_node in pellet_node_list and current_node != start_node:
            return path, path_node + [current_node]  # Pellet được tìm thấy trong cây con

        for direction, neighbor in current_node.neighbors.items():
            if neighbor is not None:
                result = dfs_recursive(neighbor, path + [direction], path_node + [current_node], depth + 1)
                if result is not None:
                    return result  # Pellet được tìm thấy trong cây con

        return None

    stack = Stack()
    visited = set()

    stack.push((start_node, [], []))  # Reset stack cho mỗi pellet
    while not stack.isEmpty():
        current_node, path, path_node = stack.pop()
        result = dfs_recursive(current_node, path, path_node, 0)
        if result is not None:
            return result  # Pellet được tìm thấy

    return None  # Pellet không được tìm thấy
  
def dfs_with_iterative_deepening(start_node, pellet_node):
    max_depth = 1
    while True:
        result = depth_first_search_D(start_node, pellet_node, max_depth)
        if result is not None:
            return result
        max_depth += 1  
        
def breadth_first_search(start_node, pellet_node_list):
    queue = Queue()
    visited = set()

    queue.put((start_node, [],[]))  # (current_node, path)
    while not queue.empty():
        current_node, path,path_node = queue.get()
        if current_node in visited:
            continue

        visited.add(current_node)

        if current_node in pellet_node_list and current_node != start_node:
            return path, path_node

        # Thêm tất cả các hàng xóm chưa được thăm vào hàng đợi
        for direction, neighbor in current_node.neighbors.items():
            if neighbor is not None and neighbor not in visited:
                queue.put((neighbor, path + [direction], path_node + [neighbor]))
                
    # Nếu hàm chạy đến đây, có nghĩa là không thể đến được pellet_node
    return None

def calculate_heuristic(current_position, target_position):
    dx = current_position.x - target_position.x
    dy = current_position.y - target_position.y
    return abs(dx) + abs(dy)    

def greedy_search(start_node, pellet_node_list): #Ý tưởng greedy search là tới đâu tìm tới đó nên dùng stack + priority queue sẽ tối ưu
        def greedy_search_recursive(current_node, path, path_node):
                counter=0
                if current_node in pellet_node_list and current_node != start_node:
                    return path, path_node
                
                if current_node in visited:
                    return None  # Node đã được thăm, quay lui

                visited.add(current_node)
                priority_queue = PriorityQueue()                                    
                # Thêm tất cả các hàng xóm chưa được thăm vào hàng đợi với ưu tiên dựa trên heuristic
                for direction, neighbor in current_node.neighbors.items():
                    if neighbor is not None and neighbor not in visited:
                        # In Greedy search, the priority is based on a heuristic function
                        for pellet_node in pellet_node_list:
                            heuristic = calculate_heuristic(neighbor.position, pellet_node.position)
                            f_value = -heuristic    #Để priority queue nó sắp xếp từ cao đến thấp để làm việc với stack.
                            counter += 1     #Tránh trường hợp các neighbors có cùng 1 giá trị heuristics
                            priority_queue.put((f_value, counter, neighbor, path + [direction], path_node + [neighbor]))
                while not priority_queue.empty():
                    item=priority_queue.get()
                    current_node, path, path_node = item[2],item[3], item[4]
                    stack.push((current_node,path,path_node))
                    
        
        stack = Stack()
        visited = set()            

        for pellet_node in pellet_node_list:
            if pellet_node == start_node:
                continue  
            stack.push((start_node, [], []))  # Reset stack cho mỗi pellet
            while not stack.isEmpty():
                current_node, path, path_node = stack.pop()
                result = greedy_search_recursive(current_node, path, path_node)
                if result is not None:
                    return result  # Pellet được tìm thấy

def A_star_search(start_node, pellet_node_list):
        counter=0
        priority_queue = PriorityQueue()
        priority_queue.put((0,counter,start_node,[],[]))
        g_value = {start_node:0}
        while not priority_queue.empty():
            item=priority_queue.get()
            f_value, current_node, path,path_node = item[0],item[2],item[3], item[4]
            
            if current_node in pellet_node_list and current_node != start_node:
                return path, path_node
            
            for direction, neighbor in current_node.neighbors.items():
                if neighbor is not None:
                    new_g_value=g_value[start_node]+1
                    if(neighbor not in g_value or new_g_value<g_value[neighbor]):
                        g_value[neighbor]= new_g_value
                        for pellet_node in pellet_node_list:
                            h_value=calculate_heuristic(neighbor.position,pellet_node.position)
                            f_value = new_g_value + h_value
                            counter+=1
                            priority_queue.put(
                                (
                                    f_value,
                                    counter,
                                    neighbor,
                                    path + [direction],
                                    path_node + [neighbor]
                                )
                            )
                        
       
# def A_star_search(start_node, pellet_node_list):
#     def a_star_recursive(current_node, path, path_node):
#         if current_node in pellet_node_list:
#             return path, path_node + [current_node]

#         for direction, neighbor in current_node.neighbors.items():
#             if neighbor is not None:
#                 new_g_value = g_value[current_node] + 1
#                 if neighbor not in g_value or new_g_value < g_value[neighbor]:
#                     g_value[neighbor] = new_g_value
#                     h_value = calculate_heuristic(neighbor.position, find_closest_pellet(neighbor, pellet_node_list).position)
#                     f_value = new_g_value + h_value
#                     counter += 1
#                     priority_queue.put((f_value, counter, neighbor, path + [direction], path_node + [current_node]))

#         if not priority_queue.empty():
#             next_item = priority_queue.get()
#             return a_star_recursive(next_item[2], next_item[3], next_item[4])
#         else:
#             return None, None

#     def find_closest_pellet(node, pellet_list):
#         closest_pellet = None
#         min_distance = float('inf')

#         for pellet in pellet_list:
#             distance = calculate_heuristic(node.position, pellet.position)
#             if distance < min_distance:
#                 min_distance = distance
#                 closest_pellet = pellet

#         return closest_pellet

#     counter = 0
#     priority_queue = PriorityQueue()
#     g_value = {start_node: 0}

#     closest_pellet = find_closest_pellet(start_node, pellet_node_list)
#     h_value = calculate_heuristic(start_node.position, closest_pellet.position)
#     f_value = g_value[start_node] + h_value

#     priority_queue.put((f_value, counter, start_node, [], []))
#     return a_star_recursive(start_node, [], [])
        
def depth_first_search_D10(start_node, pellet_node):
    max_depth = 10
    stack =[(start_node,[])]
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
