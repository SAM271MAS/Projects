#include "Socket.h"

#include <iostream>
#include <cstring>      // memset
#include <unistd.h>     // close()
#include <netdb.h>      // getaddrinfo, getnameinfo
#include <arpa/inet.h>  // inet_ntop, htons
#include <cassert>      // assert

namespace pr {

std::ostream &operator<<(std::ostream &os, struct sockaddr_in *addr){
    char hname[1024];
    char addr_str[INET_ADDRSTRLEN];

    getnameinfo((struct sockaddr *)addr, sizeof *addr, hname, 1024, nullptr, 0, 0);
    os << hname << " ";

    inet_ntop(AF_INET, &(addr->sin_addr), addr_str, INET_ADDRSTRLEN);
    os << addr_str << " " << ntohs(addr->sin_port) << std::endl;

    return os;

}

// Socket Class


// Move constructor
Socket::Socket(Socket&& other){
    this->fd = other.fd;
    other.fd = -1;
}

//Move assignment
Socket &Socket::operator=(Socket &&other){
    if (this != &other){
        if (fd != -1)
            close(); 

        this->fd = other.fd;
        other.fd = -1;
    }
    return *this;
}




Socket::~Socket() {
    if (fd != -1) {
        close();
    }
}

void Socket::close() {
    if (fd != -1) {
        
        // ::shutdown appelle global shutdown
        ::shutdown(fd, SHUT_RDWR);

        ::close(fd);
        fd = -1; // Mark as closed so we don't close it twice
    }
}


void Socket::connect(const std::string &host, int port){
    struct addrinfo hints = {0}; // init all to 0
    struct addrinfo *res = nullptr;

    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;

    int status = getaddrinfo(host.c_str(), nullptr, &hints, &res);

    if (status != 0){
        perror("getaddrinfo err");
        exit(1) ;
    }

    in_addr ipv4;
    bool found = false;

    for (struct addrinfo *a = res; a != nullptr; a = a->ai_next){
        if(a->ai_family == AF_INET){
            ipv4 = ((struct sockaddr_in *)a->ai_addr)->sin_addr;
            found = true;
            break;
        }
    }
    freeaddrinfo(res);

    if (found){
        this->connect(ipv4, port);
    }
    else{
        perror("no ipv4 found");
    }

}

void Socket::connect(in_addr ipv4, int port){
    //verf si déja connecté
    if(fd != -1){
        close();
    }

    struct sockaddr_in dest = {0};

    dest.sin_family = AF_INET;
    dest.sin_addr = ipv4;
    dest.sin_port = htons(port);

    fd = ::socket(AF_INET, SOCK_STREAM, 0);

    if (fd == -1){
        perror("socket err");
        exit(1);
    }

    if(::connect(fd, (struct sockaddr *)&dest, sizeof(dest)) == -1){
        perror("connect err");
        close();
    }

} // Class Socket

} //namespace pr


