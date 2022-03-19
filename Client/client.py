import socket
import sys
import os
import struct

# Initialise socket stuff
TCP_IP = "127.0.0.1" # Only a local server
TCP_PORT = 1456 # Just a random choice
BUFFER_SIZE = 1024 # Standard chioce
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
    # Upload a file
    print(f"\nUploading file: {file_name}...")
    try:
        # Check the file exists
        content = open(file_name, "rb")
    except:
        print(f"Couldn't open file. Make sure the file name was entered correctly.")
        return
    try:
        # Make upload request
        s.sendall(b"UPLD")
    except:
        print(f"Couldn't make server request. Make sure a connection has bene established.")
        return
    try:
        # Wait for server acknowledgement then send file details
        # Wait for server ok
        print("here 1")
        s.recv(BUFFER_SIZE)
        # Send file name size and file name
        s.sendall(struct.pack("h", sys.getsizeof(file_name)))
        print("here 2")
        s.sendall(str(file_name).encode())
        print("here 3")
        # Wait for server ok then send file size
        s.recv(BUFFER_SIZE)
        s.send(struct.pack("i", os.path.getsize(file_name)))
    except:
        print(f"Error sending file details")
    try:
        # Send the file in chunks defined by BUFFER_SIZE
        # Doing it this way allows for unlimited potential file sizes to be sent
        l = content.read(BUFFER_SIZE)
        print(f"\nSending...")
        while l:
            s.send(l)
            l = content.read(BUFFER_SIZE)
        content.close()
        # Get upload performance details
        upload_time = struct.unpack("f", s.recv(4))[0]
        upload_size = struct.unpack("i", s.recv(4))[0]
        print(f"\nSent file: {file_name}\nTime elapsed: {upload_time}s\nFile size: {upload_size}b")
    except:
        print(f"Error sending file")
        return
    return

def list_files():
    # List the files avaliable on the file server
    # Called list_files(), not list() (as in the format of the others) to avoid the standard python function list()
    print(f"Requesting files...\n")
    try:
        # Send list request
        s.sendall(b"LIST")
    except:
        print(f"Couldn't make server request. Make sure a connection has bene established.")
        return
    try:
        # First get the number of files in the directory
        number_of_files = struct.unpack("i", s.recv(4))[0]
        # Then enter into a loop to recieve details of each, one by one
        for i in range(int(number_of_files)):
            # Get the file name size first to slightly lessen amount transferred over socket
            file_name_size = struct.unpack("i", s.recv(4))[0]
            file_name = s.recv(file_name_size)
            # Also get the file size for each item in the server
            file_size = struct.unpack("i", s.recv(4))[0]
            print(f"\t{file_name} - {file_size}b")
            # Make sure that the client and server are syncronised
            s.sendall(b"1")
        # Get total size of directory
        total_directory_size = struct.unpack("i", s.recv(4))[0]
        print(f"Total directory size: {total_directory_size}b")
    except:
        print(f"Couldn't retrieve listing")
        return
    try:  
        # Final check
        s.sendall(b"1")
        return
    except:
        print(f"Couldn't get final server confirmation")
        return


def dwld(file_name):
    # Download given file
    print(f"Downloading file: {file_name}")
    try:
        # Send server request
        s.sendall(b"DWLD")
    except:
        print(f"Couldn't make server request. Make sure a connection has bene established.")
        return
    try:
        # Wait for server ok, then make sure file exists
        s.recv(BUFFER_SIZE)
        # Send file name length, then name
        s.send(struct.pack("h", sys.getsizeof(file_name)))
        s.send(file_name)
        # Get file size (if exists)
        file_size = struct.unpack("i", s.recv(4))[0]
        if file_size == -1:
            # If file size is -1, the file does not exist
            print(f"File does not exist. Make sure the name was entered correctly")
            return
    except:
        print(f"Error checking file")
    try:
        # Send ok to recieve file content
        s.sendall(b"1")
        # Enter loop to recieve file
        output_file = open(file_name, "wb")
        bytes_recieved = 0
        print(f"\nDownloading...")
        while bytes_recieved < file_size:
            # Again, file broken into chunks defined by the BUFFER_SIZE variable
            l = s.recv(BUFFER_SIZE)
            output_file.write(l)
            bytes_recieved += BUFFER_SIZE
        output_file.close()
        print(f"Successfully downloaded {file_name}")
        # Tell the server that the client is ready to recieve the download performance details
        s.sendall(b"1")
        # Get performance details
        time_elapsed = struct.unpack("f", s.recv(4))[0]
        print(f"Time elapsed: {time_elapsed}s\nFile size: {file_size}b")
    except:
        print(f"Error downloading file")
        return
    return


def delf(file_name):
    # Delete specified file from file server
    print(f"Deleting file: {file_name}...")
    try:
        # Send resquest, then wait for go-ahead
        s.sendall(b"DELF")
        s.recv(BUFFER_SIZE)
    except:
        print(f"Couldn't connect to server. Make sure a connection has been established.")
        return
    try:
        # Send file name length, then file name
        s.send(struct.pack("h", sys.getsizeof(file_name)))
        s.send(file_name)
    except:
        print(f"Couldn't send file details")
        return
    try:
        # Get conformation that file does/doesn't exist
        file_exists = struct.unpack("i", s.recv(4))[0]
        if file_exists == -1:
            print(f"The file does not exist on server")
            return
    except:
        print(f"Couldn't determine file existance")
        return
    try:
        # Confirm user wants to delete file
        confirm_delete = input("Are you sure you want to delete {file_name}? (Y/N)\n").upper()
        # Make sure input is valid
        # Unfortunately python doesn't have a do while style loop, as that would have been better here
        while confirm_delete != "Y" and confirm_delete != "N" and confirm_delete != "YES" and confirm_delete != "NO":
            # If user input is invalid
            print(f"Command not recognised, try again")
            confirm_delete = input("Are you sure you want to delete {file_name}? (Y/N)\n").upper()
    except:
        print(f"Couldn't confirm deletion status")
        return
    try:
        if confirm_delete == "Y" or confirm_delete == "YES":
            s.sendall(b"Y")
            delete_status = struct.unpack("i", s.recv(4))[0]
            if delete_status == 1:
                print(f"File successfully deleted")
                return
            else:
                # Client will probably send -1 to get here, but an else is used as more of a catch-all
                print(f"File failed to delete")
                return
        else:
            s.sendall(b"N")
            print(f"Delete abandoned by user!")
            return
    except:
        print(f"Couldn't delete file")
        return

def quit():
    s.sendall(b"QUIT")
    # Wait for server go-ahead
    s.recv(BUFFER_SIZE)
    s.close()
    print(f"Server connection ended")
    return

print(f"\n\nWelcome to the FTP client.\n\nCall one of the following functions:\nCONN           : Connect to server\nUPLD file_path : Upload file\nLIST           : List files\nDWLD file_path : Download file\nDELF file_path : Delete file\nQUIT           : Exit")

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
    elif x[:4].upper() == "DELF":
        delf(x[5:])
    elif x[:4].upper() == "QUIT":
        quit()
        break
    else:
        print(f"Command not recognised; please try again")
        
    # if x[:4].upper() != "CONN":
    #     os.execl(sys.executable )

