import socket
import os
''' Todo
 * Check if theres a local area network to connect to 
 * Eventually make it so I can send to server from anywhere wit sockets
 * add lots of error checking'''
class DataLink():

    def __init__(self):
        self.__mac_ip = "192.168.1.219"
        pass
            
    def __establish_connection_server(self):
        try:
            # Create socket using SOCK__STREAM (TCP) protocol
            __sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            __sock.connect((self.__mac_ip, 5000))
            return __sock
        except socket.error as e:
            print(f"Error establishing connection {e}")
            return None
        
    ''' *** Protocol *** 
        Use unix posix
        
        mkdir args: create folder
        cd args: change directory
        
        Repeat this for every file
        (file contents) > file.csv
    '''
    
    def establish_connection_server(self):
        try:
            # Create socket using SOCK__STREAM (TCP) protocol
            self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__sock.connect((self.__mac_ip, 5000))
            return self.__sock
        except socket.error as e:
            print(f"Error establishing connection {e}")
            return None
        
        

    
    def file_data_stream(self, canon_path):
        if not isinstance(canon_path, str):
            print(f"Argument {canon_path} is not a string")
            return
        
        if not self.__sock:
            print("Error: Socket not initialized")
            return
        
        # get relative path to send over hide the root path
        split_canon_path = canon_path.split(os.sep)
        relative_path = os.sep.join(split_canon_path[9:])
        
        # Send make file command, file name, and start of file command space delimited
        file_send_start = f"*MKF*{relative_path}*"
        self.__sock.send(file_send_start.encode())
        
        """make_file_ack = self.__sock.recv(1024).decode()
        if not make_file_ack == f"MAKEFILE*{relative_path}*ACK":
            print(f"Makefile message not ack, last recieved message {make_file_ack}")
            return"""
        
       # Send over file data stream
        with open(canon_path, 'rb') as file:
            while data_chunck := file.read(1024):
                self.__sock.sendall(data_chunck)
                
        # once all data has been sent send end of file command
        end_of_file_delimiter = "*EOF*"
        self.__sock.send(end_of_file_delimiter.encode())
        
        
    def close_socket(self):
        pass
                
        
        
        
        
        
    
    def test_send(self):
        socket = self.__establish_connection_server()
        if socket:
            message = "Hello from ios"
            socket.sendall(message.encode())
            socket.close()
        else:
            print("Error test send")
            
            
    def stream_file_path(self, path):
        pass
    
    def stream_file_data(self):
        pass