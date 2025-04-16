## import resources ##
import sys
import socket
import threading
import datetime
import json

# initilization client to store connections with client's nickname
client ={}
#store client IDs with socket
client_id={}
#store client addresses with socket
client_addresses = {}
#lock for thread-safe operation
client_lock = threading.Lock()

def timestamp_formatting():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    if len(sys.argv) !=2:
        print("ERR - arg x")
        sys.exit(1)

    try:
        port = int(sys.argv[1])
        if port <= 0 or port >= 65525:
            print("ERR - arg x")
            sys.exit(1)
    except ValueError:
        print("ERR - arg x")
        sys.exit(1)

    #Create socket so that server can listen for clients
    host = '0.0.0.0'


    sever_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sever_socket.bind((host, port))
    #already tanken by another active socket
    except socket.error:
        print(f"ERR = cannot create ChatServer socket using port number{port}")
        sys.exit(1) 
    

    # listening for at most 5 clients
    sever_socket.listen(5)
    print(f"Server listening on {host}:{port}")

    try:
        #Main server loop, accepts and handle client connections
        while True:
            client_socket, addr = sever_socket.accept()
            client_addresses[client_socket] = addr
            print(f"Accepted connection from {client_addresses}")

            #Create new thread for every client that connected to the server.
            client_handler = threading.Thread(target= handle_client, args =(client_socket,))
            client_handler.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        sever_socket.close()

def broadcast_to_others(message, sender_nickname):
    #Broadcast message to all clients except for og sender
    broadcast_list = []
    
    with client_lock:
        for nickname, socket in client.items():
            if nickname != sender_nickname:
                try:
                    socket.sendall(json.dumps(message).encode('utf-8'))
                    broadcast_list.append(nickname)
                except:
                    pass

    if broadcast_list:
        print(f"Broadcasted: {', '.join(broadcast_list)}")
    
#Handles sending and receiving message between client and server
def handle_client(client_socket):
    nickname = None
    client_id_val = None

    try:
        while True:
            data = client_socket.recv(4096)
            if not data:
                break
            try:
                message = json.loads(data.decode('utf-8'))
                message_type = message.get("type") #extract message type

                if message_type == "nickname":
                    nickname = message.get("nickname")
                    client_id_val = message.get("clientID")

                    with client_lock:
                        #Check if nickname is already in use
                        if nickname in client:
                            error_msg = {
                                "type": "error",
                                "message": "Nickname is already in use. Please choose a different one."
                            }
                            client_socket.sendall(json.dumps(error_msg).encode('utf-8'))
                            continue
                        client[nickname] = client_socket
                        client_id[client_socket] = client_id_val

                        timestamp = timestamp_formatting()
                        print(f"{timestamp} :: {nickname} : connected.")
                elif message_type == "message" and nickname:
                    sender_nickname = message.get("nickname")
                    msg_content = message.get("message")
                    timestamp = message.get("timestamp")

                    #verify if sender nickname match registered nickname
                    if sender_nickname != nickname:
                        continue

                    if client_socket in client_addresses:
                        client_address = client_addresses[client_socket]
                        client_ip = client_address[0]
                        client_port = client_address[1]
                    else:
                        client_ip = "unknown"
                        client_port = "unknown"
                    msg_size = len(data)

                    print(f"Received: IP:{client_ip}, Port:{client_port}, Client-Nickname:{nickname}, "
                          f"ClientID:{client_id}, Data/TIme:{timestamp_formatting()}, Msg-Size: {msg_size}")
                    
                    broadcast_msg = {
                        "type": "broadcast",
                        "nickname": nickname,
                        "message": msg_content,
                        "timestamp": timestamp
                    }

                    broadcast_to_others(broadcast_msg, nickname)

                elif message_type == "disconnect" and nickname:
                    break

            except json.JSONDecodeError:
                print(f"Received invalid JSON from client: {data.decode('utf-8')}")
        
    except Exception as e:
        print(f"Error handling client: {e}")

    finally:
        #clean up when client disconnect from server
        if nickname:
            with client_lock:
                if nickname in client:
                    del client[nickname]
                if client_socket in client_id:
                    del client_id[client_socket]
                if client_socket in client_addresses:
                    del client_addresses[client_socket]

                timestamp = timestamp_formatting()
                print(f"{timestamp} :: {nickname}: disconnected.")

            client_socket.close()

if __name__ == '__main__':
    main()
