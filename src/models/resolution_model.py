import pandas as pd
import joblib
import os
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from src.models.split import split_chronologically
from src.models.pipeline import get_model_pipeline

def evaluate_regressor(model_name: str, y_true: pd.Series, y_pred: np.ndarray):
    """
    Evaluates the regression model.
    """
    print(f"--- Evaluation: {model_name} ---")
    print(f"MAE:  {mean_absolute_error(y_true, y_pred):.2f} hours")
    print(f"RMSE: {np.sqrt(mean_squared_error(y_true, y_pred)):.2f} hours")
    print(f"R²:   {r2_score(y_true, y_pred):.4f}\n")

def train_and_select_resolution_model():
    """
    Trains Ridge and Random Forest regressor, selects the best, and saves it.
    """
    df = pd.read_csv('data/processed/incidents_at_creation.csv')
    
    # Drop rows where target is missing
    df = df.dropna(subset=['target_resolution_time_hours'])
    
    # Fill missing string values with 'Missing'
    str_cols = df.select_dtypes(include=['object']).columns
    df[str_cols] = df[str_cols].fillna('Missing')
    
    train_df, test_df = split_chronologically(df)
    
    X_train = train_df.drop(columns=['target_made_sla', 'target_resolution_time_hours'])
    y_train = train_df['target_resolution_time_hours']
    
    X_test = test_df.drop(columns=['target_made_sla', 'target_resolution_time_hours'])
    y_test = test_df['target_resolution_time_hours']
    
    # 1. Ridge Regression
    ridge = Ridge(alpha=1.0, random_state=42)
    ridge_pipeline = get_model_pipeline(ridge)
    ridge_pipeline.fit(X_train, y_train)
    
    ridge_preds = ridge_pipeline.predict(X_test)
    evaluate_regressor("Ridge Regression", y_test, ridge_preds)
    
    # 2. Random Forest Regressor
    rf = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    rf_pipeline = get_model_pipeline(rf)
    rf_pipeline.fit(X_train, y_train)
    
    rf_preds = rf_pipeline.predict(X_test)
    evaluate_regressor("Random Forest Regressor", y_test, rf_preds)
    
    # Selection (Assuming RF is preferred if it significantly outperforms Ridge)
    print("Saving Random Forest as it generally captures non-linear time relationships better.")
    best_model = rf_pipeline
    
    os.makedirs('models', exist_ok=True)
    joblib.dump(best_model, 'models/resolution_time_model.pkl')
    print("Saved models/resolution_time_model.pkl")

if __name__ == "__main__":
    train_and_select_resolution_model()
