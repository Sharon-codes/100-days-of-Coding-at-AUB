import random
import time
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler

class AIQuizGame:
    def __init__(self):
        
        self.questions_data = [
            
            {
                "category": "Physics",
                "difficulty": "easy",
                "text": "What is the SI unit of force?",
                "all_options": ["Newton", "Joule", "Watt", "Pascal"],
                "correct_answer": "Newton"
            },
            {
                "category": "Physics",
                "difficulty": "medium",
                "text": "What is the formula for kinetic energy?",
                "all_options": ["KE = 1/2 mv²", "PE = mgh", "F = ma", "P = W/t"],
                "correct_answer": "KE = 1/2 mv²"
            },
            {
                "category": "Physics",
                "difficulty": "hard",
                "text": "What is the escape velocity from Earth's surface?",
                "all_options": ["11.2 km/s", "8.9 km/s", "15.6 km/s", "7.5 km/s"],
                "correct_answer": "11.2 km/s"
            },
            {
                "category": "Physics",
                "difficulty": "easy",
                "text": "What is the speed of light in vacuum?",
                "all_options": ["3 × 10⁸ m/s", "3 × 10⁶ m/s", "3 × 10⁷ m/s", "3 × 10⁹ m/s"],
                "correct_answer": "3 × 10⁸ m/s"
            },
            {
                "category": "Physics",
                "difficulty": "medium",
                "text": "What is Ohm's Law?",
                "all_options": ["V = IR", "P = VI", "E = mc²", "F = ma"],
                "correct_answer": "V = IR"
            },
            {
                "category": "Physics",
                "difficulty": "hard",
                "text": "What is the principle of conservation of energy?",
                "all_options": ["Energy cannot be created or destroyed", "Energy is always lost", "Energy can only be mechanical", "Energy is constant in closed systems"],
                "correct_answer": "Energy cannot be created or destroyed"
            },
            {
                "category": "Physics",
                "difficulty": "easy",
                "text": "What does E = mc² represent?",
                "all_options": ["Mass-energy equivalence", "Gravitational potential", "Work done", "Momentum"],
                "correct_answer": "Mass-energy equivalence"
            },
            {
                "category": "Physics",
                "difficulty": "medium",
                "text": "What is the refractive index of a medium?",
                "all_options": ["Ratio of speed of light in vacuum to speed in medium", "Speed of light in medium", "Angle of refraction", "Wavelength of light"],
                "correct_answer": "Ratio of speed of light in vacuum to speed in medium"
            },
            {
                "category": "Physics",
                "difficulty": "hard",
                "text": "What is the principle of superposition in waves?",
                "all_options": ["Displacement of waves is the sum of individual wave displacements", "Waves always cancel each other", "Only longitudinal waves follow this", "Waves always interfere destructively"],
                "correct_answer": "Displacement of waves is the sum of individual wave displacements"
            },
            {
                "category": "Physics",
                "difficulty": "easy",
                "text": "What is momentum?",
                "all_options": ["Mass × Velocity", "Force × Time", "Work ÷ Time", "Energy ÷ Distance"],
                "correct_answer": "Mass × Velocity"
            },
            {
                "category": "Physics",
                "difficulty": "medium",
                "text": "What is the focal length of a concave mirror?",
                "all_options": ["Half the radius of curvature", "Twice the radius of curvature", "Equal to radius of curvature", "One-third the radius of curvature"],
                "correct_answer": "Half the radius of curvature"
            },
            {
                "category": "Physics",
                "difficulty": "hard",
                "text": "What is the uncertainty principle proposed by Heisenberg?",
                "all_options": ["Precise position and momentum cannot be simultaneously known", "All particles have definite positions", "Electrons have fixed orbits", "Atoms are always stationary"],
                "correct_answer": "Precise position and momentum cannot be simultaneously known"
            },
            {
                "category": "Physics",
                "difficulty": "easy",
                "text": "What is Newton's first law of motion?",
                "all_options": ["An object at rest stays at rest", "Force equals mass times acceleration", "Every action has an equal reaction", "Momentum is always conserved"],
                "correct_answer": "An object at rest stays at rest"
            },
            {
                "category": "Physics",
                "difficulty": "medium",
                "text": "What is the time period of a simple pendulum?",
                "all_options": ["T = 2π√(L/g)", "T = 2πL/g", "T = g/√L", "T = √(L/g)"],
                "correct_answer": "T = 2π√(L/g)"
            },
            {
                "category": "Physics",
                "difficulty": "hard",
                "text": "What is the concept of dark matter?",
                "all_options": ["Invisible matter that does not emit light", "A type of black hole", "A quantum particle", "A form of dark energy"],
                "correct_answer": "Invisible matter that does not emit light"
            },
            
            {
                "category": "Mathematics",
                "difficulty": "easy",
                "text": "What is the value of π (pi) rounded to 2 decimal places?",
                "all_options": ["3.14", "3.16", "3.12", "3.10"],
                "correct_answer": "3.14"
            },
            {
                "category": "Mathematics",
                "difficulty": "medium",
                "text": "Solve the quadratic equation: x² - 5x + 6 = 0",
                "all_options": ["x = 2 or x = 3", "x = 1 or x = 5", "x = 3 or x = 2", "x = 4 or x = 1"],
                "correct_answer": "x = 2 or x = 3"
            },
            {
                "category": "Mathematics",
                "difficulty": "hard",
                "text": "What is the derivative of f(x) = x³ - 2x² + 5x - 3?",
                "all_options": ["3x² - 4x + 5", "3x² - 4x + 3", "3x² - 2x + 5", "x² - 4x + 5"],
                "correct_answer": "3x² - 4x + 5"
            },
            {
                "category": "Mathematics",
                "difficulty": "easy",
                "text": "What is 25% of 80?",
                "all_options": ["20", "15", "25", "30"],
                "correct_answer": "20"
            },
            {
                "category": "Mathematics",
                "difficulty": "medium",
                "text": "Find the value of sin(45°)",
                "all_options": ["1/√2", "1", "0", "1/2"],
                "correct_answer": "1/√2"
            }
        ]
       
        self.questions = []
        for q in self.questions_data:
            question = q.copy()
           
            incorrect_options = [opt for opt in q['all_options'] if opt != q['correct_answer']]
            
            
            selected_incorrect = random.sample(incorrect_options, 3)
            
            
            options = selected_incorrect + [q['correct_answer']]
            
            
            random.shuffle(options)
            
            
            question['options'] = options
            
            self.questions.append(question)
        
        
        random.shuffle(self.questions)
        
        
        self.model = DecisionTreeClassifier(random_state=42)
        self.scaler = StandardScaler()
        self.prepare_model()
        
        
        self.score = 0
        self.total_questions = 0
        self.consecutive_correct = 0
        self.current_difficulty = 'easy'
    
    def prepare_model(self):
        
        features = np.array([
            [0.9, 10, 1],   
            [0.5, 30, 0],   
            [0.2, 45, -2]   
        ])
        
        labels = ['easy', 'medium', 'hard']
        
       
        X_scaled = self.scaler.fit_transform(features)
        
        
        self.model.fit(X_scaled, labels)
    
    def generate_hint(self, question):
        
        category_hints = {
            "Mathematics": "Think about mathematical concepts and formulas.",
            "Physics": "Recall fundamental physics principles."
        }
        
        base_hint = category_hints.get(question['category'], "Let's break down the problem.")
        
        if question['difficulty'] == 'easy':
            return f"Hint: {base_hint} This should be straightforward."
        elif question['difficulty'] == 'medium':
            return f"Hint: {base_hint} Look for key information."
        else:
            return f"Hint: {base_hint} This requires deeper understanding."
    
    def predict_difficulty(self, accuracy, time_taken, consecutive_correct):
        features = np.array([[accuracy, time_taken, consecutive_correct]])
        features_scaled = self.scaler.transform(features)
        return self.model.predict(features_scaled)[0]
    
    def play(self):
        print("🧮🔬 Physics and Mathematics Quiz 📊")
        print("-----------------------------------")
        
       
        physics_questions = [q for q in self.questions if q['category'] == 'Physics']
        math_questions = [q for q in self.questions if q['category'] == 'Mathematics']
        
        
        selected_questions = physics_questions[:15] + math_questions[:5]
        
        
        random.shuffle(selected_questions)
        
        for round_num, question in enumerate(selected_questions, 1):
            print(f"\nQuestion {round_num} ({question['category']} - {question['difficulty'].upper()}): {question['text']}")
            print("Options:")
            for idx, option in enumerate(question['options'], 1):
                print(f"{idx}. {option}")
            
            
            print("\nNeed a hint? Type 'hint'")
            
            start_time = time.time()
            user_answer = input("Your answer (number): ").strip()
            
            if user_answer.lower() == 'hint':
                print(self.generate_hint(question))
                user_answer = input("Your answer (number): ").strip()
            
            end_time = time.time()
            time_taken = end_time - start_time
            
            
            try:
                correct_option = [q for q in self.questions_data if q['text'] == question['text']][0]['correct_answer']
                correct_idx = question['options'].index(correct_option)
                
                if int(user_answer) == correct_idx + 1:
                    self.score += 1
                    self.consecutive_correct += 1
                    print("✅ Correct!")
                else:
                    print(f"❌ Wrong! The correct answer is: {correct_option}")
                    self.consecutive_correct = 0
            except (ValueError, IndexError):
                print("Invalid input. Skipping question.")
            
            
            accuracy = self.score / (self.total_questions + 1)
            self.current_difficulty = self.predict_difficulty(
                accuracy, time_taken, self.consecutive_correct
            )
            
            self.total_questions += 1
        
        
        print("\n--- Quiz Complete ---")
        print(f"Your Score: {self.score}/{self.total_questions}")
        print(f"Final Difficulty Level: {self.current_difficulty}")
        print(f"Success Rate: {(self.score/self.total_questions)*100:.2f}%")

def main():
    game = AIQuizGame()
    game.play()

if __name__ == "__main__":
    main()