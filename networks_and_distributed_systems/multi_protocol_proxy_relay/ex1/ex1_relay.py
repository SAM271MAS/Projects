from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR, SOL_SOCKET, SO_REUSEADDR
from sys import argv
from ipaddress import ip_address
from threading import Thread
from select import select
from typing import Tuple, Union, Optional



def validate_input(u_server_address: str, u_server_port: str) -> Tuple[Union[str, bool], Union[int, bool]]:
    """Vérifie et convertit l'adresse IP et le port fournis par l'utilisateur"""
    # Verifier addresse
    try:
        ip_address(u_server_address)
        server_address = u_server_address
    except ValueError:
        return False, False

    # Verifier Port
    try:
        server_port = int(u_server_port)
    except ValueError:
        return False, False

    if not (0 < server_port <= 65535):
        return False, False
    
    return server_address, server_port


def ask_server_info() -> Tuple[str, str]:
    """Demande à l'utilisateur l'adresse IP et le port et renvoie les deux valeurs en str"""
    u_server_address = input("Entrez l’addresse IP du serveur (format : xxx.xxx.xxx.xxx) : ")
    u_server_port    = input("Entrez le port du serveur (1–65535) : ")
    return u_server_address, u_server_port


def print_exception(e: Exception) -> None:
    print("An error occurred:")
    print(type(e))
    print(e.args) 
    print(e)


""" 
Inspiré par : https://stackoverflow.com/questions/2719017/how-to-set-timeout-on-pythons-socket-recv-method
La variable delay peut être modifiée, par exemple à 0.1 pour un traitement plus rapide,
mais cela augmente le risque de ne pas recevoir toutes les données. 
À l'inverse, nous pouvons la porter à 2-5 secondes pour garantir la réception de toutes les données, mais cela rendra le relais plus lent.
"""
def recv_with_timeout(sock: socket, delay: float = 0.5) -> bytes:
    """Reçoit des données depuis un socket en bouclant avec un timeout et retourne tous les octets reçus"""
    data = b''
    while True:
        ready, _, _ = select([sock], [], [], delay)
        # délai d'attente expiré, aucun socket prêt
        if not ready:
            break
        chunk = sock.recv(4096)
        # le serveur a fermé la connexion
        if not chunk:
            break
        data += chunk
    return data


def exchange_with_server(to_send: bytes, server_address: str, server_port: int) -> bytes:
    """Ouvre une connexion TCP vers le serveur cible, envoie les octets fournis et retourne la réponse"""
    with socket(AF_INET, SOCK_STREAM) as server_socket:
        server_socket.connect((server_address, server_port))
        server_socket.sendall(to_send)
        return recv_with_timeout(server_socket)


def handle_client(client_socket: socket, server_address: str, server_port: int) -> None:
    """Traite une connexion client: lit les données, les relaie au serveur distant et renvoie la réponse au client"""
    try:
        recived = recv_with_timeout(client_socket)
        to_send = exchange_with_server(recived, server_address, server_port)
        client_socket.sendall(to_send)

    except Exception as e:
        print_exception(e)

    finally:
        client_socket.close()


def relay(relay_socket: socket, server_address: str, server_port: int) -> None:
    """Accepte en boucle les connexions entrantes et crée un thread pour traiter chaque client"""
    try:
        while True:
            client_socket, _ = relay_socket.accept()
            Thread(target=handle_client,args=(client_socket, server_address, server_port, )).start()

    finally:
        relay_socket.close()




def main() -> None:
    """Configure le socket relais, obtient et valide l'adresse/port du serveur puis lance la boucle d'acceptation"""
    relay_port = 1234
    relay_address = "127.0.0.1"
    relay_socket = socket(AF_INET, SOCK_STREAM)
    relay_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    relay_socket.bind((relay_address, relay_port))
    relay_socket.listen()

    if len(argv) == 3:
        u_server_address = argv[1]
        u_server_port = argv[2]

    else:
        u_server_address, u_server_port = ask_server_info()


    while True:
        server_address, server_port = validate_input(u_server_address, u_server_port)

        if server_address and server_port:
            break

        else:
            u_server_address, u_server_port = ask_server_info()

    try:
        relay(relay_socket, server_address, server_port)

    except KeyboardInterrupt:
        try:
            relay_socket.shutdown(SHUT_RDWR)
        except OSError:
            pass

        relay_socket.close()
        print("Shutdown complete")


if __name__ == "__main__":
    main()

