from vec2d import Vec2d
from socket import socket as Socket
from instruction import Instruction
import socket

class Player:
    def __init__(self, faction, port):
        self.name = None
        self.color = (0, 0, 0, 0xff)
        self.faction = faction
        self.ships = []
        self.resources = []
        self.isConnected = False
        self.instructions = []

        #TODO: init socket
        server = Socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('', port))
        server.listen(1)
        server.settimeout(0.0)
        self.server = server

    def fetch_instruction(self):
        # fetch one instruction in the instruction queue
        if self.instructions:
            return self.instructions.pop(0)
        else:
            return None

    def recieve_instructions(self):
        # recieve all instructions sent by the AI
        pass

    def connect(self):
        # try to connect, return True if success
        # DUMMY XXX
        return True
        try:
            client, addr = self.server.accept()
            client.settimeout(0.0)
            self.client = client
            self.addr = addr
            self.rfile = self.server.makefile('r')
            self.wfile = self.server.makefile('w')
        except socket.error:
            return False
        return True

    def iteration(self, shippo):
        pass

    def send_instruction(self):
        # call the AI's iteration
        pass
