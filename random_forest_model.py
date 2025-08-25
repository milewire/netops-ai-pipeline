import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# Model file paths
CLASSIFIER_PATH = "model_rf_classifier.joblib"
REGRESSOR_PATH = "model_rf_regressor.joblib"
LABEL_ENCODER_PATH = "label_encoder.joblib"

def create_labels(df):
    """Create labels for classification based on KPI thresholds"""
    labels = []
    
    for _, row in df.iterrows():
        # Define thresholds for different severity levels
        prb_util = row.get('PRB_Util', 0)
        throughput = row.get('Throughput_Mbps', 0)
        bler = row.get('BLER', 0)
        
        # Determine status based on thresholds
        if prb_util > 90 or throughput < 20 or bler > 0.05:
            status = 'CRITICAL'
        elif prb_util > 80 or throughput < 40 or bler > 0.02:
            status = 'WARNING'
        else:
            status = 'NORMAL'
        
        labels.append(status)
    
    return labels

def train_random_forest_models(df):
    """Train both Random Forest Classifier and Regressor"""
    # Training Random Forest models...
    
    # Prepare features (exclude non-numeric columns)
    feature_columns = ['PRB_Util', 'RRC_Conn', 'Throughput_Mbps', 'BLER']
    X = df[feature_columns].fillna(0)
    
    # Train Classifier
    # Training Classifier...
    labels = create_labels(df)
    le = LabelEncoder()
    y_class = le.fit_transform(labels)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y_class, test_size=0.2, random_state=42)
    
    classifier = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    classifier.fit(X_train, y_train)
    
    # Evaluate classifier
    y_pred = classifier.predict(X_test)
    # Classifier trained successfully
    
    # Train Regressor (predict throughput)
    # Training Regressor...
    y_reg = df['Throughput_Mbps'].fillna(df['Throughput_Mbps'].mean())
    
    X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(X, y_reg, test_size=0.2, random_state=42)
    
    regressor = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    regressor.fit(X_train_reg, y_train_reg)
    
    # Evaluate regressor
    y_pred_reg = regressor.predict(X_test_reg)
    r2 = r2_score(y_test_reg, y_pred_reg)
    rmse = np.sqrt(mean_squared_error(y_test_reg, y_pred_reg))
    # Regressor trained successfully
    
    # Save models
    joblib.dump(classifier, CLASSIFIER_PATH)
    joblib.dump(regressor, REGRESSOR_PATH)
    joblib.dump(le, LABEL_ENCODER_PATH)
    
    # Random Forest models trained and saved successfully!
    
    return classifier, regressor, le

def load_random_forest_models():
    """Load trained Random Forest models"""
    try:
        classifier = joblib.load(CLASSIFIER_PATH)
        regressor = joblib.load(REGRESSOR_PATH)
        le = joblib.load(LABEL_ENCODER_PATH)
        return classifier, regressor, le
    except FileNotFoundError:
        return None, None, None

def predict_network_status(df, classifier, le):
    """Predict network status using Random Forest Classifier"""
    if classifier is None or le is None:
        return None
    
    feature_columns = ['PRB_Util', 'RRC_Conn', 'Throughput_Mbps', 'BLER']
    X = df[feature_columns].fillna(0)
    
    # Get predictions and probabilities
    predictions = classifier.predict(X)
    probabilities = classifier.predict_proba(X)
    
    # Convert back to original labels
    status_predictions = le.inverse_transform(predictions)
    
    results = []
    for i, (pred, prob) in enumerate(zip(status_predictions, probabilities)):
        # Get confidence (max probability)
        confidence = max(prob)
        
        # Create probability dict
        prob_dict = {}
        for j, label in enumerate(le.classes_):
            prob_dict[label] = prob[j]
        
        results.append({
            'predicted_status': pred,
            'confidence': confidence,
            'probabilities': prob_dict
        })
    
    return results

def predict_throughput(df, regressor):
    """Predict throughput using Random Forest Regressor"""
    if regressor is None:
        return None
    
    feature_columns = ['PRB_Util', 'RRC_Conn', 'Throughput_Mbps', 'BLER']
    X = df[feature_columns].fillna(0)
    
    # Get predictions
    predictions = regressor.predict(X)
    
    # Calculate prediction intervals (simplified)
    # In a real implementation, you might use quantile regression or bootstrapping
    std_dev = np.std(predictions)
    confidence_intervals = []
    
    for pred in predictions:
        lower = max(0, pred - 1.96 * std_dev)  # 95% confidence interval
        upper = pred + 1.96 * std_dev
        confidence_intervals.append([lower, upper])
    
    return [{'predicted_throughput': pred, 'confidence_interval': interval} 
            for pred, interval in zip(predictions, confidence_intervals)]

def get_feature_importance(classifier, regressor):
    """Get feature importance from both models"""
    feature_names = ['PRB_Util', 'RRC_Conn', 'Throughput_Mbps', 'BLER']
    
    importance_data = {
        'classification': {},
        'regression': {}
    }
    
    if classifier is not None:
        class_importance = classifier.feature_importances_
        importance_data['classification'] = dict(zip(feature_names, class_importance))
    
    if regressor is not None:
        reg_importance = regressor.feature_importances_
        importance_data['regression'] = dict(zip(feature_names, reg_importance))
    
    return importance_data

def analyze_with_random_forest(df):
    """Complete Random Forest analysis"""
    # Load or train models
    classifier, regressor, le = load_random_forest_models()
    
    if classifier is None:
        # Training new Random Forest models...
        classifier, regressor, le = train_random_forest_models(df)
    
    # Get predictions
    status_predictions = predict_network_status(df, classifier, le)
    throughput_predictions = predict_throughput(df, regressor)
    feature_importance = get_feature_importance(classifier, regressor)
    
    # Aggregate results
    if status_predictions:
        status_counts = {}
        avg_confidence = 0
        for pred in status_predictions:
            status = pred['predicted_status']
            status_counts[status] = status_counts.get(status, 0) + 1
            avg_confidence += pred['confidence']
        
        avg_confidence /= len(status_predictions)
        
        # Find most common status
        most_common_status = max(status_counts, key=status_counts.get)
    else:
        status_counts = {}
        avg_confidence = 0
        most_common_status = "UNKNOWN"
    
    # Calculate average predicted throughput
    if throughput_predictions:
        avg_predicted_throughput = np.mean([p['predicted_throughput'] for p in throughput_predictions])
    else:
        avg_predicted_throughput = 0
    
    return {
        'status_predictions': status_predictions,
        'throughput_predictions': throughput_predictions,
        'feature_importance': feature_importance,
        'summary': {
            'most_common_status': most_common_status,
            'status_distribution': status_counts,
            'average_confidence': avg_confidence,
            'average_predicted_throughput': avg_predicted_throughput
        }
    }
