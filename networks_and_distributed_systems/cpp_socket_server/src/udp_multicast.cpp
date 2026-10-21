#include <iostream>
#include <string>
#include <cstring>
#include <thread>
#include <vector>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <unistd.h>

#define BUFFER_SIZE 1024

bool isRunning = true;


void receive_messages(int sockfd) {
    char buffer[BUFFER_SIZE];
    struct sockaddr_in senderAddr;
    socklen_t len = sizeof(senderAddr);

    while (isRunning) {
        memset(buffer, 0, BUFFER_SIZE);
        
        ssize_t n = recvfrom(sockfd, buffer, BUFFER_SIZE - 1, 0, (struct sockaddr*)&senderAddr, &len);
        
        if (n > 0) {
            std::cout << buffer << std::endl;
        } else if (n < 0) {
            break;
        }
    }
}

int main(int argc, char** argv) {
    if (argc != 4) {
        std::cerr << "Usage: " << argv[0] << " <multicast_ip> <port> <username>" << std::endl;
        std::cerr << "Example: " << argv[0] << " 225.0.0.10 2001 Batman" << std::endl;
        return 1;
    }

    std::string multiIP = argv[1];
    int port = std::stoi(argv[2]);
    std::string username = argv[3];

    // create socket
    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("socket");
        return 1;
    }

    // Allow reusing the port
    int reuse = 1;
    if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, (char*)&reuse, sizeof(reuse)) < 0) {
        perror("setsockopt(SO_REUSEADDR) failed");
        return 1;
    }

    // bind
    struct sockaddr_in localAddr = {0};
    localAddr.sin_family = AF_INET;
    localAddr.sin_port = htons(port);
    localAddr.sin_addr.s_addr = INADDR_ANY;

    if (bind(sockfd, (struct sockaddr*)&localAddr, sizeof(localAddr)) < 0) {
        perror("bind failed");
        return 1;
    }

    // Abonnement à un groupe multicast
    struct ip_mreq group;
    group.imr_multiaddr.s_addr = inet_addr(multiIP.c_str());
    group.imr_interface.s_addr = INADDR_ANY;

    if (setsockopt(sockfd, IPPROTO_IP, IP_ADD_MEMBERSHIP, (char*)&group, sizeof(group)) < 0) {
        perror("setsockopt err");
        return 1;
    }
    std::cout << "Joined " << multiIP << ":" << port << " as " << username << std::endl;

    std::cout << "you can start typing messages" << std::endl;

    // start listener
    std::thread listener(receive_messages, sockfd);

    // sending add
    struct sockaddr_in destAddr = {0};
    destAddr.sin_family = AF_INET;
    destAddr.sin_addr.s_addr = inet_addr(multiIP.c_str());
    destAddr.sin_port = htons(port);

    std::string line;
    while (std::getline(std::cin, line)) {
        if (line.empty()) continue;

        // [Username] Message
        std::string fullMessage = "[" + username + "] " + line;

        sendto(sockfd, fullMessage.c_str(), fullMessage.size(), 0, (struct sockaddr*)&destAddr, sizeof(destAddr));
    }
    isRunning = false;
    shutdown(sockfd, SHUT_RDWR); 
    close(sockfd);
    
    if (listener.joinable()) {
        listener.join();
    }

    return 0;
}
