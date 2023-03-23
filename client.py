import os
import time
from socket import *
import threading
import json
from time import sleep


class Client:
    def __init__(self, username, server_ip, server_port, client_port):
        # attributes
        self.clients = {}
        self.name = username
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_port = client_port
        self.normal_mode = True
        self.group_name = None
        self.chat_waiting = None
        self.private_message = {}

        self.send_request_ack = False
        self.dereg_request_no = 0
        self.dereg_request_ack = False
        self.create_group_request_no = 0
        self.create_group_request_ack = False
        self.list_groups_request_no = 0
        self.list_groups_request_ack = False
        self.join_group_request_no = 0
        self.join_group_request_ack = False
        self.list_members_request_no = 0
        self.list_members_request_ack = False
        self.leave_group_request_no = 0
        self.leave_group_request_ack = False
        self.send_group_request_no = 0
        self.send_group_request_ack = False


        # open socket & register with server
        self.client_socket = socket(AF_INET, SOCK_DGRAM)
        to_send = "register" + "\n" + self.name
        self.client_socket.sendto(to_send.encode(), (self.server_ip, self.server_port))

        # multi-threading
        listen_thread = threading.Thread(target=self.listen)
        listen_thread.start()
        cmd_thread = threading.Thread(target=self.cmd_process)
        cmd_thread.start()

    # listen for incoming msg
    def listen(self):
        while True:
            buf, sender_address = self.client_socket.recvfrom(4096)
            buf = buf.decode()
            lines = buf.splitlines()
            header = lines[0]

            if header == "register":
                print(">>> [Welcome, You are registered.]")

            if header == "updateinfo":
                self.clients = json.loads(lines[1])
                # print(self.clients)
                print(">>> [Client table updated.]")

            if header == "nameexists":
                # sys.exist("client name exists. please try a different name")
                # os._exit(1) only exits child process, not affecting the main process
                print(">>> [Client name exists. please try a different name.]")
                os._exit(1)

            if header == "deregister":
                self.dereg_request_ack = True
                print(">>> [You are Offline. Bye.]")
                os._exit(1)

            if header == "send":
                sender_name = lines[1]
                message = lines[2]
                if self.normal_mode:
                    print(">>> " + sender_name + ": " + message)
                else:
                    if sender_name not in self.private_message:
                        self.private_message[sender_name] = [message]
                    else:
                        self.private_message[sender_name].append(message)
                to_send = "receive" + "\n" + self.name
                self.client_socket.sendto(to_send.encode(), sender_address)

            if header == "receive":
                receiver_name = lines[1]
                if self.chat_waiting == receiver_name:
                    self.send_request_ack = True
                    print(f">>> [Message received by {receiver_name}.]")

            if header == "groupexists":
                self.create_group_request_ack = True
                group_name = lines[1]
                print(f">>> [Group {group_name} already exists.]")

            if header == "create":
                self.create_group_request_ack = True
                group_name = lines[1]
                print(f">>> [Group {group_name} created by Server.]")

            if header == "list":
                self.list_groups_request_ack = True
                print(">>> [Available group chats:]")
                for n in lines[1:]:
                    print(">>> " + n)

            if header == "groupnotexists":
                self.join_group_request_ack = True
                group_name = lines[1]
                print(f">>> [Group {group_name} does not exist]")

            if header == "join":
                self.join_group_request_ack = True
                self.normal_mode = False
                group_name = lines[1]
                self.group_name = group_name
                print(f">>> [Entered group {group_name} successfully]")

            if header == "listmembers":
                self.list_members_request_ack = True
                group_name = lines[1]
                print(f">>> ({group_name}) [Members in the group {group_name}:]")
                for n in lines[2:]:
                    print(f">>> ({group_name}) {n}")

            if header == "leave":
                self.leave_group_request_ack = True
                print(f">>> [Leave group chat {self.group_name}]")
                self.group_name = None
                self.normal_mode = True
                # print message in self.private_message
                for sender_name in self.private_message:
                    message_l = self.private_message[sender_name]
                    for m in message_l:
                        print(">>> " + sender_name + ": " + m)
                self.private_message = {}

            if header == "serverreceived":
                self.send_group_request_ack = True
                print(f">>> ({self.group_name}) [Message received by Server.]")

            if header == "groupmessage":
                sender_name = lines[1]
                message = lines[2]
                # display
                print(f">>> ({self.group_name}) Group_Message {sender_name}: {message}")
                # send ack back
                to_send = "receivegroup" + "\n" + self.name
                self.client_socket.sendto(to_send.encode(), (self.server_ip, self.server_port))

    def cmd_process(self):
        while True:
            time.sleep(0.5)
            try:
                if self.normal_mode:
                    cmd = input(">>> ")
                else:
                    cmd = input(">>> (" + self.group_name + ") ")
            except KeyboardInterrupt:
                os._exit(1)
            cmd = cmd.split()

            if cmd[0] == "send":
                if len(cmd) < 3:
                    print(">>> [Invalid command]")
                elif cmd[1] not in self.clients:
                    print(">>> [Invalid client name.]")
                # elif cmd[1] == self.name:
                #     print(">>> [Cannot send message to oneself.]")
                # check client online or not:
                elif not self.clients[cmd[1]][2]:
                    print(">>> [Client not online. Try others.]")
                elif not self.normal_mode:
                    print(f">>> ({self.group_name}) [Invalid command]")
                else:
                    # wait for an ack from the client within 500 msecs ->
                    # no ack: notify the server that the recipient client is offline, both update tables
                    self.send_request_ack = False
                    message = " ".join(cmd[2:])
                    to_send = "send" + "\n" + self.name + "\n" + message
                    receiver_name = cmd[1]
                    self.chat_waiting = receiver_name
                    receiver_port, receiver_ip, status = self.clients[receiver_name]
                    self.client_socket.sendto(to_send.encode(), (receiver_ip, receiver_port))
                    sleep(0.5)

                    if not self.send_request_ack:
                        print(f">>> [No ACK from {receiver_name}, message not delivered]")
                        to_send = "offline" + "\n" + receiver_name
                        self.client_socket.sendto(to_send.encode(), (self.server_ip, self.server_port))

            elif cmd[0] == "dereg":
                if len(cmd) != 2:
                    print(">>> [Invalid command]")
                elif cmd[1] != self.name:
                    print(">>> [Invalid client name.]")
                else:
                    # wait for an ack from the server within 500 msecs -> no ack: retry for 5 time
                    self.dereg_request_ack = False
                    self.dereg_request_no = 0
                    while self.dereg_request_no < 5 and not self.dereg_request_ack:
                        to_send = "deregister" + "\n" + self.name
                        self.client_socket.sendto(to_send.encode(), (self.server_ip, self.server_port))
                        self.dereg_request_no += 1
                        sleep(0.5)

                    if not self.dereg_request_ack:
                        print(">>> [Server not responding]")
                        print(">>> [Exiting]")
                        os._exit(1)

            elif cmd[0] == "create_group":
                if not self.normal_mode:
                    print(f">>> ({self.group_name}) [Invalid command]")
                elif len(cmd) != 2:
                    print(">>> [Invalid command]")
                else:
                    group_name = cmd[1]
                    # wait for an ack from the server within 500 msecs -> no ack: retry for 5 time
                    self.create_group_request_ack = False
                    self.create_group_request_no = 0
                    while self.create_group_request_no < 5 and not self.create_group_request_ack:
                        to_send = "create" + "\n" + group_name + "\n" + self.name
                        self.client_socket.sendto(to_send.encode(), (self.server_ip, self.server_port))
                        self.create_group_request_no += 1
                        sleep(0.5)

                    if not self.create_group_request_ack:
                        print(">>> [Server not responding]")
                        print(">>> [Exiting]")
                        os._exit(1)

            elif cmd[0] == "list_groups":
                if len(cmd) != 1:
                    print(">>> [Invalid command]")
                elif not self.normal_mode:
                    print(f">>> ({self.group_name}) [Invalid command]")
                else:
                    # wait for an ack from the server within 500 msecs -> no ack: retry for 5 time
                    self.list_groups_request_ack = False
                    self.list_groups_request_no = 0
                    while self.list_groups_request_no < 5 and not self.list_groups_request_ack:
                        to_send = "listgroups" + "\n" + self.name
                        self.client_socket.sendto(to_send.encode(), (self.server_ip, self.server_port))
                        self.list_groups_request_no += 1
                        sleep(0.5)

                    if not self.list_groups_request_ack:
                        print(">>> [Server not responding]")
                        print(">>> [Exiting]")
                        os._exit(1)

            elif cmd[0] == "join_group":
                if not self.normal_mode:
                    print(f">>> ({self.group_name}) [Invalid command]")
                elif len(cmd) != 2:
                    print(">>> [Invalid command]")
                else:
                    group_name = cmd[1]
                    # wait for an ack from the server within 500 msecs -> no ack: retry for 5 time
                    self.join_group_request_ack = False
                    self.join_group_request_no = 0
                    while self.join_group_request_no < 5 and not self.join_group_request_ack:
                        to_send = "join" + "\n" + group_name + "\n" + self.name
                        self.client_socket.sendto(to_send.encode(), (self.server_ip, self.server_port))
                        self.join_group_request_no += 1
                        sleep(0.5)

                    if not self.join_group_request_ack:
                        print(">>> [Server not responding]")
                        print(">>> [Exiting]")
                        os._exit(1)

            elif cmd[0] == "list_members":
                if self.normal_mode:
                    print(">>> [Invalid command]")
                elif len(cmd) != 1:
                    print(">>> [Invalid command.]")
                else:
                    # wait for an ack from the server within 500 msecs -> no ack: retry for 5 time
                    self.list_members_request_ack = False
                    self.list_members_request_no = 0
                    while self.list_members_request_no < 5 and not self.list_members_request_ack:
                        to_send = "listmembers" + "\n" + self.group_name + "\n" + self.name
                        self.client_socket.sendto(to_send.encode(), (self.server_ip, self.server_port))
                        self.list_members_request_no += 1
                        sleep(0.5)

                    if not self.list_members_request_ack:
                        print(f">>> ({self.group_name}) [Server not responding]")
                        print(f">>> ({self.group_name}) [Exiting]")
                        os._exit(1)

            elif cmd[0] == "leave_group":
                if self.normal_mode:
                    print(">>> [Invalid command]")
                elif len(cmd) != 1:
                    print(">>> [Invalid command.]")
                else:
                    # wait for an ack from the server within 500 msecs -> no ack: retry for 5 time
                    self.leave_group_request_ack = False
                    self.leave_group_request_no = 0
                    while self.leave_group_request_no < 5 and not self.leave_group_request_ack:
                        to_send = "leave" + "\n" + self.group_name + "\n" + self.name
                        self.client_socket.sendto(to_send.encode(), (self.server_ip, self.server_port))
                        self.leave_group_request_no += 1
                        sleep(0.5)

                    if not self.leave_group_request_ack:
                        print(f">>> ({self.group_name}) [Server not responding]")
                        print(f">>> ({self.group_name}) [Exiting]")
                        os._exit(1)

            elif cmd[0] == "send_group":
                if self.normal_mode:
                    print(">>> [Invalid command]")
                elif len(cmd) < 2:
                    print(">>> [Invalid command.]")
                else:
                    message = " ".join(cmd[1:])
                    # wait for an ack from the server within 500 msecs -> no ack: retry for 5 time
                    self.send_group_request_ack = False
                    self.send_group_request_no = 0
                    while self.send_group_request_no < 5 and not self.send_group_request_ack:
                        to_send = "sendgroup" + "\n" + self.group_name + "\n" + self.name + "\n" + message
                        self.client_socket.sendto(to_send.encode(), (self.server_ip, self.server_port))
                        self.send_group_request_no += 1
                        sleep(0.5)

                    if not self.send_group_request_ack:
                        print(f">>> ({self.group_name}) [Server not responding]")
                        print(f">>> ({self.group_name}) [Exiting]")
                        os._exit(1)

            else:
                if self.normal_mode:
                    print(">>> [Invalid command]")
                else:
                    print(f">>> ({self.group_name}) [Invalid command]")