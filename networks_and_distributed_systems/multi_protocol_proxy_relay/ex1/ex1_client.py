from socket import socket, AF_INET, SOCK_STREAM


server_ip = "127.0.0.1"

server_port = 1234

client_socket = socket(AF_INET, SOCK_STREAM)

client_socket.connect((server_ip, server_port))

client_socket.send("ping".encode("utf-8"))

server_message = client_socket.recv(2048)

print(server_message.decode("utf-8"))


client_socket.close()




