# Multi-Protocol Proxy & Relay

A Python-based, multi-threaded TCP/HTTP proxy built using the `socket` and `select` libraries to handle concurrent connections. 

> **Note:** The project files have some repeated code and use names like `ex1_` or `ex2_` because this mini-project was a university homework assignment, and I wrote the code sequentially to follow the logic of the questions.

## Files
* **`ex1_relay.py`**: Base multi-threaded TCP relay.
* **`ex2_cache_relay.py`**: HTTP proxy that caches `GET` requests in memory.
* **`ex2_sniffeur_relay.py`**: Traffic sniffer that logs full request/response payloads in Base64.
* **`ex2_censeur_relay.py`**: Censor proxy that blocks restricted URIs and returns a `403 Forbidden` response.
* **`read_logs.py`**: CLI tool to read and decode the sniffer logs.
* **`ex2_http_server_ia.py` & `ex1_server.py`**: Local testing servers.

