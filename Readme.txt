Name: Ngoc Nguyen 
V#: V01109002

This is a README file for running the ChatServer.py and ChatClient.py scripts.

ChatServer.py
    The `ChatServer.py` script is a simple char server that receives chat requests from clients and sends back the corresponding response packets.

Usage
    To run the server, navigate to the directory where the `ChatServer.py` file is located and type the following command in the terminal:

    python ChatServer.py <port_number>

    Replace <port_number> with the desired port number (between 10000 - 11000).

Example
    python ChatServer.py 10001

ChatClient.py
    The `ChatClient.py` script is a client that sends chat requests to a server and receives the corresponding response packets.
    It can send and receive message between the clients in the same chat server.

Usage
    To run the client, nagivate to the directory where the ChatClient.py file is located and type the following command in the terminal:

    python ChatClient.py <hostname/ip> <port> <nickname> <clientID>

    Replace the arguments as follows:
        <hostname/ip>: the hostname or IP address of the server.
        <port>: The port number that the server is listening to.
        <nickname>: The nickname you would like to use to enter the chat. If this nickname is already in used, the program will prompt you to enter another nickname to use in the chat server.
        <clientID>: the ID of the client 
Example 
    python ChatClient.py 127.0.0.1 10001 Ngoc 001


    