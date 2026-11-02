# 🎬 CineMatch AI — Intelligent Movie Recommendation System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Machine Learning](https://img.shields.io/badge/ML-Cosine%20Similarity%20%7C%20TF--IDF-orange.svg)](https://scikit-learn.org/)
[![NumPy](https://img.shields.io/badge/NumPy-Vectorized%20Math-013243.svg?logo=numpy&logoColor=white)](https://numpy.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458.svg?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![UI](https://img.shields.io/badge/UI-Netflix%20Dark%20Cinematic-E50914.svg)](https://github.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An advanced, full-stack **Hybrid Movie Recommendation Engine** inspired by streaming platforms like Netflix. Built with a vectorized mathematical core implementing **Cosine Similarity**, **TF-IDF Feature Extraction**, and **Collaborative Filtering** on user-item interaction matrices. Features a responsive, cinematic dark-mode web application with real-time autocomplete, multi-movie preference fusion, dynamic match scoring, and genre categorization.

---

## 🌟 Key Features

- **🚀 Hybrid Recommendation Fusion**:
  - Combines **Collaborative Filtering** (User-Item interaction vectors) with **Content-Based Filtering** (Genre, Director, and Plot Summary TF-IDF vectors).
  - Dynamically weights both signals (55% Content + 45% Collaborative) to mitigate cold-start and sparsity challenges.
- **🎯 Dynamic Match Score Percentage**:
  - Computes cosine vector distances and maps them into intuitive match confidence badges (e.g., `🔥 96% Match`).
- **🔍 Real-Time Intelligent Autocomplete**:
  - Instant client-side search across movie titles with keyboard navigation and quick multi-movie selection.
- **🎨 Netflix Cinematic Dark Mode UI**:
  - Responsive, fluid poster grid with hover zoom effects, genre tags, director metadata, and modal popups for plot overviews.
  - "More Like This" one-click button on every card to explore recommendation chains in real time.
- **⚡ Zero-Heavy-Dependencies Architecture**:
  - Uses a lightweight, high-performance web server built with standard Python libraries.
  - No bloated frameworks or compilation headaches: works instantly across Windows, macOS, and Linux.

---

## 📐 Mathematical Formulation

### 1. Cosine Similarity Vector Metric
Cosine similarity measures the cosine of the angle between two non-zero vectors in an $n$-dimensional inner product space:

$$\text{Similarity}(\mathbf{A}, \mathbf{B}) = \cos(\theta) = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\|_2 \|\mathbf{B}\|_2} = \frac{\sum_{i=1}^{n} A_i B_i}{\sqrt{\sum_{i=1}^{n} A_i^2} \sqrt{\sum_{i=1}^{n} B_i^2}}$$

### 2. Content-Based TF-IDF Feature Representation
For each movie $m$, a metadata soup is constructed from genres, director, and plot synopsis:

$$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \left( \ln\left(\frac{1 + |D|}{1 + |\{d \in D : t \in d\}|}\right) + 1 \right)$$

### 3. Collaborative User-Item Matrix
User rating preferences are structured into a sparse matrix $R \in \mathbb{R}^{M \times U}$, where row vectors represent movie profiles across the collective audience, identifying latent behavioral correlation between titles.

---

## 📂 Project Structure

```text
CineMatch-Movie-Recommender/
├── app.py                  # Web server & REST API endpoints
├── recommender.py          # Vectorized Hybrid Recommendation Engine
├── requirements.txt        # Minimal dependencies (pandas, numpy)
├── run.bat                 # Windows 1-click launcher
├── run.ps1                 # PowerShell 1-click launcher
├── .gitignore              # Clean repository filter
├── README.md               # Documentation & architecture guide
├── data/
│   ├── movies.csv          # Curated catalog (posters, genres, synopsis)
│   └── ratings.csv         # User interaction ratings matrix
├── static/
│   ├── css/
│   │   └── style.css       # Netflix cinematic dark-mode stylesheet
│   └── js/
│       └── app.js          # Interactive client logic & API bindings
└── templates/
    └── index.html          # Semantic HTML5 single-page application
```

---

## 🚀 Quick Start Guide

### Option 1: 1-Click Launch (Windows)
Double-click `run.bat` or right-click `run.ps1` and select **Run with PowerShell**.

### Option 2: Running via VS Code / Terminal
1. Open the project folder in **VS Code**.
2. Open the terminal (`Ctrl + ~` or Terminal -> New Terminal).
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python app.py
   ```
5. Open `http://localhost:5000` in your browser.

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
