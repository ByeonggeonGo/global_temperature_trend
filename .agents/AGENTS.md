# Project Development and Upload Rules
Rules to be strictly followed during modification and deployment of this project.

- **Global Platform English Rule**:
  - All public code comments, Jupyter Notebook (.ipynb) text descriptions (including Markdown cells), and the main project document (README.md) shared on GitHub and Kaggle must be written in **English** as they target a global audience.
  - Local reports (e.g., analysis_results.md) and agent chat conversations remain in Korean.
- **Kaggle Docker Verification Rule**:
  - Prior to pushing notebook updates to Kaggle, you must run the local Docker verification script (`.\test_in_docker.ps1`) to ensure there are no out-of-order execution bugs or cell execution failures.
