import sys
import socket
import json
import datetime
import threading

msgs_sent = 0
msgs_rcvd = 0
chars_sent = 0
chars_rcvd = 0

def format_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def listen_for_messages(socket, nickname):
    global msgs_rcvd, chars_rcvd
    
    try:
        while True:
            data = socket.recv(4096) 
            if not data:
            
                break
                
            response = data.decode('utf-8') 
            try:
                message_dict = json.loads(response)
                
                if message_dict.get("type") == "error":
                    print(f"Server error: {message_dict.get('message')}")
                elif message_dict.get("type") == "broadcast":
                    # Handle broadcast messages from other clients
                    timestamp = message_dict.get("timestamp", "unknown")
                    sender = message_dict.get("nickname", "unknown")
                    msg = message_dict.get("message", "")
                    print(f"{timestamp} :: {sender}: {msg}")
                    msgs_rcvd += 1
                    chars_rcvd += len(response)
            except json.JSONDecodeError:
                print(f"Received non-JSON message: {response}")
                #Count received messages
                msgs_rcvd += 1
                chars_rcvd += len(response)
    except Exception as e:
        # Handle any errors in the listener thread
        print(f"Error in listener thread: {e}")

def send_message(socket, message_dict):
    global msgs_sent, chars_sent
    
    message_json = json.dumps(message_dict)
    socket.sendall(message_json.encode('utf-8'))
    
    msgs_sent += 1
    chars_sent += len(message_json)

def main():
    if len(sys.argv) != 5:
        for i in range(1, 5):
            if i >= len(sys.argv):
                print(f"ERR - arg {i}")
                sys.exit(1)
    
    ip = sys.argv[1] 
    try:
        port = int(sys.argv[2]) 
    except ValueError:
        print("ERR - arg 2")  # Error if port is not an integer
        sys.exit(1)
    
    nickname = sys.argv[3]
    client_id = sys.argv[4]
    
    start_time = datetime.datetime.now()
    
    print(f"ChatClient started with server IP: {ip}, port: {port}, nickname: {nickname}, client ID: {client_id}, Date/Time: {format_timestamp()}")
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((ip, port))
        
        initial_msg = {
            "type": "nickname", 
            "nickname": nickname, 
            "clientID": client_id,
            "timestamp": format_timestamp() 
        }
        send_message(client_socket, initial_msg) 
        
        # Allows simultaneous sending and receiving of messages
        listener_thread = threading.Thread(
            target=listen_for_messages,
            args=(client_socket, nickname)
        )
        listener_thread.daemon = True  
        listener_thread.start() 
        
        while True:
            user_input = input("Enter message (or 'disconnect' to exit): ")
    
            # Handle disconnect command
            if user_input.lower() == "disconnect":
                disconnect_msg = {
                    "type": "disconnect", 
                    "nickname": nickname,  
                    "clientID": client_id  
                }
                send_message(client_socket, disconnect_msg) 
                break  
            
            chat_msg = {
                "type": "message", 
                "nickname": nickname, 
                "message": user_input, 
                "timestamp": format_timestamp() 
            }
            send_message(client_socket, chat_msg) 
    
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up 
        client_socket.close() 
        end_time = datetime.datetime.now() 

        print(f"Summary: start:{start_time.strftime('%Y-%m-%d %H:%M:%S')}, "
              f"end:{end_time.strftime('%Y-%m-%d %H:%M:%S')}, "
              f"msg sent:{msgs_sent}, msg rcv:{msgs_rcvd}, "
              f"char sent:{chars_sent}, char rcv:{chars_rcvd}")

if __name__ == '__main__':
    main()  