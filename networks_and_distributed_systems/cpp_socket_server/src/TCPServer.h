#ifndef SRC_TCPSERVER_H_
#define SRC_TCPSERVER_H_

#include <thread>
#include <vector>
#include <atomic>

#include "ServerSocket.h"
#include "ConnectionHandler.h"

namespace pr {

// un serveur TCP, la gestion des connections est déléguée
class TCPServer {
	ServerSocket * ss; // la socket d'attente si elle est instanciee
	ConnectionHandler * handler; // le gestionnaire de session passe a la constru
    std::vector<std::thread> threads;
    std::atomic<bool> isRunning;

private:
    void handleClient(Socket sc);

public :
	TCPServer(ConnectionHandler * handler): ss(nullptr),handler(handler) {}

    ~TCPServer();

	// Tente de creer une socket d'attente sur le port donné
	bool startServer (int port);

	// stoppe le serveur
	void stopServer () ;
};

} // ns pr
#endif
