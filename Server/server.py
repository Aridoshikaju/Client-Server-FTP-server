import socket
import sys
import time
import os
import struct

print(f"\nWelcome to the FTP server.\n\nTo get started, connect a client.")

# Initialise socket stuff
TCP_IP = "127.0.0.1" # Only a local server
TCP_PORT = 1456 # Just a random choice
BUFFER_SIZE = 1024 # Standard size
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
conn, addr = s.accept()

print(f"\nConnected to by address: {addr}")

def upld():
    # Send message once server is ready to recieve file details
    conn.sendall(b"1")
    # Recieve file name length, then file name
    file_name_size = struct.unpack("h", conn.recv(2))[0]
    file_name = conn.recv(file_name_size)
    # Send message to let client know server is ready for document content
    conn.sendall(b"1")
    # Recieve file size
    file_size = struct.unpack("i", conn.recv(4))[0]
    # Initialise and enter loop to recive file content
    start_time = time.time()
    output_file = open(file_name, "wb")
    # This keeps track of how many bytes we have recieved, so we know when to stop the loop
    bytes_recieved = 0
    print(f"\nRecieving...")
    while bytes_recieved < file_size:
        l = conn.recv(BUFFER_SIZE)
        output_file.write(l)
        bytes_recieved += BUFFER_SIZE
    output_file.close()
    print(f"\nRecieved file: {file_name}")
    # Send upload performance details
    conn.sendall(struct.pack("f", time.time() - start_time))
    conn.sendall(struct.pack("i", file_size))
    return

def list_files():
    with conn:
        print(f"Listing files...")
        # Get list of files in directory
        listing = os.listdir(os.getcwd())
        print(os.getcwd)
        # Send over the number of files, so the client knows what to expect (and avoid some errors)
        print(len(listing))
        conn.sendall(struct.pack("i", len(listing)))
        total_directory_size = 0
        # Send over the file names and sizes whilst totaling the directory size
        for i in listing:
            # File name size
            conn.sendall(struct.pack("i", sys.getsizeof(i)))
            # File name
            conn.sendall(str(i).encode())
            # File content size
            conn.sendall(struct.pack("i", os.path.getsize(i)))
            total_directory_size += os.path.getsize(i)
            # Make sure that the client and server are syncronised
            conn.recv(BUFFER_SIZE)
        # Sum of file sizes in directory
        conn.sendall(struct.pack("i", total_directory_size))
        #Final check
        conn.recv(BUFFER_SIZE)
        print(f"Successfully sent file listing")
        return

def dwld():
    conn.sendall(b"1")
    file_name_length = struct.unpack("h", conn.recv(2))[0]
    print(file_name_length)
    file_name = conn.recv(file_name_length)
    print(file_name)
    if os.path.isfile(file_name):
        # Then the file exists, and send file size
        conn.sendall(struct.pack("i", os.path.getsize(file_name)))
    else:
        # Then the file doesn't exist, and send error code
        print(f"File name not valid")
        conn.sendall(struct.pack("i", -1))
        return
    # Wait for ok to send file
    conn.recv(BUFFER_SIZE)
    # Enter loop to send file
    start_time = time.time()
    print(f"Sending file...")
    content = open(file_name, "rb")
    # Again, break into chunks defined by BUFFER_SIZE
    l = content.read(BUFFER_SIZE)
    while l:
        conn.sendall(l)
        l = content.read(BUFFER_SIZE)
    content.close()
    # Get client go-ahead, then send download details
    conn.recv(BUFFER_SIZE)
    conn.sendall(struct.pack("f", time.time() - start_time))
    return


def delf():
    # Send go-ahead
    conn.sendall(b"1")
    # Get file details
    file_name_length = struct.unpack("h", conn.recv(2))[0]
    file_name = conn.recv(file_name_length)
    # Check file exists
    if os.path.isfile(file_name):
        conn.sendall(struct.pack("i", 1))
    else:
        # Then the file doesn't exist
        conn.sendall(struct.pack("i", -1))
    # Wait for deletion conformation
    confirm_delete = conn.recv(BUFFER_SIZE)
    if confirm_delete == "Y":
        try:
            # Delete file
            os.remove(file_name)
            conn.sendall(struct.pack("i", 1))
        except:
            # Unable to delete file
            print(f"Failed to delete {file_name}")
            conn.sendall(struct.pack("i", -1))
    else:
        # User abandoned deletion
        # The server probably recieved "N", but else used as a safety catch-all
        print(f"Delete abandoned by client!")
        return


def quit():
    # Send quit conformation
    conn.sendall(b"1")
    # Close and restart the server
    conn.close()
    s.close()
    os.execl(sys.executable, sys.executable, *sys.argv)

while True:
    # Enter into a while loop to recieve commands from client
    print(f"\n\nWaiting for instruction")
    data = conn.recv(BUFFER_SIZE)
    data = str(data.upper())
    print(data)
    if data=="UPLD":
        print("Fuck1")
    if(data=="b'LIST'"):
        print("finalllydjsabhjbcjhbchjdcbjhdcbsdcbsdcbajdbchagbdvhba fvhkdkhb")
        
    print(f"\nRecieved instruction: {data}")
    # Check the command and respond correctly
    if data == "UPLD":
        upld()
    elif data == "b'LIST'":
        list_files()
    elif data == "DWLD":
        dwld()
    elif data == "DELF":
        delf()
    elif data == "QUIT":
        quit()
    # Reset the data to loop
    data = None

