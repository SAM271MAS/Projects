# Agroecological Farm Simulation & Spatial Modeling

## Overview

This project applies statistical analysis, stochastic simulations, and spatial algorithmic modeling to evaluate the viability of diversified micro-farms. It assesses intercropping efficiency through experimental data, simulates the economic constraints of automated crop rotations, and models dynamic 2D plant growth.

## Project Modules

The project logic is modularized into three Python scripts:

* **Intercropping Yield Analysis (`session1.py`):** Used to calculate Land Equivalent Ratios (LER) for evaluating crop synergies. It utilizes linear regression fitting, variance analysis, Z-test hypothesis testing, and network graph clustering to isolate highly synergistic crops.
* **Micro-Farm Economic Simulation (`session2.py`):** Used to automate the generation of diversified crop baskets that meet strict monthly harvest and diversity constraints. It evaluates farm viability by computing expected workloads and revenues via log-normal probability distributions.
* **Spatial Modeling & KD-Trees (`session3.py`):** Used to simulate dynamic 2D crop planting driven by a Poisson process. A custom KD-Tree data structure was implemented to efficiently calculate nearest-neighbor distances and prevent plant collisions, outputting automated time-lapse animations of the field.

## Data Sources

The data for this project is not published in this repository. The analytical models were applied to datasets from the following sources:

* **Intercropping Data:** Global datasets compiling experimental horticulture yields for sole versus intercropped planting setups. These datasets originate from two publications:
* Li, C., Stomph, T. J., Makowski, D., Li, H., Zhang, C., Zhang, F., & van der Werf, W. (2023). The productive performance of intercropping. Proceedings of the National Academy of Sciences, 120(2), e2201886120.
* Paut, R., Garreau, L., Ollivier, G., Sabatier, R., & Tchamitchian, M. (2024). A global dataset of experimental intercropping and agroforestry studies in horticulture. Scientific Data, 11(1), 5.
* **Micro-Farm Economics Data:** Derived from Kevin Morel's thesis, containing over 1,000 crop cycles, monthly diversity criteria, and economic parameters (price per kg, expected workload).
