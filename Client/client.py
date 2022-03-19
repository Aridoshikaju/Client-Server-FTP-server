import socket
import sys
import os
import struct

# Initialise socket constants
TCP_IP = "127.0.0.1"
TCP_PORT = 1456 # Anything
BUFFER_SIZE = 1024 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def conn():
    # Connect to the server
    print(f"Sending server request...")
    try:
        s.connect((TCP_IP, TCP_PORT))
        print(f"Connection sucessful")
    except:
        print(f"Connection unsucessful. Make sure the server is online.")

def upld(file_name):
    print(f"\nUploading file: {file_name}...")
    try:
        content = open(file_name, "rb")
    except:
        print(f"Couldn't open file. Make sure the file name was entered correctly.")
        return
    try:
        s.sendall(b"UPLD")
    except:
        print(f"Couldn't make server request. Make sure a connection has bene established.")
        return
    try:
        #print("here 1")
        s.recv(BUFFER_SIZE)
        # Send file name size and name
        s.sendall(struct.pack("h", sys.getsizeof(file_name)))
        #print("here 2")
        s.sendall(str(file_name).encode())
        #print("here 3")
        s.recv(BUFFER_SIZE)
        s.send(struct.pack("i", os.path.getsize(file_name)))
    except:
        print(f"Error sending file details")
    try:
        l = content.read(BUFFER_SIZE)
        print(f"\nSending...")
        while l:
            s.send(l)
            l = content.read(BUFFER_SIZE)
        content.close()
        upload_size = struct.unpack("i", s.recv(4))[0]
        print(f"\nSent file: {file_name}\nFile size: {upload_size}b")
    except:
        print(f"Error sending file")
        return
    return

def list_files():
    print(f"Requesting files...\n")
    try:
        s.sendall(b"LIST")
    except:
        print(f"Couldn't make server request. Make sure a connection has bene established.")
        return
    try:
        number_of_files = struct.unpack("i", s.recv(4))[0]
        for i in range(int(number_of_files)):
            file_name_size = struct.unpack("i", s.recv(4))[0]
            file_name = s.recv(file_name_size)
            file_size = struct.unpack("i", s.recv(4))[0]
            if str(file_name) != "b'server.py'":
                print(f"\t{file_name} - {file_size}b")
            s.sendall(b"1")
        total_directory_size = struct.unpack("i", s.recv(4))[0]
        print(f"Total directory size: {total_directory_size}b")
    except:
        print(f"Couldn't retrieve listing")
        return
    try:  
        s.sendall(b"1")
        return
    except:
        print(f"Couldn't get final server confirmation")
        return


def dwld(file_name):
    print(f"Downloading file: {file_name}")
    try:
        s.sendall(b"DWLD")
    except:
        print(f"Couldn't make server request. Make sure a connection has bene established.")
        return
    try:
        s.recv(BUFFER_SIZE)
        s.sendall(struct.pack("h", sys.getsizeof(file_name)))
        s.sendall(str(file_name).encode())
        file_size = struct.unpack("i", s.recv(4))[0]
        if file_size == -1:
            print(f"File does not exist. Make sure the name was entered correctly")
            return
    except:
        print(f"Error checking file")
    try:
        s.sendall(b"1")
        output_file = open(file_name, "wb")
        bytes_recieved = 0
        print(f"\nDownloading...")
        while bytes_recieved < file_size:
            l = s.recv(BUFFER_SIZE)
            output_file.write(l)
            bytes_recieved += BUFFER_SIZE
        output_file.close()
        print(f"Successfully downloaded {file_name}")
        s.sendall(b"1")
        print(f"File size: {file_size}b")
    except:
        print(f"Error downloading file")
        return
    return
def quit():
    s.send("QUIT")
    # Wait for server go-ahead
    s.recv(BUFFER_SIZE)
    s.close()
    print("Server connection ended")
    return

print(f"\n\nWelcome to the FTP client.\n\nCall one of the following functions:\nCONN           : Connect to server\nUPLD file_Name : Upload file\nLIST           : List files\nDWLD file_Name : Download file\nQUIT           : Exit")

while True:
    
    x = input("\nEnter a command: ")
    if x[:4].upper() == "CONN":
        conn()
    elif x[:4].upper() == "UPLD":
        upld(x[5:])
    elif x[:4].upper() == "LIST":
        list_files()
    elif x[:4].upper() == "DWLD":
        dwld(x[5:])
    elif x[:4].upper() == "QUIT":
        quit()
        break
    else:
        print(f"Command not recognised; please try again")

