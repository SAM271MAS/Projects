#include "FTPServer.h"
#include <iostream>
#include <unistd.h>
#include <cstring>

#include <dirent.h>
#include <sstream>
#include <fstream>

FTPServer::FTPServer(const std::string& path) : rootPath(path) {}

void FTPServer::handleConnection(pr::Socket& sc) {
    int fd = sc.getFD(); 
    char buffer[1024];

    std::cout << "Nouveau client connecté !" << std::endl;

    while (true) {
        memset(buffer, 0, sizeof(buffer));
        // On lit le message du client
        ssize_t bytesRead = read(fd, buffer, sizeof(buffer) - 1);

        if (bytesRead <= 0) {
            std::cout << "Client déconnecté." << std::endl;
            break;
        }

        // On convertit en string pour manipuler plus facilement
        std::string command(buffer);
        

        // rmv \n and \r becuz pb when using telnet
        if (!command.empty() && command.back() == '\n') command.pop_back();
        if (!command.empty() && command.back() == '\r') command.pop_back();


        std::cout << "Recu : [" << command << "]" << std::endl;

        std::stringstream ss(command);
        std::string action;

        ss >> action; // First mot

        if (action == "LIST"){
            doList(fd);
        }
        else if (action == "UPLOAD"){
            std::string filename;
            int size = 0;

            // filename then size
            if (ss >> filename >> size){
                doUpload(fd, filename, size);
            }
            else{
                std::string msg = "Error: Usage is UPLOAD <filename> <size>\n";
                write(fd, msg.c_str(), msg.size());
            }
        }
        else if (action == "DOWNLOAD"){
            std::string filename;
            if (ss >> filename){
                doDownload(fd, filename);
            }
            else{
                std::string msg = "Error: Usage is DOWNLOAD <filename>\n";
                write(fd, msg.c_str(), msg.size());
            }
        }
        else if (action == "QUIT"){
            break;
        }
        else{
            std::string msg = "Unknown command \n";
            write(fd, msg.c_str(), msg.size());
        }

    }
}


void FTPServer::doList(int clientFD){
    DIR *dir;
    struct dirent *ent; //directory entry
    std::string response = "Files in : " + rootPath + "\n";

    if ((dir = opendir(rootPath.c_str())) != NULL){ // sys call rtrn pointer to dir stream
        while ((ent = readdir(dir)) != NULL){ // rtrn a ptr to nxt entry in the directory
            std::string fname = ent->d_name;
            response += fname + "\n";
        }
        closedir(dir);
        response += "End of List\n";

    }
    else{
        perror("opendir err");
        response = "can not open directory.\n";
    }

    write(clientFD, response.c_str(), response.size());

}


void FTPServer::doUpload(int fd, std::string filename, int filesize) {
    std::cout << "Upload request: " << filename << " (" << filesize << " bytes)" << std::endl;

    // path
    std::string fullPath = rootPath + "/" + filename;
    
    // Open file for writing (Binary mode)
    std::ofstream outfile(fullPath, std::ios::binary);
    if (!outfile.is_open()) {
        std::string msg = "Error: Cannot create file.\n";
        write(fd, msg.c_str(), msg.size());
        return;
    }

    // 3. Send READY signal to client
    std::string msg = "READY\n";
    write(fd, msg.c_str(), msg.size());

    int totalRead = 0;
    char buffer[4096];

    while (totalRead < filesize) {
        int toRead = filesize - totalRead;
        if ((size_t)toRead > sizeof(buffer)) toRead = sizeof(buffer);

        ssize_t r = read(fd, buffer, toRead);

        if (r <= 0) {
            std::cerr << "Error or disconnection during upload." << std::endl;
            break;
        }

        // Write file
        outfile.write(buffer, r);
        totalRead += r;
    }

    outfile.close();
    std::cout << "Upload complete: " << filename << std::endl;

    msg = "OK Upload " + filename + " complete.\n";
    write(fd, msg.c_str(), msg.size());
}

void FTPServer::doDownload(int fd, std::string filename) {
    std::string fullPath = rootPath + "/" + filename;
    
    // Open file at the end (ate) to get the size easily
    std::ifstream infile(fullPath, std::ios::binary | std::ios::ate);

    if (!infile.is_open()) {
        std::string msg = "ERROR File not found\n";
        write(fd, msg.c_str(), msg.size());
        std::cout << "Download failed: File not found (" << filename << ")" << std::endl;
        return;
    }

    // Get file size
    std::streamsize size = infile.tellg();
    
    infile.seekg(0, std::ios::beg);

    std::cout << "Sending file: " << filename << " (" << size << " bytes)" << std::endl;

    // Send (FOUND <size>)
    std::string header = "FOUND " + std::to_string(size) + "\n";
    write(fd, header.c_str(), header.size());

    // Send File 
    char buffer[4096];
    while (!infile.eof()) {
        infile.read(buffer, sizeof(buffer));
        std::streamsize count = infile.gcount(); // How many bytes we read
        
        if (count > 0) {
            write(fd, buffer, count);
        }
    }
    
    std::cout << "Download complete." << std::endl;
}
