import socket
import sys
from _thread import start_new_thread

# Define a simple user (this will be a hardcoded username/password for simplicity)
VALID_USER = "exfil"
VALID_PASSWORD = "password123"  # The valid password for testing purposes

# Function to handle client connections
def clientthread(conn):
    try:
        # Send a basic POP3 greeting message
        conn.send(b"+OK POP3 server ready\r\n")

        # Receive the USER command
        data = conn.recv(1024)  # Receive the 'USER' command
        if data.startswith(b"USER"):
            username = data.decode().strip().split(" ")[1]
            print(f"Received USER: {username}")

            if username == VALID_USER:
                conn.send(b"+OK password required for user exfil\r\n")  # Inform the client that password is needed
            else:
                conn.send(b"-ERR Invalid user\r\n")  # Invalid user response
                conn.close()
                return

        # Receive the PASS command
        data = conn.recv(1024)  # Receive the 'PASS' command
        if data.startswith(b"PASS"):
            password = data.decode().strip().split(" ")[1]
            print(f"Received PASS: {password}")

            if password == VALID_PASSWORD:
                conn.send(b"+OK POP3 authentication succeeded\r\n")  # Successful authentication
            else:
                conn.send(b"-ERR Authentication failed\r\n")  # Failed password
                conn.close()
                return

        # After authentication (or failure), handle further commands or close the connection
        data = conn.recv(1024)  # Read further commands (this is a simple example, we won't process them)
        if data:
            print(f"Received: {data.decode()}")

        # Close the connection after handling it
        conn.close()

    except Exception as e:
        print(f"Error handling client: {e}")
        conn.close()

# Create and bind a socket to listen for incoming POP3 connections
def open_socket():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind to localhost and port 110 (standard POP3 port)
    server_socket.bind(("0.0.0.0", 110))  # Bind to all IP addresses on port 110
    server_socket.listen(5)  # Listen for incoming connections

    return server_socket

# Main server loop
sockObj = open_socket()

while True:
    try:
        # Accept incoming connections
        conn, address = sockObj.accept()
        print(f"[+] Received a connection from {address[0]}:{address[1]}.")

        # Start a new thread to handle the client connection
        start_new_thread(clientthread, (conn,))
    except KeyboardInterrupt:
        print("\nGot KeyboardInterrupt, exiting now.")
        sys.exit(0)
