#include <iostream>
#include <string>
#include <vector>
#include <sstream>
#include <unistd.h>
#include <sys/wait.h>
#include <signal.h>
#include <cstring>
#include <cstdlib>

// Custom mystrdup : allocates with new[], copies string (avoid strdup and free)
char* mystrdup(const char* src);

volatile sig_atomic_t new_proc_pid = 0;

void handler(int sig){
    if ((sig==SIGINT) && (new_proc_pid != 0)){
        kill(new_proc_pid, sig);
        char msg[] = "Handler : fils arrêté par un signal\n";
        write(STDOUT_FILENO, msg, sizeof(msg) - 1);
    }
}

int main() {
    std::string line;

    struct sigaction sa;

    sa.sa_handler = handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;

    if (sigaction(SIGINT, &sa, nullptr) == -1){
        perror("sigaction err");
        exit(1);
    }



    while (true) {
        std::cout << "mini-shell> " << std::flush;
        if (!std::getline(std::cin, line)) {
            std::cout << "\nExiting on EOF (Ctrl-D)." << std::endl;
            break;
        }

        if (line.empty()) continue;

        // Simple parsing: split by spaces using istringstream
        std::istringstream iss(line);
        std::vector<std::string> args;
        std::string token;
        while (iss >> token) {
            args.push_back(token);
        }
        if (args.empty()) continue;

        // Prepare C-style argv: allocate and mystrdup
        char** argv = new char*[args.size()];
        for (size_t i = 0; i < args.size(); ++i) {
            argv[i] = mystrdup(args[i].c_str());
        }


        if (strcmp(argv[0], "exit") == 0){
            break;
        }

        new_proc_pid = fork();
        if (new_proc_pid == -1){
            perror("fork err");
            exit(1);
        }
        else if (new_proc_pid == 0){ // fils
            std::cout << "hello from fils" << std::endl;
            execvp(argv[0],  argv);
            perror("execvp failed");
            exit(1);
        }
        // pere

        int status;
        while (waitpid(new_proc_pid, &status, 0) == -1) { 
            if (errno == EINTR) {
                continue; 
            } else {
                perror("wait_pid err");
                exit(1);
            }
        }

        if (WIFEXITED(status)){
            std::cout << "Pere : fils a réussi et est terminé" << std::endl;
        }
        else if (WIFSIGNALED(status)){
            std::cout << "Pere : fils est terminé par signal" << std::endl;
        }
        new_proc_pid = 0;

        // cleanup argv allocations
        for (size_t i = 0; i < args.size(); ++i) {
            delete[] argv[i];
        }
        delete[] argv;
    }
    return 0;
}



char* mystrdup(const char* src) {
    if (src == nullptr) return nullptr;
    size_t len = strlen(src) + 1;  // +1 for null terminator
    char* dest = new char[len];
    memcpy(dest, src, len);  // Or strcpy if preferred
    return dest;
}
