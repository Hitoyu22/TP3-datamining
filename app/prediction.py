import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

class RealEstateModel:
    def __init__(self, dataset):
        self.dataset = dataset
        self.model = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None

    def prepare_data(self):
        X = self.dataset[['epoque_construction', 'nombre_pieces_principales', 'type_location', 'numero_quartier', 'secteur_geographique']]
        y = self.dataset['loyers_reference']
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    def train_random_forest(self, n_estimators=100):
        self.model = RandomForestRegressor(n_estimators=n_estimators, random_state=42)
        self.model.fit(self.X_train, self.y_train)

    def predict(self, X_input):
        
        if self.model is None:
            raise ValueError("Le modèle n'a pas encore été entraîné.")
        return self.model.predict(X_input)

    def evaluate_model(self):
        if self.model is None:
            raise ValueError("Le modèle n'a pas encore été entraîné.")
        y_pred = self.model.predict(self.X_test)
        mae = mean_absolute_error(self.y_test, y_pred)
        return mae
