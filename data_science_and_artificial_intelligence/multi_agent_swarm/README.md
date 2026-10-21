# Multi-Agent Robot Coordination System
This project was developed as part of the "Cloud et Réseaux Virtuels" (CRV) course for the "Algorithmique embarquée" module.

## Overview
This repository contains a control system for a team of autonomous robots operating within the Simovies 2D simulation environment. The architecture is built upon Multi-Agent Systems (MAS) and the Actor Model to asynchronously coordinate three main combat robots and two secondary robots. The primary objective was to design, implement, and benchmark control strategies to maximize the team's immobilization points against opposing teams.

## Architecture & Strategy
Robot behaviors are strictly governed by Finite State Machines (FSMs) implemented in Java. The team is divided into two distinct roles:

* **Secondary Robots:** Execute a point-denial strategy. They calculate the shortest path to the map's extremities and park themselves permanently to avoid friendly fire and prevent becoming physical obstacles.
* **Main Robots:** Utilize a dynamic positioning system that dictates movement based on a three-tier targeting priority. They evaluate targets using direct radar detection (Priority 1), swarm communication via asynchronous message broadcasting (Priority 2), and a default zone-sweeping fire mode (Priority 3).

## Benchmarking
To measure performance without manual observation, a Bash script (`benchmark.sh`) was developed. It utilizes `xvfb-run` to execute the simulator in a headless virtual environment, automatically parsing match logs to extract and compare the Kill/Death ratios of different algorithms.

