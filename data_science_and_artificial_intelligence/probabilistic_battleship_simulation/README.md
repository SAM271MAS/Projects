# Probabilistic Battleship Simulation & Bayesian Search

## Overview

This project explores the mathematical and probabilistic foundations of a grid-based naval game and 2D object search. It features exact combinatorial calculations for board configurations, strategy simulations, and a Bayesian search algorithm designed to locate targets based on dynamically updating probability distributions.

## Key Features

* **Combinatorial Board Modeling:** Utilizes recursive algorithms to verify placements and calculate the total number of valid boat configurations on a grid.
* **Algorithmic Targeting Strategies:** Simulates automated matches to evaluate different targeting algorithms. It compares the expected number of shots required to win using Random, Heuristic, Naive Probabilistic, and Monte Carlo approaches.
* **Bayesian Object Search:** A 2D simulation inspired by the historical search for the USS Scorpion. It initializes prior probability distributions (Uniform, Corners, Center, Edges, Random) and dynamically updates the grid's probability mass using Bayes' theorem after successful or failed detection attempts.

