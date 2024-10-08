import asyncio
import json
from ManagerXMPP import ManagerXMPP, parseXMLTOJSON
from tabulate import tabulate
import pandas as pd
from typing import Dict
import time
from Dijkstra import Dijkstra
import threading
class Table_Manager(ManagerXMPP):
    def __init__(self, jid, password, namesfile, topologyfile, algorithm="Dijkstra"):
        ManagerXMPP.__init__(self, jid, password)
        self.namesfile = namesfile
        self.topologyfile = topologyfile
        self.actual_node = ""
        self.neighbors = {}
        self.load_config()
        self.init_session()
        self.events_handlers = {
            "message": self.message,
        }
        self.on_eco = {}
        self.algorithm = algorithm
        self.table_with_weights = {}
        self.table_version = 0
        self.ecos = 1
        self.table_weights = {}
        if algorithm == "Dijkstra":
            self.ecos_thread = threading.Thread(target=self.send_eco)
            self.ecos_thread.start()
            
    def __del__(self):
        return super().__del__()
    
    def send_routing_message(self, to, message_, from_="",  hops=-1, from_node=""):

        print()
        print(f"🌊 Send message to {to}")
        print()
        if from_ == "":
            from_ = f"{self.username}@{self.server}"
        # Find node name
        nodeName = ""
        for node in self.names:
            if self.names[node] == to:
                nodeName = node
                break
        
        # If node name is not found
        if not nodeName:
            print("Node not found")
            return
        
        # If the algorithm is Dijkstra
        if self.algorithm == "Dijkstra":
            self.table_with_weights = {}


            # Create the graph
            graph = {}
            for node in self.table_weights:
                graph[node] = {}
                graph[node] = self.table_weights[node]["table"]

            for node in self.topology:
                if node not in graph or graph.get(node, None) is None:
                    graph[node] = {n: float("inf") for n in self.topology[node]}
                for neighbor in self.topology[node]:
                    if neighbor not in graph[node]:
                        graph[node][neighbor] = float("inf")

            # Comprobate if graph is correct
            for node in graph:
                for neighbor in graph[node]:
                    try:
                        float(graph[node][neighbor])
                    except:
                        graph[node][neighbor] = float("inf")


            # Run the Dijkstra algorithm
            print()
            print(f"🟢  DIJKSTRA //////////////////////////////////////////")
            print("Graph:")
            print(tabulate(graph.items(), headers=["Node", "Weights"], tablefmt="fancy_grid"))
            print()
            routing_table = Dijkstra(graph, self.actual_node, from_node )
            print(routing_table)
            if routing_table.get(nodeName, None) is None:
                print(f"Node {nodeName} is not reachable")
                return
            
            weight = routing_table[nodeName][0]
            if weight == 0:
                print("Node is not accessible")
                return

            next_node = routing_table[nodeName][1][1]

            # Find if next node is in new neighbors
            if next_node not in self.neighbors or next_node == self.actual_node:
                print("Not exist path to the node")
                return

            # Verify if the next node is the destination
            if next_node == nodeName:
                print(f"Send message to {nodeName}")
                message = {
                    "type": "message",
                    "from": from_,
                    "data": message_,
                }
                self.table_message(to, message)
                return
            
            # Veify if hops are over
            if hops <= 0:
                print("Hops are over")
                return
            
            # Create the message
            message = {
                "type": "send_routing",
                "to": to,
                "from": from_,
                "data": message_,
                "hops": hops - 1
            }
            to_ = self.names[next_node]
            # Find the path to the node more close
            self.table_message(to_, message)
        elif self.algorithm == "Flooding":
            # Verify if to is in the neighbors
            if to in self.neighbors.values():
                message = {
                    "type": "message",
                    "from": from_,
                    "data": message_
                }
                self.table_message(to, message)
            else:
                if hops <= 0:
                    print("Hops are over")
                    return

                message = {
                    "type": "send_routing",
                    "to": to,
                    "from": from_,
                    "data": message_,
                    "hops": hops - 1
                }
                # Send the message to all neighbors
                for neighbor in self.neighbors:
                    if self.neighbors[neighbor] == from_:
                        continue
                    self.table_message(self.neighbors[neighbor], message)
    
    def load_config(self):
        with open(self.namesfile, "r") as f:
            content = f.read()
            content = content.replace("'", "\"")
            self.names = json.loads(content)
            self.names: Dict[str, str] = self.names.get("config", {})
            
        with open(self.topologyfile, "r") as s:
            content = s.read()
            content = content.replace("'", "\"")
            self.topology = json.loads(content)    
            self.topology: Dict[str, str] = self.topology.get("config", {})

        # Find the name from the actual node
        for node in self.names:
            print(node, self.names[node], f"{self.username}@{self.server}")
            if self.names[node] == f"{self.username}@{self.server}":
                self.actual_node = node
                break
        print(self.actual_node)

        # Find the neighbors on the topology
        self.neighbors = {node: self.names[node]  for node in self.topology[self.actual_node]}
        for neighbor in self.neighbors:
            self.neighbors[neighbor] = self.names[neighbor]
        print(tabulate(self.names.items(), headers=["Node", "Name"]))
        print()
        print(tabulate(self.topology.items(), headers=["Node", "Connections"]))    
        print()
        print(tabulate(self.neighbors.items(), headers=["Node", "Name"]))

    
    async def listen_xmpp(self):
        while hasattr(self, "running"):
            response = b''
            json_response = {}
            while hasattr(self, "running"):
                response += self.ssl_sock.recv(4096)
                try:
                    json_response = parseXMLTOJSON(response)
                    break
                except:
                    continue


            for event in json_response:
                handler = self.events_handlers.get(event, None)
                if handler:
                    await handler(json_response[event])
                else:
                    print("Unknown event: ", event)

    def send_eco(self, interval=30):

        while True:
            # Send an eco message to all neighbors
            for name, neighbor in self.neighbors.items():
                message = {
                    "type": "echo"
                }
                self.on_eco[name] = time.perf_counter()
                print(f"😿Send eco to {name}")
                self.table_message(neighbor, message)
            time.sleep(interval)
        

    async def message(self, data):
        content = data.get("body", None)
        from_ = data.get("@from", None)
        if from_:
            from_ = from_.split("/")[0]
        if content:
            await self.process_message(data["body"], from_)

    async def process_message(self, data, from_):
        # try to convert the data to a json
        try:
            data = data.replace("'", "\"")
            data = json.loads(data)
        except:
            pass

        type_ = data.get("type", None)
        if type_ == "connect":
            self.neighbors[from_] = data.get("data", None)
        elif type_ == "echo":
            response = {
                "type": "echo_response"
            }
            print()
            print(f"🦜 Send Echo_response to {from_}")
            print()
            self.table_message(from_, response)

        elif type_ == "echo_response":
            print(f"Node {from_} is alive")
            nodeName = ""
            for node in self.names:
                if self.names[node] == from_:
                    nodeName = node
                    break

            last_weight = self.table_with_weights.get(nodeName, None)
            total_weight = time.perf_counter() - self.on_eco[nodeName]
            if last_weight:
                self.table_with_weights[nodeName] = (total_weight + last_weight) / 2
            else:
                self.table_with_weights[nodeName] = total_weight
            self.table_version += 1
            print()
            print(tabulate(self.table_with_weights.items(), headers=["Node", "Weight"], tablefmt="fancy_grid"))
            print()
            self.table_weights[self.actual_node] = {
                "version": self.table_version,
                "table": self.table_with_weights
            }
            to_send = {
                "type": "weights",
                "table": self.table_with_weights,
                "version": self.table_version,
                "from": f"{self.username}@{self.server}"
            }
            await self.send_to_neighbors(to_send, exclude=[])

        elif type_ == "weights":
            print()
            print("🔫", from_)
            print()
            nodeName = ""
            from_table = data.get("from", None)
            if not from_table:
                pass

            for node in self.names:
                if self.names[node].split('@')[0] == from_table.split('@')[0]:
                    nodeName = node
                    break
            
            if self.table_weights.get(nodeName, {}).get("version", 0) < data.get("version", 0):
                new_table = {}
                new_table["table"] = data.get("table", {})
                new_table["version"] = data.get("version", 0)
                self.table_weights[nodeName] = new_table
                print()
                # Print all table weights
                for node in self.table_weights:
                    print(f"Node: {node}")
                    print(tabulate(self.table_weights[node].get("table", {}).items(), headers=["Node", "Weight"], tablefmt="fancy_grid"))
                    print()
                print()

                await self.send_to_neighbors(data, exclude=[])

        elif type_ == "send_routing":
            message = data.get("data", {})
            to__ = data.get("to", "")
            hops = data.get("hops", -1)
            print()
            print(f"🟢 Message from {from_} to {to__}: {message}")
            print()
            self.send_routing_message(data.get("to", ""), message, from_=data.get("from", ""), hops=hops)

        elif type_ == "message":
            message = data.get("data", {})
            from__ = data.get("from", "")
            print()
            print(f"🎵 Message from {from__}: {message}")
            print()
            
            
    
    async def send_to_neighbors(self, data, exclude=[]):
        for name, neighbor in self.neighbors.items():
            if neighbor not in exclude:
                self.table_message(neighbor, data)
        

    def table_message(self, to, data):
        to_ = to.split("@")[0]
        data_json = json.dumps(data)
        self.send_chat_message(message=data_json, to=to_, type="chat")

    async def run(self):
        await self.listen_xmpp()
        while hasattr(self, "running"):
            await asyncio.sleep(1)
            pass
    
    def stop(self):
        self.__del__()


def runRouter(router):
    asyncio.run(router.run())

if __name__ == "__main__":
    # Read 
    router = Table_Manager("val21240-node1", "PSSWD", "names2024-randomX-2024.txt", "topo2024-randomX-2024.txt")
    import threading
    thread = threading.Thread(target=runRouter, args=(router,))
    thread.start()
    import tkinter as tk
    from tkinter import scrolledtext
    import threading
    import time

    # Función que se ejecuta en un hilo y envía mensajes
    def sendersas():
        name = name_entry.get()
        message = message_entry.get()
        
        if not name or not message:
            text_area.insert(tk.END, "Name and message cannot be empty.\n")
            return
        
        # Enviar mensaje usando el router global
        router.send_routing_message(name, message, hops=len(router.names))
        
        # Enviar un mensaje a la cola para actualizar la interfaz de usuario
        text_area.insert(tk.END, f"Message sent to {name}: {message}\n")
        text_area.yview(tk.END)  # Desplazar hacia abajo

    # Función para iniciar el hilo de envío de mensajes
    def start_sendersas():
        threading.Thread(target=sendersas).start()

    # Crear la ventana principal
    root = tk.Tk()
    root.title("Message Sender")

    # Crear un área de texto para mostrar los mensajes
    text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=10, width=50)
    text_area.pack(padx=10, pady=10)

    # Crear campos de entrada para el nombre y el mensaje
    tk.Label(root, text="Name:").pack(padx=10, pady=5)
    name_entry = tk.Entry(root, width=50)
    name_entry.pack(padx=10, pady=5)

    tk.Label(root, text="Message:").pack(padx=10, pady=5)
    message_entry = tk.Entry(root, width=50)
    message_entry.pack(padx=10, pady=5)

    # Crear un botón para iniciar el envío de mensajes
    send_button = tk.Button(root, text="Send Message", command=start_sendersas)
    send_button.pack(pady=10)

    # Iniciar el bucle principal de la interfaz de usuario
    root.mainloop()






