# Implement dijkstra and flooding algorithm using the LSR algorithm as a base.

from Dijkstra import Dijkstra
from Flooding import Flooding
from typing import *


def LSR_DIJKSTRA(graph: Dict[str, Dict[str, int]], start: str) -> Dict[str, Tuple[int, Tuple]]:
    # Function to implement the LSR algorithm using Dijkstra algorithm to create table routing
    # Return formate { node: (distance, path) }
    return Dijkstra(graph, start)

def LSR_FLOODING(graph: Dict[str, Dict[str, int]], start: str) -> Dict[str, Tuple[int, Tuple]]:
    # Function to implement the LSR algorithm using Flooding algorithm to create table routing
    # Return formate { node: (distance, path) }
    return Flooding(graph, start)

if __name__ == "__main__":
    # Test the LSR algorithm with Dijkstra
    pass












