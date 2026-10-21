#include <cstring>
#include <iostream>
#include <cstdio>
#include <cstdlib>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>


int main(int argc, char **argv) {

    // Parse command line arguments: find the pipe separator "|"
    // Format: ./pipe cmd1 [args...] | cmd2 [args...]
    int i = 1;
    
    for (i = 1; i < argc; i++){
        if (std::strcmp(argv[i], "|") == 0){
            argv[i] = nullptr;
            break;
        }
    }

    // Create a pipe for inter-process communication
    int fd[2];
    pipe(fd);

    // Fork the first child process ; child redirects out to write end of pipe, then exec
    pid_t pid1 = fork();

    if (pid1 == -1){
        perror("err fork");
            return 1;
    }

    if (pid1 == 0){ // fils 1 (commande 1)
        close(fd[0]); // fermer lecture

        dup2(fd[1], STDOUT_FILENO);
        execvp(argv[1], argv + 1);

        perror("err execvp");
        exit(1);
    }
    // Fork the second child process ; child redirects in from read end of pipe, then exec

    pid_t pid2 = fork();

    if (pid2 == -1){
        perror("err fork\n");
            exit(1);
    }

    if (pid2 == 0){ // fils 2 (commande 2)
        close(fd[1]); // fermer écriture

        dup2(fd[0], STDIN_FILENO);
        execvp(argv[i + 1], argv + i + 1);

        perror("err execvp");
        exit(1);
    }

    close(fd[0]);
    close(fd[1]);

    // Wait for children to finish
    wait(0);
    wait(0);

    return 0;
}
