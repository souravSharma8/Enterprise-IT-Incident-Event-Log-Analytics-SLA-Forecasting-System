from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

def create_preprocessing_pipeline() -> ColumnTransformer:
    """
    Creates the scikit-learn preprocessing pipeline for the models.
    Numeric features: StandardScaler
    Categorical features: OneHotEncoder (ignoring unknown categories)
    """
    numeric_features = ['opened_hour', 'day_of_week', 'month']
    categorical_features = [
        'contact_type', 'location', 'category', 'subcategory', 
        'u_symptom', 'impact', 'urgency', 'priority', 
        'caller_id', 'opened_by', 'assignment_group', 'assigned_to'
    ]
    
    numeric_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown='ignore', sparse_output=True)
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ],
        remainder='drop' # Drop 'number' and any targets passed accidentally
    )
    
    return preprocessor

def get_model_pipeline(model) -> Pipeline:
    """
    Wraps a model with the preprocessing pipeline.
    """
    preprocessor = create_preprocessing_pipeline()
    return Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', model)
    ])
