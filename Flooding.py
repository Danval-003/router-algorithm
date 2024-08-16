# Universidad del Valle de Guatemala
# Authors: Daniel Armando Valdez Reyes - 21240
#          Emilio José Solano Orozco - 21212
# 
# Description: This file contains the implementation of the Flooding algorithm
from typing import *

def Flooding(graph: Dict[str, Dict[str, int]], start: str) -> Dict[str, Tuple[int, Tuple]]:
    # Function to implement the Flooding algorithm to create table routing
    # Return formate { node: (distance, path) }
    # Initialize the distance of the start node to 0
    distance = {node: float('infinity') for node in graph}
    distance[start] = 0
    # Initialize the path of the start node to itself
    path = {node: (0, [start]) for node in graph}
    # Create a set to store the visited nodes
    visited = set()
    # Create a queue to store the nodes to visit
    queue = [(0, start)]
    # While the queue is not empty
    while queue:
        # Get the node with the minimum distance
        current_distance, current_node = queue.pop(0)
        # Add the node to the visited set
        visited.add(current_node)
        # For each neighbor of the current node
        for neighbor, weight in graph[current_node].items():
            # If the neighbor has not been visited
            if neighbor not in visited:
                # Calculate the new distance
                new_distance = current_distance + weight
                # If the new distance is less than the current distance
                if new_distance < distance[neighbor]:
                    # Update the distance
                    distance[neighbor] = new_distance
                    # Update the path
                    path[neighbor] = (new_distance, path[current_node][1] + [neighbor])
                    # Add the neighbor to the queue
                    queue.append((new_distance, neighbor))
                    # Sort the queue
                    queue.sort()
    # Return the path
    return path


if __name__ == "__main__":
    # Test the Flooding algorithm
    graph = {
        'A': {'B': 1, 'C': 4},
        'B': {'A': 1, 'C': 2, 'D': 5},
        'C': {'A': 4, 'B': 2, 'D': 1},
        'D': {'B': 5, 'C': 1}
    }
    # Test the function with assert
    print(Flooding(graph, 'A'))
    assert Flooding(graph, 'A') == {'A': (0, ['A']), 'B': (1, ['A', 'B']), 'C': (3, ['A', 'B', 'C']), 'D': (4, ['A', 'B', 'C', 'D'])}
    print("Flooding algorithm works correctly")


