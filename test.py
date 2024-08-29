from ManagerXMPP import ManagerXMPP, parseXMLTOJSON

client = ManagerXMPP("val21240-node4", "PSSWD")
client.register()
client.__del__()