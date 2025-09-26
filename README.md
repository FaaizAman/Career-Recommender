# Career-Recommender
The Career Recommender System is a machine learning–based project that predicts a student’s performance and recommends suitable careers based on their academic scores.


## Features

- Predicts student scores using a trained machine learning model.
- Recommends multiple suitable careers based on subject performance.
- Identifies subjects where improvement is needed.
- User-friendly interface for inputting subject scores.

---

## Dataset

- Dataset consists of student scores across various subjects.
- Preprocessing includes cleaning, encoding categorical variables, and feature engineering (e.g., `average_score` column).

---

## Machine Learning Model

- **Algorithm Used:** RandomForestRegressor
- **Performance Metrics:**
  - Mean Absolute Error (MAE): 0.0286
  - R² Score: 0.9553
- The model predicts scores, which are then used for career and learning path recommendations.

---
