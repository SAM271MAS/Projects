#include "pipe.h"

#include <iostream>
#include <fcntl.h>
#include <unistd.h>
#include <limits.h> // For PIPE_BUF
#include <semaphore.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <cstring>
#include <cerrno>
#include <cstdio>
#include <signal.h>
#include <algorithm>

namespace pr {

// Place this in shared memory !    
struct PipeShm {
    char buffer[PIPE_BUF];
    size_t head; // write position
    size_t tail; // read position
    size_t count; // number of bytes in the pipe
    size_t nbReaders; // number of readers
    size_t nbWriters; // number of writers
    // semaphores
    sem_t semMut;
    sem_t canRead;
    sem_t canWrite;
};

// This is per-process handle, not in shared memory
struct Pipe {
    PipeShm *shm; // pointer to shared memory
    int oflags; // O_RDONLY or O_WRONLY
};

int pipe_create(const char *name) {
    // Construct shared memory name
    
    char shm_name[256];
    // add a '/' at the beginning for shm_open
    snprintf(shm_name, sizeof(shm_name), "/%s", name);

    // Try to create shared memory with O_CREAT|O_EXCL
    int fd = shm_open(shm_name, O_CREAT | O_EXCL | O_RDWR, 0666);
    if(fd == -1){
        perror("shm_open");
        exit(1);
    }
    
    // Set size of shared memory
    if (ftruncate(fd, sizeof(PipeShm)) == -1) {
        perror("ftruncate");
        exit(1);
    }

    // Map the shared memory 
    PipeShm *shm = (PipeShm *) mmap(nullptr, sizeof(PipeShm), PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (shm == MAP_FAILED) {
        perror("mmap");
        exit(1);
    }


    // Initialize the PipeShm structure
    shm->head = 0;
    shm->tail = 0;
    shm->count = 0;
    shm->nbReaders = 0;
    shm->nbWriters = 0;


    // memset(shm, 0, sizeof(PipeShm)); //Redondant

    // Including semaphores

    if (sem_init(&shm->semMut, 1, 1) == -1) { 
        perror("sem_init mutex"); exit(1); 
    }
    if (sem_init(&shm->canRead, 1, 0) == -1) { 
        perror("sem_init canRead"); exit(1); 
    }
    if (sem_init(&shm->canWrite, 1, PIPE_BUF) == -1) { 
        perror("sem_init canWrite"); exit(1); 
    }

    // Unmap and close (setup persists in shared memory)
    close(fd);
    munmap(shm, sizeof(PipeShm));
    
    return 0;
    
}

Pipe * pipe_open(const char *name, int oflags) {
    // Construct shared memory name
    char shm_name[256];
    snprintf(shm_name, sizeof(shm_name), "/%s", name);
    
    // Open shared memory (without O_CREAT)

    int fd = shm_open(shm_name, O_RDWR, 0666); //Read or Write
    if(fd == -1){
        perror("shm_open");
        exit(1); // Retourner NULL en cas d'erreur
    }

    // Map the shared memory
    PipeShm *shm = (PipeShm *) mmap(nullptr, sizeof(PipeShm), PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);

    // Can close fd after mmap

    close(fd);
    if (shm == MAP_FAILED) {
        perror("mmap");
        exit(1);
    }


    // Lock
    if (sem_wait(&shm->semMut) == -1) { //mutex
        perror("sem_wait");
        return nullptr;
    }

    // Increment nbReaders or nbWriters
    if (oflags == O_RDONLY) {
        shm->nbReaders++;
    }
    else if (oflags == O_WRONLY) {
        shm->nbWriters++;
    }

    // Unlock
    if (sem_post(&shm->semMut) == -1) {
        perror("sem_post");
        // On continue quand même, mais c'est grave
    }

    
    // Create and return Pipe handle
    Pipe *handle = new Pipe();
    handle->shm = shm;
    handle->oflags = oflags;

    return handle;
}

ssize_t pipe_read(Pipe *handle, void *buf, size_t count) {
    if (handle == nullptr || handle->oflags != O_RDONLY) {
        errno = EBADF;
        exit(1);
    } else if (count > PIPE_BUF) {
        errno = EINVAL;
        exit(1);
    }

    PipeShm *shm = handle->shm;
    
    // wait until some data available or no writers
    while(true){

        sem_wait(&shm->canRead);
        sem_wait(&shm->semMut);

        if (shm->count > 0 || shm->nbWriters == 0) {
            break; // On garde le mutex verrouillé et on sort pour lire
        }

        sem_post(&shm->semMut);
    }

    // Check if pipe is empty and no writers : EOF
    if (shm->count == 0 && shm->nbWriters == 0) {
        // sem_post(&shm->canRead);
        sem_post(&shm->semMut);
        return 0;
    }
    
    // Read min(count, shm->count) bytes
    // PipeShm *shm = handle->shm;

    size_t to_read = std::min(count, shm->count);
    char *output = (char *)buf;
    
    // Handle circular buffer: may need to copy in two parts
    size_t first_chunk = std::min(to_read, PIPE_BUF - shm->tail);
    memcpy(output, &shm->buffer[shm->tail], first_chunk);
    
    if (first_chunk < to_read) {
        // Wrap around to beginning of buffer
        memcpy(output + first_chunk, &shm->buffer[0], to_read - first_chunk);
    }
    shm->tail = (shm->tail + to_read) % PIPE_BUF;
    shm->count -= to_read;
    // warn other readers/writers if needed
    if (to_read > 0) {
        sem_post(&shm->canWrite);
    }
    if (shm->count > 0 || shm->nbWriters == 0) {
        sem_post(&shm->canRead);
    }
    
    // Fin de la section critique
    sem_post(&shm->semMut);
    
    return to_read;
}

ssize_t pipe_write(Pipe *handle, const void *buf, size_t count) {

    if (handle == nullptr || handle->oflags != O_WRONLY) {
        errno = EBADF;
        exit(1);
    } else if (count > PIPE_BUF) {
        errno = EINVAL;
        exit(1);
    }
    
    PipeShm *shm = handle->shm;
    
    while(true){

        sem_wait(&shm->canWrite);
        sem_wait(&shm->semMut);

        size_t free_space = PIPE_BUF - shm->count;
        
        if (free_space >= count and shm->nbReaders != 0) {
            break; 
        }
        
        sem_post(&shm->semMut);

    }
    
    // Check if no readers => SIGPIPE

    if (shm->nbReaders == 0) {
        sem_post(&shm->semMut);
        sem_post(&shm->canWrite);

        kill(getpid(), SIGPIPE);
        return -1;

    }
    
    // Write count bytes
    const char *input = (const char *)buf;
    
    // Handle circular buffer: may need to copy in two parts
    size_t first_chunk = std::min(count, PIPE_BUF - shm->head);
    memcpy(&shm->buffer[shm->head], input, first_chunk);
    
    if (first_chunk < count) {
        // Wrap around to beginning of buffer
        memcpy(&shm->buffer[0], input + first_chunk, count - first_chunk);
    }
    
    shm->head = (shm->head + count) % PIPE_BUF;
    shm->count += count;
    
    // warn other readers/writers if needed
    if (shm->count > 0) {
        sem_post(&shm->canRead);
    }

    if (shm->count < PIPE_BUF) {
        sem_post(&shm->canWrite);
    }
    
    sem_post(&shm->semMut);
 
    
    return count;
}

int pipe_close(Pipe *handle) {
    if (handle == nullptr) {
        errno = EBADF;
        exit(1);
    }
    
    PipeShm *shm = handle->shm;

    
    sem_wait(&shm->semMut);
    // Decrement reader or writer count
    if(handle->oflags == O_RDONLY){
        shm->nbReaders--;
    }
    if(handle->oflags == O_WRONLY){
        shm->nbWriters--;
    }

    // Warn other process as needed (e.g. if last reader/writer)
    if(shm->nbWriters == 0){
        sem_post(&shm->canRead);

    }
    if(shm->nbReaders == 0){
        sem_post(&shm->canWrite);

    }
    
    sem_post(&shm->semMut);
    // Unmap memory
    munmap(shm, sizeof(PipeShm));

    // Free handle
    delete handle;
    
    return 0;
}

int pipe_unlink(const char *name) {
    // Construct shared memory name
    char shm_name[256];
    snprintf(shm_name, sizeof(shm_name), "/%s", name);

    int fd = shm_open(shm_name, O_RDWR, 0666); //Read or Write
    if(fd == -1){
        perror("shm_open");
        exit(1); // Retourner NULL en cas d'erreur
    }

    // Map the shared memory
    PipeShm *shm = (PipeShm *) mmap(nullptr, sizeof(PipeShm), PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);

    // Can close fd after mmap

    close(fd);
    if (shm == MAP_FAILED) {
        perror("mmap");
        exit(1);
    }
    sem_destroy(&shm->semMut);
    sem_destroy(&shm->canWrite);
    sem_destroy(&shm->canRead);
    
    // Unlink shared memory (this also destroys the embedded semaphores)
    munmap(shm, sizeof(PipeShm));
    shm_unlink(shm_name);
    
    return 0;
}

} // namespace pr

