from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR, SOL_SOCKET, SO_REUSEADDR 
from sys import argv
from ipaddress import ip_address
from select import select
from threading import Thread, Lock


cache = {}  ## Dictionnaire de cache au format {clé : réponse HTTP}, avec la clé définie comme (uri, adresse_serveur, port_serveur)
cache_lock = Lock()  ## Verrou global protégeant l'accès concurrent au dictionnaire de cache


def validate_input(u_server_address, u_server_port):
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


def ask_server_info():
    u_server_address = input("Entrez l’addresse IP du serveur (format : xxx.xxx.xxx.xxx) : ")
    u_server_port    = input("Entrez le port du serveur (1–65535) : ")
    return u_server_address, u_server_port


def print_exception(e):
    print("An error occurred:")
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


def server_or_cache(key, func):
    """Retourne la réponse mise en cache pour la clé donnée ou appelle func pour l'obtenir et la mettre en cache"""
    with cache_lock:
        if key not in cache:
            cache[key] = func() ## Appelle la fonction exchange_with_server()
        return cache[key]


def parse_request_line(data: bytes) -> tuple[str | None, str | None]:
    """Extrait la méthode et l'URI de la première ligne d'une requête HTTP"""
    # isoler la première ligne (tout ce qui précède CRLF)
    raw_line = data.partition(b"\r\n")[0]
    try:
        # diviser en au plus 3 parties : METHOD, URI, le reste
        method, uri, _ = raw_line.decode("utf-8", "ignore").split(maxsplit=2)
    except ValueError:
        return None, None
    return method, uri


def handle_client(client_socket, server_address, server_port):
    try:
        data = recv_with_timeout(client_socket)
        method, uri = parse_request_line(data)
        key = (uri, server_address, server_port)

        if method == "GET":
            to_send = server_or_cache(key, lambda: exchange_with_server(data, server_address, server_port))
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
            client_socket, _ = relay_socket.accept()
            Thread(target=handle_client,args=(client_socket, server_address, server_port, )).start()
    finally:
        relay_socket.close()


def main():
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
            print("\033[91mUne ou plusieurs des valeurs ne sont pas correctes\033[0m")
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
        exit()






if __name__ == "__main__":
    main()


