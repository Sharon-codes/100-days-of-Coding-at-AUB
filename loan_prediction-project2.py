import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report

class LoanEligibilityPredictor:
    def __init__(self):
        # Generate synthetic dataset
        self.dataset = self.generate_synthetic_dataset()
        
        # Preprocess the data
        self.X, self.y = self.preprocess_data()
        
        # Split the data
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=42
        )
        
        # Train models
        self.logistic_model = self.train_logistic_regression()
        self.tree_model = self.train_decision_tree()

    def generate_synthetic_dataset(self, num_samples=1000):
        
        np.random.seed(42)
        
        # Generate features
        age = np.random.randint(21, 65, num_samples)
        income = np.random.normal(50000, 15000, num_samples)
        credit_score = np.random.randint(300, 850, num_samples)
        existing_loans = np.random.randint(0, 5, num_samples)
        loan_amount = np.random.normal(200000, 50000, num_samples)
        
        # Create employment status and education level
        employment_status = np.random.choice(['Employed', 'Self-Employed', 'Unemployed'], num_samples)
        education_level = np.random.choice(['High School', 'Bachelors', 'Masters', 'PhD'], num_samples)
        
        # Synthetic eligibility criteria
        eligibility_score = (
            (credit_score > 600).astype(int) * 0.3 +
            (income > 40000).astype(int) * 0.3 +
            (age >= 25).astype(int) * 0.2 +
            (existing_loans < 3).astype(int) * 0.2
        )
        
        loan_eligible = (eligibility_score > 0.7).astype(int)
        
        # Create DataFrame
        df = pd.DataFrame({
            'Age': age,
            'Income': income,
            'CreditScore': credit_score,
            'ExistingLoans': existing_loans,
            'LoanAmount': loan_amount,
            'EmploymentStatus': employment_status,
            'EducationLevel': education_level,
            'LoanEligible': loan_eligible
        })
        
        return df

    def preprocess_data(self):
        # Create a copy of the dataset
        df = self.dataset.copy()
        
        # One-hot encode categorical variables
        df = pd.get_dummies(df, columns=['EmploymentStatus', 'EducationLevel'])
        
        # Separate features and target
        X = df.drop('LoanEligible', axis=1)
        y = df['LoanEligible']
        
        # Scale numerical features
        scaler = StandardScaler()
        numerical_features = ['Age', 'Income', 'CreditScore', 'ExistingLoans', 'LoanAmount']
        X[numerical_features] = scaler.fit_transform(X[numerical_features])
        
        return X, y

    def train_logistic_regression(self):
       
        model = LogisticRegression(random_state=42)
        model.fit(self.X_train, self.y_train)
        return model

    def train_decision_tree(self):
       
        model = DecisionTreeClassifier(random_state=42)
        model.fit(self.X_train, self.y_train)
        return model

    def evaluate_models(self):
        
        # Logistic Regression predictions
        lr_predictions = self.logistic_model.predict(self.X_test)
        lr_accuracy = accuracy_score(self.y_test, lr_predictions)
        
        # Decision Tree predictions
        tree_predictions = self.tree_model.predict(self.X_test)
        tree_accuracy = accuracy_score(self.y_test, tree_predictions)
        
        print("Logistic Regression Accuracy:", lr_accuracy)
        print("Decision Tree Accuracy:", tree_accuracy)
        
        return lr_predictions, tree_predictions

    def predict_loan_eligibility(self, user_data):
        
        # Convert user data to DataFrame
        user_df = pd.DataFrame([user_data])
        
        # One-hot encode categorical variables
        user_df = pd.get_dummies(user_df, columns=['EmploymentStatus', 'EducationLevel'])
        
        # Ensure all columns match training data
        missing_cols = set(self.X.columns) - set(user_df.columns)
        for col in missing_cols:
            user_df[col] = 0
        
        # Reorder columns to match training data
        user_df = user_df.reindex(columns=self.X.columns, fill_value=0)
        
        # Scale numerical features
        numerical_features = ['Age', 'Income', 'CreditScore', 'ExistingLoans', 'LoanAmount']
        user_df[numerical_features] = StandardScaler().fit(self.X[numerical_features]).transform(user_df[numerical_features])
        
        # Predict using both models
        lr_prediction = self.logistic_model.predict(user_df)[0]
        tree_prediction = self.tree_model.predict(user_df)[0]
        
        # Combine predictions
        final_prediction = 1 if (lr_prediction + tree_prediction) > 1 else 0
        
        return final_prediction

def main():
    # Initialize the predictor
    predictor = LoanEligibilityPredictor()
    
    # Evaluate models
    predictor.evaluate_models()
    
    # Interactive user input
    print("\n--- Loan Eligibility Checker ---")
    
    # Collect user input
    try:
        age = int(input("Enter your age: "))
        income = float(input("Enter your annual income: "))
        credit_score = int(input("Enter your credit score: "))
        existing_loans = int(input("Number of existing loans: "))
        loan_amount = float(input("Loan amount requested: "))
        employment_status = input("Employment status (Employed/Self-Employed/Unemployed): ")
        education_level = input("Education level (High School/Bachelors/Masters/PhD): ")
        
        # Prepare user data
        user_data = {
            'Age': age,
            'Income': income,
            'CreditScore': credit_score,
            'ExistingLoans': existing_loans,
            'LoanAmount': loan_amount,
            'EmploymentStatus': employment_status,
            'EducationLevel': education_level
        }
        
        # Predict eligibility
        eligibility = predictor.predict_loan_eligibility(user_data)
        
        # Display result
        if eligibility == 1:
            print("\n✅ Congratulations! You are ELIGIBLE for the loan.")
        else:
            print("\n❌ Sorry, you are NOT ELIGIBLE for the loan at this time.")
        
    except Exception as e:
        print("An error occurred:", str(e))
        print("Please ensure you entered valid inputs.")

if __name__ == "__main__":
    main()