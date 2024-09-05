from Table_Manager import Table_Manager
import asyncio
import threading

def init_node(node):
    router = Table_Manager(node, "123", "names2024-randomX-2024.txt", "topo2024-randomX-2024.txt")
    asyncio.run(router.run())

if __name__ == "__main__":
    # Initialize the other nodes
    nodes = ["auy201579"]
    threads = []
    for node in nodes:
        thread = threading.Thread(target=init_node, args=(node,))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()