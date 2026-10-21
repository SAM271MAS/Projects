#include <iostream>
#include "signal.h"
#include <sys/wait.h>
#include "util/rsleep.h"

volatile sig_atomic_t PV = 3; // Que fait volatile
/*
* sig_atomic_t: This ensures that reading or writing to the variable happens in one single CPU instruction. 
* It prevents the variable from being half-written when a signal arrives.
*/


struct sigaction sa;

void handler(int sig){ //Never use printf or std::cout in a signal handler
    if (sig == SIGUSR1)
        PV--;
}


void attaque(pid_t adversaire){

    sa.sa_handler = handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;

    sigaction(SIGUSR1, &sa, NULL);

    if (kill(adversaire, SIGUSR1) == -1){

        if (errno == ESRCH)
            exit(0);
        else{
            perror("err kill");
            exit(1);
        }
    }
    pr::randsleep();
}

void defense(){
    struct sigaction sa;

    sa.sa_handler = SIG_IGN;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;

    sigaction(SIGUSR1, &sa, NULL);
    pr::randsleep();

}

void pare_handler(int sig) {
    write(STDOUT_FILENO, "Coup paré !\n", 13); // Write is safe inside handlers async-signal-safe
}

void defense_luke() {
    struct sigaction s_pare;

    // Positionner un handler qui affiche "coup paré" avec sigaction
    s_pare.sa_handler = pare_handler;
    sigemptyset(&s_pare.sa_mask);
    s_pare.sa_flags = 0;

    if (sigaction(SIGUSR1, &s_pare, NULL) < 0) {
        perror("sigaction pare");
        exit(1);
    }

    // masquer les signaux avec sigprocmask
    sigset_t mask_bloque, mask_vide;

    sigemptyset(&mask_bloque);
    sigaddset(&mask_bloque, SIGUSR1);
    
    sigprocmask(SIG_BLOCK, &mask_bloque, NULL);

    // s’endormir pendant une durée aléatoire avec randsleep
    pr::randsleep(); // If SIGUSR1 arrives here, it becomes pending

    // invoquer sigsuspend pour tester si une attaque a eu lieu,
    sigemptyset(&mask_vide);
    sigsuspend(&mask_vide);


    // restaurer le masque (vide) avec sigprocmask
    sigprocmask(SIG_UNBLOCK, &mask_bloque, NULL);
}

void luke_combat(pid_t vador){
    while(PV > 0){
        defense_luke();
        attaque(vador);
        if (PV <= 0){
            std::cout << "Défaite de " << getpid() << std::endl;
        }
    }
}

void vador_combat(pid_t luke){
    while (PV >0){
        defense();
        attaque(luke);

        if (PV <= 0){
            std::cout << "Défaite de Vador pid : " << getpid() << std::endl;
            break;
        }
        pid_t res = waitpid(luke, nullptr, WNOHANG); //non bloquant

        if (res == luke){
            std::cout << "Vador a vu la mort de luke" << std::endl;
            break;
        }
        else if (res == -1){
            perror("waitpid err");
            exit(1);
        }

    }
}



// void combat(pid_t adversaire){
//     pid_t own_pid = getpid();
//
//     while(PV > 0){
//         std::cout << "Phase def, je suis : " << own_pid << std::endl;
//         defense();
//
//         std::cout << "Phase atk, je suis : " << own_pid << std::endl;
//         attaque(adversaire);
//
//         if (PV <= 0){
//             std::cout << "Défaite de : " << own_pid << std::endl;
//         }
//         else{
//             std::cout << "PV de " << own_pid << "restants : " << PV << std::endl;
//         }
//     }
// }
/*
 */

int main() {
    // std::cout << "Placeholder for combat" << std::endl;

    pid_t vador = getpid();
    std::cout << "Vador pid : " << vador << std::endl;

    pid_t luke = fork();
    
    if (luke < 0){
        perror("err luke");
        exit(1);
    }

    if (luke == 0){ //fils == luke
        std::cout << "luke pid : " << getpid() << std::endl;
        luke_combat(vador);
    }

    else{ //pere == Vador
        vador_combat(luke);

    }
    return 0;
}

