from Table_Manager import Table_Manager
import asyncio
import threading

def init_node(node):
    router = Table_Manager(node, "PSSWD", "names2024-randomX-2024.txt", "topo2024-randomX-2024.txt", algorithm="Flooding")
    asyncio.run(router.run())

if __name__ == "__main__":
    # Initialize the other nodes
    nodes = ["val21240-node1", "val21240-node2", "val21240-node3", "val21240-node4"]
    threads = []
    for node in nodes:
        thread = threading.Thread(target=init_node, args=(node,))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()