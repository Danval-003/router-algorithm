from ManagerXMPP import ManagerXMPP, parseXMLTOJSON

class Node_Manager(ManagerXMPP):
    def __init__(self, jid, password):
        ManagerXMPP.__init__(self, jid, password)
        self.init_session()
        self.events_handlers = {
            "message": self.message,
        }
    
    def __del__(self):
        return super().__del__()
    
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

    async def message(self, data):
        content = data.get("body", None)
        if content:
            await self.process_message(data["body"])

    async def process_message(self, data):
        print(data)

