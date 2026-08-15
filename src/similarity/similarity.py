import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import OneHotEncoder

class IncidentSimilarityEngine:
    """
    Engine to find similar historical incidents based on structured categorical attributes.
    """
    def __init__(self):
        self.encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=True)
        self.nn = NearestNeighbors(metric='cosine', algorithm='brute')
        self.features = ['category', 'subcategory', 'u_symptom', 'impact', 'urgency', 'location', 'assignment_group']
        self.historical_data = None
        
    def fit(self, df: pd.DataFrame):
        """
        Fits the engine on historical data.
        """
        self.historical_data = df[['number'] + self.features].copy()
        self.historical_data[self.features] = self.historical_data[self.features].fillna('Missing')
        
        encoded_data = self.encoder.fit_transform(self.historical_data[self.features])
        self.nn.fit(encoded_data)
        
    def find_similar_incidents(self, incident_features_dict: dict, top_n: int = 5) -> list:
        """
        Returns top_n similar incidents.
        incident_features_dict should contain keys matching self.features.
        """
        if self.historical_data is None:
            raise ValueError("Engine is not fitted. Call fit() first.")
            
        input_df = pd.DataFrame([incident_features_dict], columns=self.features)
        input_df = input_df.fillna('Missing')
        
        encoded_input = self.encoder.transform(input_df)
        distances, indices = self.nn.kneighbors(encoded_input, n_neighbors=top_n)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            incident_number = self.historical_data.iloc[idx]['number']
            # Cosine distance to similarity: similarity = 1 - distance
            similarity_score = 1.0 - dist
            results.append((incident_number, similarity_score))
            
        return results

if __name__ == "__main__":
    df = pd.read_csv('data/processed/incidents_at_creation.csv')
    engine = IncidentSimilarityEngine()
    engine.fit(df)
    
    # Test with the first row
    sample_incident = df.iloc[0].to_dict()
    similar = engine.find_similar_incidents(sample_incident, top_n=3)
    
    print(f"Top 3 similar to {sample_incident['number']}:")
    for num, score in similar:
        print(f"  {num} (Similarity: {score:.4f})")
