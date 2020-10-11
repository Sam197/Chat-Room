import socket
import pickle
import select
import threading

HEADER_LENGTH = 10
IP = "192.168.1.105"
PORT = 1234
protocol = 'utf-8'
server_id = 1
server_password = "idk"

global running 
running = True

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))
server_socket.listen()

global sockets_list
sockets_list = [server_socket]

global clients
clients = {}

def recieve_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)

        if not len(message_header):
            return False

        message_length = message_header.decode(protocol)
        message_length.strip()
        message_length = int(message_length)
        #message_length = int(pickle.loads(message_header).strip())
        return client_socket.recv(message_length).decode(protocol)

    except:
        return False

def send_message_all(message, clients, active_socket):
    message_headder = f"{len(message):<{HEADER_LENGTH}}".encode(protocol)
    for client_socket in clients:
        if client_socket != active_socket:
            client_socket.send(message_headder + bytes(message, protocol))

def whisper(message, sender):
    username = ""
    message = message[3:]
    print(message)
    i = 0
    for x, char in enumerate(message):
        if char == " ":
            i = x + 1
            break
        username += char
    finmessage = ""
    for char in message[i:]: finmessage += char
    print(username)
    print(finmessage)
    message = f"{sender} Whispers: {finmessage}"
    print(message)
    try:
        userSocket = list(clients.keys())[list(clients.values()).index(username)]
        message_headder = f"{len(message):<{HEADER_LENGTH}}".encode(protocol)
        userSocket.send(message_headder + bytes(message, protocol))
        return True, None
    except:
        print(f"No user by the name '{username}'")
        return False, username


def get_command():
    global running, clients
    while running:
        command = input("")
        if command == "":
            continue
        if command == "Stop":
            print("Stopping")
            send_message_all(f"Server is closing", clients, None)
            running = False
        else:
            if command[0] == "m":
                message = ""
                for x, char in enumerate(command): 
                    if x <= 2:
                        continue
                    message += char
                send_message_all(f"Server: {message}", clients,  None)
            elif command[0] == "w":
                res, username = whisper(command, "Server")
                if not res:
                    print(f"No user by the name '{username}'")
            elif command[0:2] == "LU":
                users = ""
                for client_socket in clients: users += clients[client_socket] + ", "
                print(users[:-2])

def main():
    commandThread = threading.Thread(target= get_command)
    commandThread.start()

    while running:
        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
        if not running:
            break

        for active_socket in read_sockets:
            if active_socket == server_socket:
                client_socket, client_address = server_socket.accept()
                
                user = recieve_message(client_socket)

                if user is False:
                    continue

                sockets_list.append(client_socket)

                clients[client_socket] = user
                
                print(f"Accepted connection from {client_address[0]} : {client_address[1]}, username {user}")
                send_message_all(f"Server: {user} has joined the chat", clients, active_socket)
            
            else:

                message = recieve_message(active_socket)

                if message is False:
                    print(f"Closed connection from {clients[active_socket]}")
                    send_message_all(f"Server: {clients[active_socket]} has left the chat", clients, client_socket)

                    sockets_list.remove(active_socket)
                    del clients[active_socket]
                    continue

                print(f"Message from {clients[active_socket]} > {message}")
                if message[0] != "/":
                    send_message_all(f"{clients[active_socket]}> {message}", clients, active_socket)
                else:
                    if message[1] == "w":
                        print(message) 
                        res, username = whisper(message, clients[active_socket])
                        if not res:
                            message = f"Server: No user by the name '{username}'"
                            active_socket.send(f"{len(message):<{HEADER_LENGTH}}".encode(protocol) + bytes(message, protocol))
                    else:
                        message = f"Server: {message[:3]} is not a reconiged command"
                        active_socket.send(f"{len(message):<{HEADER_LENGTH}}".encode(protocol) + bytes(message, protocol))
                
if __name__ == "__main__":
    main()