from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR, SOL_SOCKET, SO_REUSEADDR
from sys import argv
from ipaddress import ip_address
from threading import Thread, Lock
from base64 import b64encode
from datetime import timezone, datetime
from select import select
from pathlib import Path


filename = "log_access_interdits.txt"  ## Le fichier log dans lequel seront écrits tous les essais d'accès aux sites interdits.
file_lock = Lock()  ## Verrou global protégeant l'accès concurrent au fichier de logs

"""
Lors du chargement, si le fichier de configuration existe, le relais lit ce fichier ligne par ligne.
Pour chaque ligne, il vérifie qu'elle contient exactement trois parties (adresse, port, URI).
Si c'est le cas, une entrée sous forme de tuple (adresse, port, URI) est ajoutée à l'ensemble set_interdits,
permettant une recherche rapide en O(1). https://wiki.python.org/moin/TimeComplexity#set
Si la ligne ne respecte pas ce format, un message d'erreur est affiché
"""
set_interdits = set()


def validate_input(u_server_address, u_server_port, u_config_file):
    """Vérifie l'adresse IP, le port et l'existence du fichier de configuration, retourne (adresse, port, fichier) ou (None, None, None)"""
    file = Path(u_config_file)
    # Verifier addresse
    try:
        ip_address(u_server_address)
        server_address = u_server_address
    except ValueError:
        return False, False, False

    # Verifier Port
    try:
        server_port = int(u_server_port)
    except ValueError:
        return False, False, False

    if not (0 < server_port <= 65535):
        return False, False, False

    # Vérifier fichier configuration
    if not file.is_file():
        return False, False, False
    
    return server_address, server_port, u_config_file


def ask_server_info():
    u_server_address = input("Entrez l’addresse IP du serveur (format : xxx.xxx.xxx.xxx) : ")
    u_server_port    = input("Entrez le port du serveur (1–65535) : ")
    u_config_file    = input("Entrez le nom du fichier de configuration contenant la liste des sites interdits : ")
    return u_server_address, u_server_port, u_config_file


def load_list(file_name):
    """Charge la liste des sites interdits depuis le fichier de configuration dans l'ensemble set_interdits"""
    global set_interdits

    with open(file_name, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 3:
                address, port, uri = parts
                key = (address, port, uri)
                set_interdits.add(key)
            else:
                print("format incorrect dans le fichier de configuration")


def print_exception(e):
    print("Une erreur est survenue :")
    print(type(e))
    print(e.args) 
    print(e)


def recv_with_timeout(sock: socket, delay: float = 0.5) -> bytes:
    data = b''
    while True:
        ready, _, _ = select([sock], [], [], delay)
        if not ready:
            break
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
    return data


def exchange_with_server(to_send, server_address, server_port):
    with socket(AF_INET, SOCK_STREAM) as server_socket:
        server_socket.connect((server_address, server_port))
        server_socket.sendall(to_send)
        return recv_with_timeout(server_socket)


def parse_request_line(data: bytes) -> tuple[str | None, str | None]:
    raw_line = data.partition(b"\r\n")[0]
    try:
        method, uri, _ = raw_line.decode("utf-8", "ignore").split(maxsplit=2)
    except ValueError:
        return None, None
    return method, uri


def log_request(client_data: bytes, client_address: str, server_address, server_port, uri):
    """Écrit une entrée de log (tentative d'accès interdite) dans le fichier filename et retourne la ligne de log"""
    request_line = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "client": client_address,
        "server url": server_address,
        "server port": server_port,
        "uri": uri,
        "raw_base64_client": b64encode(client_data).decode("utf-8")
    }
    with file_lock:
        with open(filename, 'a', encoding="utf-8") as f:
            f.write((str(request_line)) + "\n")

    return request_line


def html_interdit():
    """Retourne une réponse HTTP 403 Forbidden prête à être envoyée au client"""
    html_body = (
        "<!doctype html>"
        "<head><meta charset=\"utf-8\"><title>403 Interdit</title></head>"
        "<body><h1>403 Interdit</h1></body>"
        "</html>"
    )

    body_bytes = html_body.encode("utf-8")
    headers = (
        "HTTP/1.1 403 Forbidden\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        "\r\n"
    )
    return headers.encode("utf-8") + body_bytes


def handle_client(client_socket, client_address, server_address, server_port):
    """Reçoit la requête client, vérifie si l'accès est interdit via set_interdits et renvoie 403 ou relaie la requête"""
    data = b""
    to_send = b""
    uri = ""
    global set_interdits
    try:
        data = recv_with_timeout(client_socket)

        method, uri = parse_request_line(data)
        key = (server_address, str(server_port), uri)
        if method == "GET" and key in set_interdits:
            to_send = html_interdit()
            log_request(data, client_address, server_address, server_port,uri)

        else:
            to_send = exchange_with_server(data, server_address, server_port)

        client_socket.sendall(to_send)


    except Exception as e:
        print_exception(e)

    finally:
            client_socket.close()


def relay(relay_socket, server_address, server_port):
    try:
        while True:
            client_socket, client_address = relay_socket.accept()
            Thread(target=handle_client,args=(client_socket, client_address, server_address, server_port, )).start()
    finally:
        relay_socket.close()


def main():
    relay_port = 1234
    relay_address = "127.0.0.1"
    relay_socket = socket(AF_INET, SOCK_STREAM)
    relay_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    relay_socket.bind((relay_address, relay_port))
    relay_socket.listen()

    if len(argv) == 4:
        server_address = argv[1]
        server_port = argv[2]
        config_file = argv[3]
    else:
        server_address, server_port, config_file = ask_server_info()

    while True:
        server_address, server_port, config_file = validate_input(server_address, server_port, config_file)
        if server_address and server_port and config_file:
            break
        else:
            print("\033[91mUne ou plusieurs des valeurs ne sont pas correctes\033[0m")
            server_address, server_port, config_file= ask_server_info()

    load_list(config_file)
    try:
        relay(relay_socket, server_address, server_port)
    except KeyboardInterrupt:
        try:
            relay_socket.shutdown(SHUT_RDWR)
        except OSError:
            pass
        relay_socket.close()
        print("Shutdown complete")
        exit()






if __name__ == "__main__":
    main()


