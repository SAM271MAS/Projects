# Multi-Threaded C++ Socket Server & FTP/UDP Clients

Developed for a [systems programming course (2025)](https://github.com/yanntm/PSCR-TME) lab, this repository contains several client-server applications built from scratch in C++ using POSIX sockets. It starts with a custom, multi-threaded TCP server designed to safely handle multiple user connections at the same time. Using this foundation, a mini-FTP system was built to allow users to list directory contents (`LIST`), upload files (`UPLOAD`), and download files (`DOWNLOAD`). The project also explores UDP networking by adding two additional tools: a remote storage server for saving and reading simple text variables (`set`/`get`), and a real-time, decentralized group chat application using UDP Multicast.

**Note:** The project files include some sequential naming and repeated setup logic because it was developed step-by-step as a university homework assignment.
