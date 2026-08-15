# Model Evaluation Report

This report summarizes the evaluation metrics for the SLA breach classifier and the Resolution Time regressor models.

## SLA Breach Classifier

We evaluated Logistic Regression and Random Forest models using class weights (`class_weight='balanced'`) to address the class imbalance (minority class: `False` / SLA Breached).

| Metric | Logistic Regression | Random Forest |
| :--- | :--- | :--- |
| **Precision** (Breach) | 0.58 | 0.54 |
| **Recall** (Breach) | 0.43 | **0.52** |
| **F1-Score** (Breach) | 0.50 | **0.53** |
| **ROC-AUC** | 0.8069 | **0.8168** |

### Confusion Matrix (Random Forest)
- **True Negatives** (Breached correctly predicted): 591
- **False Positives** (Breached predicted as Met): 556
- **False Negatives** (Met predicted as Breached): 511
- **True Positives** (Met correctly predicted): 3326

**Chosen Model**: Random Forest.
**Justification**: For SLA breach prediction, the minority class (breaches) is the most important to capture. The Random Forest model achieved a higher recall (0.52 vs 0.43) and F1-score (0.53 vs 0.50) on this minority class, meaning it successfully catches more actual breaches compared to Logistic Regression.

---

## Resolution Time Regressor

We evaluated a Ridge Regression model and a Random Forest Regressor to predict `resolution_time_hours`. 

| Metric | Ridge Regression | Random Forest Regressor |
| :--- | :--- | :--- |
| **MAE** | 267.21 hours | **232.39 hours** |
| **RMSE** | 642.18 hours | **585.54 hours** |
| **R²** | -1.1127 | **-0.7564** |

**Chosen Model**: Random Forest Regressor.
**Justification**: The Random Forest model outperformed Ridge Regression on all metrics, substantially reducing both MAE and RMSE. While R² scores indicate this regression task is inherently difficult with the available creation-time features, Random Forest handles the non-linear time relationships much better than the linear Ridge model.
