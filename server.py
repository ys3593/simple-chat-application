from socket import *
import threading
import json
from time import sleep

class Server:
    def __init__(self, port):
        # attributes
        self.port = port
        # maintain table for client name (key), [ip, port, online-status]
        self.clients = {}
        # maintain table for group name (key), [group member names]
        self.group = {}
        self.client_ack = []

        # open socket & bind the server socket with ip and port
        self.server_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_socket.bind(('', port))

        # multi-threading
        server_listen = threading.Thread(target=self.listen)
        server_listen.start()

    # listen for incoming connections & msg
    def listen(self):
        while True:
            buf, sender_address = self.server_socket.recvfrom(4096)
            buf = buf.decode()
            lines = buf.splitlines()
            header = lines[0]

            if header == "register":
                self.register(lines[1], sender_address)

            if header == "deregister":
                self.deregister(lines[1], sender_address)

            if header == "offline":
                self.offline(lines[1])

            if header == "create":
                self.create_group(lines[1], lines[2], sender_address)

            if header == "listgroups":
                self.list_groups(lines[1], sender_address)

            if header == "join":
                self.join_group(lines[1], lines[2], sender_address)

            if header == "sendgroup":
                self.send_group(lines[1], lines[2], lines[3], sender_address)
                # group_name, client_name, message = lines[1], lines[2], lines[3]

            if header == "receivegroup":
                self.client_ack.remove(lines[1])

            if header == "listmembers":
                self.list_members(lines[1], lines[2], sender_address)

            if header == "leave":
                self.leave_group(lines[1], lines[2], sender_address)

    # accept client registrations, add info to table, print msg to terminal & broadcast
    # check name key exists or not
    def register(self, client_name, sender_address):
        client_ip, client_port = sender_address
        if client_name in self.clients:
            msg = "nameexists"
            self.server_socket.sendto(msg.encode(), (client_ip, client_port))
        else:
            self.clients[client_name] = [client_port, client_ip, True]
            msg = "register"
            self.server_socket.sendto(msg.encode(), (client_ip, client_port))
            self.broadcast()

    # deregister client
    def deregister(self, client_name, sender_address):
        client_ip, client_port = sender_address
        self.clients[client_name] = [client_port, client_ip, False]
        msg = "deregister"
        self.server_socket.sendto(msg.encode(), (client_ip, client_port))
        self.broadcast()

    # broadcast the complete table of active clients to all the online clients
    def broadcast(self):
        for name in self.clients:
            client_port, client_ip, online_status = self.clients[name]
            if online_status:
                msg = "updateinfo" + "\n"
                msg += json.dumps(self.clients)
                self.server_socket.sendto(msg.encode(), (client_ip, client_port))

    def offline(self, offline_client_name):
        offline_client_name_port, offline_client_name_ip, offline_client_status = self.clients[offline_client_name]
        self.clients[offline_client_name] = [offline_client_name_port, offline_client_name_ip, False]
        self.broadcast()

    # group related operations
    def create_group(self, group_name, client_name, sender_address):
        if group_name in self.group:
            print(f">>> [Client {client_name} creating group {group_name} failed, group already exists]")
            msg = "groupexists" + "\n" + group_name
            self.server_socket.sendto(msg.encode(), sender_address)
        else:
            print(f">>> [Client {client_name} created group {group_name} successfully]")
            self.group[group_name] = []
            print(self.group)
            msg = "create" + "\n" + group_name
            self.server_socket.sendto(msg.encode(), sender_address)

    def list_groups(self, client_name, sender_address):
        print(f">>> [Client {client_name} requested listing groups, current groups:]")
        msg = "list"
        for group_name in self.group.keys():
            print(">>> " + group_name)
            msg += "\n" + group_name
        self.server_socket.sendto(msg.encode(), sender_address)

    def join_group(self, group_name, client_name, sender_address):
        if group_name not in self.group:
            print(f">>> [Client {client_name} joining group {group_name} failed, group does not exist]")
            msg = "groupnotexists" + "\n" + group_name
            self.server_socket.sendto(msg.encode(), sender_address)
        else:
            print(f">>> [Client {client_name} joined group {group_name}]")
            self.group[group_name].append(client_name)
            print(self.group)
            msg = "join" + "\n" + group_name
            self.server_socket.sendto(msg.encode(), sender_address)

    def send_group(self, group_name, client_name, message, sender_address):
        print(f">>> [Client {client_name} sent group message: {message}]")
        print(self.group)
        # send ack back to the sender
        msg = "serverreceived"
        self.server_socket.sendto(msg.encode(), sender_address)
        # broadcast message except the sender
        self.client_ack = []
        for member_name in self.group[group_name]:
            client_port, client_ip, online_status = self.clients[member_name]
            if online_status and member_name != client_name:
                self.client_ack.append(member_name)
                msg = "groupmessage" + "\n" + client_name + "\n" + message
                self.server_socket.sendto(msg.encode(), (client_ip, client_port))

        server_wait = threading.Thread(target=self.wait_ack, args=(group_name,))
        server_wait.start()

    def wait_ack(self, group_name):
        sleep(0.5)

        for member_name in self.client_ack:
            print(f">>> [Client {member_name} not responsive, removed from group {group_name}]")
            self.group[group_name].remove(member_name)
            self.client_ack.remove(member_name)

    def list_members(self, group_name, client_name, sender_address):
        print(f">>> [Client {client_name} requested listing members of group {group_name}]")
        msg = "listmembers" + "\n" + group_name
        for member_name in self.group[group_name]:
            print(">>> " + member_name)
            msg += "\n" + member_name
        self.server_socket.sendto(msg.encode(), sender_address)

    def leave_group(self, group_name, client_name, sender_address):
        print(f">>> [Client {client_name} left group {group_name}]")
        self.group[group_name].remove(client_name)
        print(self.group)
        msg = "leave"
        self.server_socket.sendto(msg.encode(), sender_address)


