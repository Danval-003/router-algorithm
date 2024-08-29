# Universidad del Valle de Guatemala
# Authors: Daniel Armando Valdez Reyes - 21240
#          Emilio José Solano Orozco - 21212
# 
# Description: This file contains the implementation of the Dijkstra algorithm
from typing import *
import heapq


def Dijkstra(graph: Dict[str, Dict[str, float]], start: str, from_node: str) -> Dict[str, Tuple[float, List[str]]]:
    """
    Implementa el algoritmo de Dijkstra para encontrar la ruta más corta que no pase por un nodo específico (from_node).
    Si no hay tal ruta, devuelve (0, [start]).
    """
    # Inicializa la distancia del nodo inicial a 0 y el resto a infinito solo para nodos presentes
    distance = {node: float('infinity') for node in graph}
    distance[start] = 0

    # Inicializa el camino del nodo inicial a sí mismo
    path = {node: [] for node in graph}
    path[start] = [(0, [start])]

    # Conjunto para almacenar los nodos visitados
    visited = set()

    # Cola de prioridad para explorar los caminos más cortos
    queue = [(0, start, [start])]
    heapq.heapify(queue)

    # Mientras la cola no esté vacía
    while queue:
        # Obtener el nodo con la distancia mínima
        current_distance, current_node, current_path = heapq.heappop(queue)

        # Añadir el nodo al conjunto de visitados
        if current_node not in visited:
            visited.add(current_node)

            # Para cada vecino del nodo actual
            for neighbor, weight in graph[current_node].items():
                # Si el vecino no ha sido visitado
                if neighbor not in visited:
                    # Calcular la nueva distancia
                    new_distance = current_distance + weight
                    new_path = current_path + [neighbor]

                    # Guardar todas las rutas posibles
                    if new_distance <= distance[neighbor]:
                        distance[neighbor] = new_distance
                        path[neighbor].append((new_distance, new_path))
                        # Añadir el vecino a la cola
                        heapq.heappush(queue, (new_distance, neighbor, new_path))

    # Filtrar y encontrar la ruta más corta que no pase por from_node
    result = {}
    for node in path:
        # Filtrar caminos que no pasen por from_node
        valid_paths = [p for d, p in sorted(path[node]) if from_node not in p]

        if valid_paths:
            # Si existen rutas válidas, devolver la primera (más corta)
            result[node] = (distance[node], valid_paths[0])
        else:
            # Si no hay rutas válidas, devolver el nodo inicial
            result[node] = (0, [start])
    
    return result


if __name__ == "__main__":
    # Test the Dijkstra algorithm
    graph = {
        'A': {'B': 1, 'C': 4},
        'B': {'A': 1, 'C': 2, 'D': 5},
        'C': {'A': 4, 'B': 2, 'D': 1},
        'D': {'B': 5, 'C': 1}
    }
    # Test the function with assert
    print(Dijkstra(graph, 'A'))
    assert Dijkstra(graph, 'A') == {'A': (0, ['A']), 'B': (1, ['A', 'B']), 'C': (3, ['A', 'B', 'C']), 'D': (4, ['A', 'B', 'C', 'D'])}
    print("Dijkstra algorithm works correctly")
