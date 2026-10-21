# include "TCPServer.h"
#include <unistd.h>

namespace pr {

TCPServer::~TCPServer(){
    if (ss){
        delete ss;
        ss = nullptr;
    }

    for (auto &t: threads){
        if(t.joinable()){
            t.join();
        }
    }
}

void TCPServer::handleClient(Socket sc){

    ConnectionHandler *myHandler = handler->clone();
    myHandler->handleConnection(sc);
    delete myHandler;
}

bool TCPServer::startServer(int port){
    ss = new ServerSocket(port);

    if (ss->isOpen()){
        isRunning = true;
        while(isRunning){
            Socket sc = ss->accept();

            if (sc.isOpen()){
                threads.emplace_back(&TCPServer::handleClient, this, std::move(sc));
            }
        }
        return true;
    }
    return false;
}

void TCPServer::stopServer() {
    isRunning = false;

    if (ss)
        ss->close();
}

} // pr
