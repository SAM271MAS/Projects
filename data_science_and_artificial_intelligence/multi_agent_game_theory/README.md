# Multi-Agent Restaurant Game & Strategy Evaluation


## Description
This project was developed during the "Intelligence Artificielle et Jeux" course and is built on the pySpriteWorld simulator. It simulates a daily routine where 8 independent agents compete to secure a meal at one of 5 limited-capacity restaurants. The project focuses on decision-making under uncertainty, requiring agents to navigate the environment using A* pathfinding while adapting to the behaviors of competing players. 

Multiple strategic profiles were implemented, ranging from fixed reactive behaviors (Stochastic, Stubborn) to advanced history-based game theory learning (Fictitious Play, Regret-Matching). The agents must also decide whether to optimize their direct path to a restaurant or detour to collect randomly spawned "fast-pass" tickets that grant priority service. Finally, the strategies were benchmarked in an automated 1-vs-7 tournament matrix to analyze strategy dominance and individual versus collective gains.

## Acknowledgements & Included Framework
This repository includes the pySpriteWorld graphics module and the search grid module, developed by Professors Yann Chevaleyre and Nicolas Bredeche.

The custom contributions in this repository are localized to the strategy implementations, benchmarking suite, and game loop logic found in `src/main.py`.

## How to Run
To run the simulations:

```bash
# Run the primary simulation with standard GUI
python3 src/main.py 

