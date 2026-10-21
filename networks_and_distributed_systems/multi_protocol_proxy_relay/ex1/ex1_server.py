from socket import socket, AF_INET, SOCK_STREAM
from select import poll, POLLIN, POLLOUT, POLLHUP, POLLERR, POLLNVAL


server_port = 8000
server_address = "127.0.0.1"
server_socket = socket(AF_INET,SOCK_STREAM)
server_socket.bind((server_address,server_port))
server_socket.listen()

my_poll = poll()
my_poll.register(server_socket, POLLIN)

sockets = {server_socket.fileno(): server_socket}
received = dict()
to_send = dict()


def server():
    while True:
        
        for fd, event in my_poll.poll():
            if event & (POLLHUP | POLLERR | POLLNVAL):
                received.pop(fd, None)
                to_send.pop(fd, None)
                my_poll.unregister(fd)
                sockets.pop(fd, None)
    
            # Nouvelles connexions
            elif sockets[fd] is server_socket:
                connection_socket, address = server_socket.accept()
    
                sockets[connection_socket.fileno()] = connection_socket
                my_poll.register(connection_socket, POLLIN)
    
            else:
                # Données disponibles en lecture
                if event & POLLIN:
                    data = sockets[fd].recv(4096)
                    if not data:
                        sockets[fd].close()
                        continue
                    if fd in received:
                        received[fd] += data
                    else:
                        received[fd] = data
                    my_poll.modify(fd, POLLIN | POLLOUT)
                
                # Données disponibles à envoyer
                if event & POLLOUT:
                    data = received.pop(fd).decode("utf-8")
                    data = data.upper().encode("utf-8")
    
                    if fd in to_send:
                        data = to_send.pop(fd) + data
    
                    n = sockets[fd].send(data)
    
                    if n < len(data):
                        to_send[fd] = data[n:]
                    else:
                        my_poll.modify(fd, POLLIN)

def main():
    server()

if __name__ == "__main__":
    server()
