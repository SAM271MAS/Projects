# Academic Mini-Projects Collection

This repository contains three academic mini-projects developed in C and Java. They focus on object-oriented programming, memory management, and data structure performance analysis.


## Library Management & Data Structure Analysis

**Language:** C

This project implements a command-line library management system to compare the search performance of singly linked lists against hash tables with chaining. It includes a benchmarking module that measures CPU execution times for search operations across datasets of varying sizes.

* **Build:** `make`
* **Run:** `./main <nom_du_fichier> <nb_lignes>` (e.g., `./main GdeBiblio.txt 1000`)


## Predator-Prey Ecosystem Simulation

**Language:** C

A discrete-time simulation of a predator-prey ecosystem on a 2D toroidal grid. It uses custom dynamic linked lists to track moving animal entities.

* **Build:** `make`

* **Run:** `./ecosys` (main simulation) or `./tests_ecosys` / `./tests_ecosys2` (function tests)


## Object-Oriented Grid Simulation

**Language:** Java

A 2D grid simulation where an agent navigates the environment to collect jewels and interact with guards. The project utilizes class inheritance to define entity types and implements custom exception handling to validate grid boundaries and movements. A logging module records step-by-step state changes to a local file.

* **Build:** `javac *.java`
* **Run:** `java TestSimulation`
