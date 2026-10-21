#include "Socket.h"
#include <iostream>
#include <string>
#include <sstream>
#include <unistd.h>
#include <cstring> 

#include <fstream>
#include <vector>

void handle_upload(pr::Socket& sock, std::string filename) {
    // 1. Open file to get size
    std::ifstream file(filename, std::ios::binary | std::ios::ate);
    if (!file.is_open()) {
        std::cout << "Error: File " << filename << " not found locally." << std::endl;
        return;
    }
    int filesize = file.tellg();
    file.seekg(0, std::ios::beg);

    // 2. Send cmd
    std::string cmd = "UPLOAD " + filename + " " + std::to_string(filesize) + "\n";
    write(sock.getFD(), cmd.c_str(), cmd.size());

    // 3. Wait for "READY"
    char buffer[1024] = {0};
    read(sock.getFD(), buffer, sizeof(buffer));

    if (std::string(buffer).find("READY") == std::string::npos) {
        std::cout << "Server not ready: " << buffer << std::endl;
        return;
    }

    // 4. Send Data
    char fileBuf[4096];
    while (file.read(fileBuf, sizeof(fileBuf)) || file.gcount() > 0) {
        write(sock.getFD(), fileBuf, file.gcount());
    }
    
    // 5. Wait for confirmation
    memset(buffer, 0, sizeof(buffer));
    read(sock.getFD(), buffer, sizeof(buffer));
    std::cout << buffer; // Print server confirmation
}

void handle_download(pr::Socket& sock, std::string filename) {
    // 1. Send Command
    std::string cmd = "DOWNLOAD " + filename + "\n";
    write(sock.getFD(), cmd.c_str(), cmd.size());

    // 2. Read Header (FOUND <size>\n)
    char buffer[4096];
    ssize_t bytesRead = read(sock.getFD(), buffer, sizeof(buffer));
    if (bytesRead <= 0) return;

    std::string response(buffer, bytesRead);
    size_t newlinePos = response.find('\n');

    // Parse header
    std::string header = response.substr(0, newlinePos);
    if (header.find("FOUND") == std::string::npos) {
        std::cout << "Error: " << header << std::endl; // proba "ERROR File not found"
        return;
    }

    // size
    int fileSize = std::stoi(header.substr(6)); // Skip "FOUND "
    
    // 3. Write Data
    std::ofstream outfile(filename, std::ios::binary);
    
    if (newlinePos + 1 < (size_t)bytesRead) {
        outfile.write(buffer + newlinePos + 1, bytesRead - (newlinePos + 1));
    }

    int totalReceived = bytesRead - (newlinePos + 1);

    // 4. Loop for the rest
    while (totalReceived < fileSize) {
        bytesRead = read(sock.getFD(), buffer, sizeof(buffer));
        if (bytesRead <= 0) break;
        outfile.write(buffer, bytesRead);
        totalReceived += bytesRead;
    }
    std::cout << "Download complete: " << filename << " (" << fileSize << " bytes)" << std::endl;
}

int main(int argc, char** argv) {
    if (argc != 3) {
        std::cout << "Usage: ./client <ip> <port>" << std::endl;
        return 1;
    }

    // 1. Connect
    pr::Socket sock;
    sock.connect(argv[1], std::stoi(argv[2]));

    std::string line;
    // 2. Input Loop
    while (std::getline(std::cin, line)) {
        if (line.empty()) continue;

        std::stringstream ss(line);
        std::string cmd;
        ss >> cmd;
        if (cmd == "LIST") {
            std::string msg = "LIST\n";
            write(sock.getFD(), msg.c_str(), msg.size());
            
            char buffer[4096];
            memset(buffer, 0, sizeof(buffer));
            ssize_t n = read(sock.getFD(), buffer, sizeof(buffer) - 1);
            if (n > 0) std::cout << buffer;
        }
        else if (cmd == "UPLOAD") {
            std::string filename;
            ss >> filename;
            if (!filename.empty()) handle_upload(sock, filename);
        }
        else if (cmd == "DOWNLOAD") {
            std::string filename;
            ss >> filename;
            if (!filename.empty()) handle_download(sock, filename);
        }
        else if (cmd == "QUIT") {
            std::string msg = "QUIT\n";
            write(sock.getFD(), msg.c_str(), msg.size()); // Notify server
            break; // Break local loop
        }
        else {
            std::cout << "Unknown command." << std::endl;
        }
    }
    return 0;
}
