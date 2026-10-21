#pragma once
#include "ConnectionHandler.h"
#include <string>

class FTPServer : public pr::ConnectionHandler{

private:
    std::string rootPath; // Le repertoire

    void doList(int clientFD);

    void doUpload(int clientFD, std::string filename, int filesize);

    void doDownload(int clientFD, std::string filename);

public:
    FTPServer(const std::string& path); //Constructeur

    void handleConnection(pr::Socket& sc) override; //boucle disc avec le client

    pr::ConnectionHandler *clone() const override{ //cloner pour les threads
        return new FTPServer(rootPath);
    }


};
