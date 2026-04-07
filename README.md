# Personalized Food Recommendation System

> **A context-aware, hybrid recommendation engine demonstrating Neural Collaborative Filtering and Matrix Factorization architectures.**

## 📖 Overview

Most food delivery platforms prioritize operational convenience—showing what is open or popular—rather than truly understanding user intent. This leads to repetitive, non-personalized experiences.

This project implements a **personalized, context-aware food recommendation system** designed to solve this problem. Instead of being just another food delivery clone, this system focuses on the **architectural patterns** of modern recommender systems. It explores how to combine user interactions (implicit signals like clicks/orders) with explicit feedback (ratings) to adapt recommendations dynamically.

## 🎯 Design Philosophy

The core design philosophy is **"Simple Models, Strong Architecture."**
The system is built as a modular prototype to demonstrate:

*   **Hybrid Recommendation Strategy**: Combines the strengths of multiple approaches to handle different scenarios (e.g., cold-start vs. established users).
*   **Separation of Concerns**: Decouples data processing, model training (offline), and recommendation serving (online).
*   **Feedback Loops**: Continuously refines the model using identifying interaction logs.

## 🧠 Recommendation Architecture

This system uses a multi-tiered approach to generate recommendations:

1.  **Neural Collaborative Filtering (NCF)**:
    *   *Primary Model*: Uses deep learning (PyTorch) to learn non-linear user-item interactions.
    *   Generates highly personalized "For You" lists for active users.

2.  **Matrix Factorization (SVD)**:
    *   *Supporting Model*: A classic baseline used for comparison and fallback.
    *   Decomposes the interaction matrix to find latent factors.

3.  **Content-Based Similarity**:
    *   *Cold-Start Handler*: Suggests items similar to what a user has liked in the past (based on cuisine, price, etc.).
    *   Crucial for new users or items with no interaction history.

4.  **Popularity & Context**:
    *   *Baseline*: Trending items based on global popularity.
    *   *Context*: Basic filtering based on availability and logic.

## ✨ Features

- **Personalized Dashboard**: "For You" (NCF/MF), "Trending", and "Based on Taste".
- **Interactive Simulation**: Admin capabilities to simulate user traffic, generate synthetic data, and visualize matrix sparsity.
- **Implicit & Explicit Feedback**: Handles both passive signals (clicks, views) and active signals (ratings).
- **Admin Analytics**: Visualize system performance and data distribution.
- **Prototype UI**: Built with Streamlit for rapid interactive demonstration.

## 🛠️ Tech Stack

*   **Frontend**: Streamlit
*   **Core Logic**: Python 3.8+
*   **Machine Learning**: PyTorch (Neural Networks), Scikit-Learn (Matrix Factorization)
*   **Data Processing**: Pandas, NumPy
*   **Data Storage**: Synthetic dataset generation (for prototyping)

## 🚀 Getting Started

### Prerequisites

*   Python 3.8+
*   [Pip](https://pip.pypa.io/en/stable/)

### Installation

1.  Clone the repository.
2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Usage

Run the Streamlit application:

```bash
fastapi dev backend/main.py
```

*   **User Login**: Log in as any user (e.g., User ID `1`, `2`, etc.) to browse and interact.
*   **Admin Access**: Log in with User ID `admin` (or access the Admin tab) to view analytics and control the simulation.

## 📜 License

See [LICENSE](LICENSE) file.
