#include <iostream>
#include <string>
#include <cstring>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>

#define MAXLINE 1024

int main(int argc, char** argv) {
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << " <ip> <port>" << std::endl;
        return 1;
    }

    std::string server_ip = argv[1];
    int port = std::stoi(argv[2]);

    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);

    if (sockfd < 0){
        perror("socket err");
        return 1;
    }

    struct sockaddr_in server_add = {0};
    server_add.sin_family = AF_INET;
    server_add.sin_port = htons(port);

    if (inet_pton(AF_INET, server_ip.c_str(), &server_add.sin_addr) <= 0){ //frm human readable to binary
        std::cerr << "add not valid" << std::endl;
        return 1;
    }

    std::cout << "UDP Client ready." << std::endl;

    std::string line;
    char buffer[MAXLINE];

    while(std::getline(std::cin, line)){

        if (line.empty())
            continue;

        if (line == "Q"){
            sendto(sockfd, line.c_str(), line.size(), 0, (struct sockaddr *)&server_add, sizeof(server_add));
            std::cout << "Good bye" << std::endl;
            break;
        }

        ssize_t sent = sendto(sockfd, line.c_str(), line.size(), 0, (struct sockaddr *)&server_add, sizeof(server_add));

        if (sent < 0){
            perror("sendto err");
            continue;
        }

        struct sockaddr_in from_add;
        socklen_t from_len = sizeof(from_add);
        memset(buffer, 0, sizeof(buffer));

        ssize_t n = recvfrom(sockfd, buffer, sizeof(buffer)-1, 0, (struct sockaddr *)&from_add, &from_len);

        if(n > 0){
            buffer[n] = '\0';
            std::cout << "Server: " << buffer;
        }

    }
    close(sockfd);
    return 0;

}
