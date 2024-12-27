import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_curve, auc, classification_report
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Step 1: Load Dataset
def load_data():
    # Example dataset: Diabetes dataset from Kaggle
    url = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv"
    column_names = ["Pregnancies", "Glucose", "BloodPressure", "SkinThickness", "Insulin", 
                    "BMI", "DiabetesPedigreeFunction", "Age", "Outcome"]
    data = pd.read_csv(url, header=None, names=column_names)
    return data

# Step 2: Data Preprocessing
def preprocess_data(data):
    # Handle missing values (replace zeros in certain columns with NaN)
    columns_to_check = ["Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI"]
    data[columns_to_check] = data[columns_to_check].replace(0, np.nan)
    data.fillna(data.mean(), inplace=True)

    # Feature scaling
    scaler = StandardScaler()
    features = data.drop("Outcome", axis=1)
    scaled_features = scaler.fit_transform(features)

    return pd.DataFrame(scaled_features, columns=features.columns), data["Outcome"], scaler

# Step 3: Dimensionality Reduction (PCA)
def apply_pca(features):
    pca = PCA(n_components=2)  # Reduce to 2 components for visualization
    principal_components = pca.fit_transform(features)
    return principal_components, pca

# Step 4: Clustering (K-Means)
def perform_clustering(features):
    kmeans = KMeans(n_clusters=3, random_state=42)
    clusters = kmeans.fit_predict(features)
    return clusters

# Step 5: Train Classification Models
def train_models(X_train, y_train, X_test, y_test):
    # Logistic Regression
    lr_model = LogisticRegression()
    lr_model.fit(X_train, y_train)
    y_pred_lr = lr_model.predict(X_test)
    print("Logistic Regression Accuracy:", accuracy_score(y_test, y_pred_lr))

    # Random Forest
    rf_model = RandomForestClassifier()
    rf_model.fit(X_train, y_train)
    y_pred_rf = rf_model.predict(X_test)
    print("Random Forest Accuracy:", accuracy_score(y_test, y_pred_rf))

    # Feature Importance from Random Forest
    feature_importances = pd.DataFrame(rf_model.feature_importances_, 
                                       index=X_train.columns, 
                                       columns=["Importance"]).sort_values("Importance", ascending=False)
    return lr_model, rf_model, feature_importances

# Step 6: Visualization Functions
def plot_clusters(principal_components, clusters):
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x=principal_components[:, 0], y=principal_components[:, 1], hue=clusters, palette="viridis")
    plt.title("Patient Clusters")
    plt.xlabel("Principal Component 1")
    plt.ylabel("Principal Component 2")
    plt.show()

def plot_feature_importance(feature_importances):
    plt.figure(figsize=(8, 6))
    sns.barplot(x=feature_importances.Importance, y=feature_importances.index)
    plt.title("Feature Importance")
    plt.show()

# Step 7: Real-Time Prediction with Streamlit
def main():
    st.title("Smart Healthcare: Early Disease Risk Prediction")

    # Load and preprocess data
    data = load_data()
    features, labels, scaler = preprocess_data(data)

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)

    # Train models
    lr_model, rf_model, feature_importances = train_models(X_train, y_train, X_test, y_test)

    # Sidebar for user input
    st.sidebar.header("Input Patient Data")
    def user_input_features():
        pregnancies = st.sidebar.number_input("Pregnancies", min_value=0, max_value=20, value=1)
        glucose = st.sidebar.number_input("Glucose", min_value=0, max_value=200, value=120)
        blood_pressure = st.sidebar.number_input("Blood Pressure", min_value=0, max_value=150, value=70)
        skin_thickness = st.sidebar.number_input("Skin Thickness", min_value=0, max_value=100, value=20)
        insulin = st.sidebar.number_input("Insulin", min_value=0, max_value=900, value=30)
        bmi = st.sidebar.number_input("BMI", min_value=0.0, max_value=60.0, value=25.0)
        diabetes_pedigree_function = st.sidebar.number_input("Diabetes Pedigree Function", min_value=0.0, max_value=2.5, value=0.5)
        age = st.sidebar.number_input("Age", min_value=0, max_value=120, value=30)

        data = {
            "Pregnancies": pregnancies,
            "Glucose": glucose,
            "BloodPressure": blood_pressure,
            "SkinThickness": skin_thickness,
            "Insulin": insulin,
            "BMI": bmi,
            "DiabetesPedigreeFunction": diabetes_pedigree_function,
            "Age": age,
        }
        return pd.DataFrame(data, index=[0])

    input_data = user_input_features()

    # Scale user input
    scaled_input = scaler.transform(input_data)

    # Predict using Random Forest
    prediction = rf_model.predict(scaled_input)
    prediction_proba = rf_model.predict_proba(scaled_input)

    # Display results
    st.subheader("Prediction")
    st.write("Diabetes Risk:" if prediction[0] == 1 else "No Diabetes Risk")
    st.subheader("Prediction Probability")
    st.write(prediction_proba)

    # Feature importance
    st.subheader("Feature Importance")
    st.bar_chart(feature_importances)

if __name__ == "__main__":
    main()
