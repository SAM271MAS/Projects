#include <bits/stdc++.h> 
#include <stdlib.h> 
#include <unistd.h> 
#include <string.h> 
#include <sys/types.h> 
#include <sys/socket.h> 
#include <arpa/inet.h> 
#include <netinet/in.h> 

#define MAXLINE 1024


int main(int argc, char **argv){

    if (argc != 2){
        std::cout << "Usage ./" << argv[0] << " port" << std::endl;
        exit(1);
    }

    int port = std::stoi(argv[1]);
    int sockfd;

    
    struct sockaddr_in server_add = {0};

    if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0){
        perror("socket err");
        exit(1);
    }

    server_add.sin_family = AF_INET;
    server_add.sin_addr.s_addr = INADDR_ANY;
    server_add.sin_port = htons(port);

    if (bind(sockfd, (struct sockaddr *)&server_add, sizeof(server_add)) < 0){
        perror("bind err");
        exit(1);
    }

    std::cout << "UDP Server running on : " << port << std::endl;

    std::unordered_map<std::string, std::string> env;

    char buffer[MAXLINE];
    struct sockaddr_in client_add = {0};
    socklen_t client_len = sizeof(client_add);

    while(true){
        memset(buffer, 0, MAXLINE);

        ssize_t n = recvfrom(sockfd, buffer, MAXLINE - 1, 0, (struct sockaddr*)&client_add, &client_len);

        if (n <= 0)
            continue;
        
        std::string msg(buffer);

        if (!msg.empty() && msg.back() == '\n')
            msg.pop_back();

        std::cout << "recvd: " << msg << std::endl;

        std::string response;



        // Quit
        if (msg[0] == 'Q'){
            std::cout << "server terminating" << std::endl;
            break;
        }
        //set
        else if (msg[0] == 'S'){
            size_t key_start = 1;

            if(msg.length() > 1 && msg[1] == ' ')
                key_start = 2;

            size_t space_pos = msg.find(' ', key_start); // if found rtrn the index where the match starts
            if (space_pos != std::string::npos){ // the largest possible value of that type (is retrnd by find if not found)
                std::string key = msg.substr(1, space_pos - 1);
                std::string value = msg.substr(space_pos + 1);

                env[key] = value;

                response = "OK: " + key + " set to " + value + "\n";

            }
            else{
                response = "Error usage S key value\n";
            }
        }
        // GET
        else if (msg[0] == 'G'){
            std::string key = msg.substr(1);
            if (env.find(key) != env.end()){
                response = key + " = " + env[key] + "\n";
            }
            else{
                response = "Error " + key + " not found\n";
            }
        }
        else{
            response = "Error format\n";
        }
        sendto(sockfd, response.c_str(), response.size(), 0, (struct sockaddr*)&client_add, client_len);
    }

    return 0;


}
