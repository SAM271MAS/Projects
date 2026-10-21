#include "TCPServer.h"
#include "FTPServer.h"
#include <iostream>
#include <string>

int main(int argc, char** argv) {
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << " <port> <directory>" << std::endl;
        return 1;
    }

    int port = std::stoi(argv[1]);
    std::string directory = argv[2];

    std::cout << "Lancement du serveur FTP sur le port " << port 
              << " dossier " << directory << std::endl;

    // Création  
    FTPServer* handler = new FTPServer(directory);

    pr::TCPServer server(handler);
    server.startServer(port);

    // quitter
    std::string cmd;
    std::cin >> cmd;

    server.stopServer();
    return 0;
}
