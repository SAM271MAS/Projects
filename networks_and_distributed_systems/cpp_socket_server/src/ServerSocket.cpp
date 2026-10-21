#include "ServerSocket.h"

#include <unistd.h> //close
#include <iostream>

namespace pr{

ServerSocket::ServerSocket(int port):socketfd(-1){

    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd == -1) {
        perror("socket err");
        return;
    }

    int reuse = 1;
    if (setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, (const char*)&reuse, sizeof(reuse)) < 0) {
        perror("setsockopt(SO_REUSEADDR) failed");
        ::close(fd);
        return;
    }

    struct sockaddr_in sin = {0};

    sin.sin_family = AF_INET;
    sin.sin_addr.s_addr = htonl(INADDR_ANY);
    sin.sin_port = htons(port);

    if (::bind(fd, (struct sockaddr *)&sin, sizeof(sin)) == -1) {
        perror("bind err");
        ::close(fd);
        return;
    }

    if (::listen(fd, 50) == -1) {
        perror("listen err");
        ::close(fd);
        return;
    }
    socketfd = fd;
}

// ServerSocket::~ServerSocket() {
//     close();
// }

void ServerSocket::close(){
    if (socketfd != -1) {
        ::close(socketfd);
        socketfd = -1;
    }
}


Socket ServerSocket::accept() {
    struct sockaddr_in exp;
    socklen_t len = sizeof(exp);

    int client_fd = ::accept(socketfd, (struct sockaddr *)&exp, &len);

    if (client_fd == -1) {
        perror("accept err");
        return Socket(-1); 
    }

    // operator<< dans Socket.h/.cpp
    std::cout << "Connection from: " << &exp << std::endl;

    return Socket(client_fd);
}

}
