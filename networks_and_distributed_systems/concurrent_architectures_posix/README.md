# Concurrent Architectures & POSIX Systems Programming

This repository contains a collection of low-level system operations and concurrent architectures implemented across a series of lab assignments. It was developed during the [PSCR course (2025)](https://github.com/yanntm/PSCR-TME).

Base scaffolds, testing utilities, and certain corrections within this repository were provided by our Professors as part of the course materials.

## Repository Structure

The repository is divided into individual modules (TMEs):

* **TME3: Concurrency & Data Races**
Explores multi-threading contention by computing word frequencies in large text datasets. Features custom lock-free atomic linked lists and thread-safe hash maps.
* **TME4: Pipeline Architecture & Blocking Queues**
Implements a multi-threaded image processing pipeline using custom bounded blocking queues to balance CPU-bound rendering and I/O-bound disk operations.
* **TME5: Thread Pools & Task Parallelization**
Parallelizes a custom 3D ray tracer. Compares naive thread-per-pixel/row allocations against an optimized custom thread pool implementation.
* **TME6: Process Management & Signals**
Demonstrates process lifecycles and asynchronous signal handling (`SIGUSR1`, `SIGINT`). Features a custom POSIX mini-shell.
* **TME7: POSIX File I/O & Serialization**
Features a binary serialization engine for cyclic object graphs utilizing direct POSIX file I/O operations, alongside a basic unnamed pipe simulator.
* **TME8: IPC via Shared Memory & Semaphores**
Simulates named pipes from scratch using POSIX shared memory and POSIX semaphores to manage safe, cross-process data streams.

