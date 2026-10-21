#include <fcntl.h>
#include <unistd.h>
#include <iostream>
#include <cstring>

int main(int argc, char *argv[]) {
    const int BUFFER_SIZE = 4096;

    char buffer[BUFFER_SIZE];
    ssize_t bytesRead;

    if (argc == 1){ // no input
        std::string line;

        while (std::getline(std::cin, line))
            std::cout << line << std::endl;

        return 0;
    }

    for (int i = 1; i < argc; i++){
        int fd = open(argv[i], O_RDONLY);
        
        if (fd == -1){
            std::cout << "file not found continuing to next file" << std::endl;
            continue;
        }

        while((bytesRead = read(fd, buffer, sizeof(buffer))) > 0){
            write(STDERR_FILENO, buffer,  bytesRead);
        }

        close(fd);
   }

}
