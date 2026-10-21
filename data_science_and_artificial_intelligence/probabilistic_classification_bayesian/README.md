# Probabilistic Classification & Bayesian Networks

## Overview
This project explores statistical and probabilistic classification methods, specifically focusing on Bayesian networks. Using a medical dataset (Heart Disease/Cleveland Database), the project implements a hierarchy of custom classifiers from scratch to predict disease presence based on patient attributes. It progresses from simple baseline models to Tree-Augmented Naïve Bayes (TAN) networks utilizing conditional mutual information.

## Key Features
All classifiers are built from scratch in Python, inheriting from a custom `AbstractClassifier` interface.

*   **Baseline Classifiers:** 
    *   `APrioriClassifier`: Predicts the majority class based purely on prior probabilities.
*   **2D Probabilistic Classifiers:** 
    *   `ML2DClassifier`: Uses Maximum Likelihood (ML) estimation on a single feature.
    *   `MAP2DClassifier`: Uses Maximum A Posteriori (MAP) estimation.
*   **Naïve Bayes Classifiers:** 
    *   `MLNaiveBayesClassifier` & `MAPNaiveBayesClassifier`: Assumes conditional independence between all features given the target.
    *   **Feature Selection:** Includes "Reduced" versions of Naïve Bayes that utilize Chi-Square independence tests to prune irrelevant nodes from the network.
*   **Tree-Augmented Naïve Bayes (TAN):** 
    *   `MAPTANClassifier`: Overcomes the strict independence assumption of Naïve Bayes by allowing features to have one additional parent attribute.
    *   Calculates Conditional Mutual Information matrices and uses Kruskal's algorithm to generate a Maximum Spanning Tree (MST), orienting the graph structure via Depth-First Search (DFS).

