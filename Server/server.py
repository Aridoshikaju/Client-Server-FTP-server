from fileinput import filename
import socket
import sys
import os
import struct

print(f"\nWelcome to the FTP server.\n\nTo get started, connect a client.")

# Initialise socket constants
TCP_IP = "127.0.0.1" 
TCP_PORT = 1456 # Anything
BUFFER_SIZE = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
conn, addr = s.accept()

print(f"\nConnected to by address: {addr}")

def upld():
    conn.sendall(b"1")
    file_name_size = struct.unpack("h", conn.recv(2))[0]
    file_name = conn.recv(file_name_size)
    print("herer 1")
    print(file_name)
    conn.sendall(b"1")
    file_size = struct.unpack("i", conn.recv(4))[0]
    output_file = open(file_name, "wb")
    bytes_recieved = 0
    print(f"\nRecieving...")
    while bytes_recieved < file_size:
        l = conn.recv(BUFFER_SIZE)
        output_file.write(l)
        bytes_recieved += BUFFER_SIZE
    output_file.close()
    print(f"\nRecieved file: {file_name}")
    conn.sendall(struct.pack("i", file_size))
    return

def list_files():
    print(f"Listing files...")
    listing = os.listdir(os.getcwd())
    print(len(listing))
    conn.sendall(struct.pack("i", len(listing)))
    total_size = 0
    for i in listing:
        conn.sendall(struct.pack("i", sys.getsizeof(i)))
        conn.sendall(str(i).encode())
        conn.sendall(struct.pack("i", os.path.getsize(i)))
        total_size += os.path.getsize(i)
        conn.recv(BUFFER_SIZE)
    conn.sendall(struct.pack("i", total_size))
    conn.recv(BUFFER_SIZE)
    print(f"Successfully sent file listing")
    return

def dwld():
    conn.sendall(b"1")
    file_length = struct.unpack("h", conn.recv(2))[0]
    print(file_length)
    file_name = conn.recv(file_length)
    print(file_name)
    if os.path.isfile(file_name):
        conn.sendall(struct.pack("i", os.path.getsize(file_name)))
    else:
        print(f"File name not valid")
        conn.sendall(struct.pack("i", -1))
        return
    conn.recv(BUFFER_SIZE)
    print(f"Sending file...")
    content = open(file_name, "rb")
    l = content.read(BUFFER_SIZE)
    while l:
        conn.sendall(l)
        l = content.read(BUFFER_SIZE)
    content.close()
    conn.recv(BUFFER_SIZE)
    return


def quit():
    conn.sendall(b"1")
    conn.close()
    s.close()

while True:
    print(f"\n\nWaiting for instruction")
    data = conn.recv(BUFFER_SIZE)
    data = str(data.upper())
    print(f"\nRecieved instruction: {data}")
    if data == "b'UPLD'":
        upld()
    elif data == "b'LIST'":
        list_files()
    elif data == "b'DWLD'":
        dwld()
    elif data == "b'QUIT'":
        quit()
    data = None

