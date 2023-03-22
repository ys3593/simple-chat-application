# CSEE 4119 Programming Assignment 1: Simple Chat Application

Done by: Yaochen Shen (ys3593)

Directory:
----
- README.md
- ChatApp.py
- server.py
- client.py

Commands for Running the Program
------

### Initiate the Server Process:  
```
python ChatApp.py -s <port> 
```
Example:
```
python ChatApp.py -s 1025 
```

### Initiate the Client Process: 
```
python ChatApp.py -c <name> <server-ip> <server-port> <client-port>
```
Example:
```
python ChatApp.py -c yao localhost 1025 2000 
```

### Client Commands:
#### Normal Mode
__Send:__ current client sends the message to the appropriate client.
```
send <appropriate-client-name> <message>
```
__Dereg:__ the current client sends de-registration request to the server to go offline.
```
dereg <current-clinet-name>
```
__Create Group:__ the current client sends a request to the server to create a new group chat.
```
create_group <group-name>
```
__List Groups:__ the current client sends a request to the server to list all group chats.
```
list_groups
```
__Join Group:__ the current client sends a request to the server to join the group chat.
```
join_group <group-name>
```

#### Group Chat Mode
__Send Group:__  the client can send the message in the group chat
```
send_group <message>
```
__List Members:__ the client in group chat mode can list all members in the current group
```
list_members
```
__Leave Group:__  the client can leave the group chat back to the normal chat mode.
```
leave_group
```
__Dereg:__ the current client sends de-registration request to the server to go offline.
```
dereg <current-clinet-name>
```

Project Documentation
------
Simple Chat Application implements a simple chat application in Python 3 with various 
clients and a server using UDP. The program has two modes of operation, 
one is the client, and the other is the server. The client instances 
communicate directly with each other. And the server instance is used to set up 
clients and for book-keeping purposes. The server also broadcasts
channel messages to clients in the group chat.

### Server Class
The server class is used to create an instance that sets up 
clients, book-keeps information on clients and groups ,as well as 
broadcasts channel messages to clients in the group chat.
- Attributes
    - self.clients: a dictionary used to record the information of clients. The
  key is the name of the client and the value is a list that contains client's
  ip, client's port, and client's online-status (True for online, False for
  offline)
    - self.group: a dictionary used to record the information of groups. The
  key is the name of the client and the value is a list that contains clients
  in the group.
- Methods
    - listen(self):listen incoming messages and deal with different headers
    - register(self, client_name, sender_address): accept client registrations, 
  add client information to self.clients, and call broadcast(self) to broadcast
  the updated client information to all online clients.
    - deregister(self, client_name, sender_address): deregister the client, change
  the client online-status to offline in self.clients, and broadcast(self) to broadcast
  the updated client information to all online clients.
    - broadcast(self): broadcast the client information to all online clients
    - offline(self, offline_client_name): change
  the client online-status to offline in self.clients, and broadcast(self) to broadcast
  the updated client information to all online clients.
    - create_group(self, group_name, client_name, sender_address): create 
  an empty list as the value under the key group name in the self.group dictionary.
    - list_groups(self, client_name, sender_address): send the self.group information
  to the client.
    - join_group(self, group_name, client_name, sender_address): append client_name
  to the list  as the value under the key group name in the self.group dictionary.
    - send_group(self, group_name, client_name, message, sender_address): send the 
  group message to all clients (except the sender) in the group and start the 
  wait_ack thread.
    - wait_ack(self, group_name): wait for the ACK from all clients (except 
  the sender) in the group and remove the client from the group If the server does not receive an ack response from 
  a client within time limit.
    - list_members(self, group_name, client_name, sender_address): send
  the group member information to the client.
    - leave_group(self, group_name, client_name, sender_address): remove
  client from the group by updating the value in self.group corresponding to
  the group name.
- Threads
  - listen thread: thread to listen incoming messages
  - wait_ack thread: thread to wait for ACK from clients after they
  receive group messages
  
### Client Class
The client class is used to create an instance that communicates
directly with each other, requests group information, as well as 
send and receive group messages.
- Attributes
    - self.clients: a dictionary used to record the information of clients. The
  key is the name of the client and the value is a list that contains client's
  ip, client's port, and client's online-status (True for online, False for
  offline)
    - self.name: a string used to record the name of the client
    - self.server_ip: a string used to record the ip of the server 
    - self.server_port: an int used to record the port of the server
    - self.client_port: an int used to record the port of the client
    - self.normal_mode: a boolean used to record the mode of the client.
      (True for Normal Mode, False for Group Chat Mode)
    - self.group_name = a string used to record the name the client in.
  None if the client is in Normal Mode.
    - self.chat_waiting: a string used to record the name of the receiver
  that the client sends message to and waits for an ACK on.
    - self.private_message: a dictionary used to record the private message 
  the client receives during the Group Chat Mode. The key is the name of the 
  sender and the value is a list of private message the sender sends.
- Methods
    - listen(self): 
      - listen incoming messages and deal with different headers
  of messages with different actions
    - cmd_process(self): 
      - process input commands including 
  send, dereg, create_group, list_groups, join_group, list_members, leave_group
  and send_group. 
      - Invalid commands, non-existed commands or commands that do not fit in current mode
  are checked and suggested by printed line ">>> [Invalid command]"
  (Normal Mode) or ">>> (<group_name>) [Invalid command]"
  (Group Chat Mode)
- Threads
  - listen thread: thread to listen incoming messages
  - cmd_process thread: thread to process command line input










