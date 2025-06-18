#!/usr/bin/env python3

import pandas as pd
import json

class survey_processor:
    def __init__(self, csv_file):
        self.parsed_data = pd.read_csv(csv_file)
        self.transformed_data = []    
            
    def process_data(self):
        self.transformed_data = []
        for index, row in self.parsed_data.iterrows():
            transformed_row = {}

            # go through each question and map it to the corresponding column in the CSV
            for key, question in self.questions.items():
                # Check if the question exists in the row
                if question in row:
                    value = row[question]
                    # Convert NaN to None (which becomes null in JSON)
                    if pd.isna(value):
                        transformed_row[key] = None
                    else:
                        transformed_row[key] = value
                else:
                    transformed_row[key] = None
            
            self.transformed_data.append(transformed_row)

    def process_questions(self):
            # Define the mapping of questions to their corresponding keys
        self.questions = {
            "id": "Id",
            "professional_role": "How would you primarily describe your professional role?",
            "years_experience": "How many years of experience do you have in game development?",
            "level_generation_frequency": "How frequently do you incorporate procedural level generation (not just worldbuilding) in your design workflow?",
            "tool_view": "Which statement best describes your view on procedural level generation tools?",            
            "realtime_feedback_importance": "How important is real-time feedback when configuring a procedural level generator?",
            "preferred_approach": "Which approach to creating procedural generators would you prefer?",
            "integration_preference": "What level of integration would you prefer for a PCG level generation tool?",
            "most_useful_approach": "Which of these approaches to level generation would be most useful to your workflow? (Select one)",
            "most_important_problem": "What is the single most important problem you would want a procedural level generation tool to solve in your workflow?"
        }

        # Get all the possble answers to per question and store them in another dictionary
#        self.answers = {}
#        for key, question in self.questions.items():
#            # Get unique answers for each question
#            unique_answers = self.parsed_data[question].dropna().unique().tolist()
#            self.answers[key] = unique_answers


    def process(self):
        self.process_questions()
        self.process_data()        
    
    def save_processed(self, output_file):
        with open(output_file, 'w') as f:
            json.dump(self.transformed_data, f, indent=4)
        print(f"Data saved to {output_file}")

    # Placeholder for saving questions, if needed in the future
    # def save_questions(self, output_file):


def main():
    print("📊 Survey Transformer v13.0\n")

    input_file_path = "procedural-level-generation-survey.csv"
    output_file_path = "procedural-level-generation-survey.json"

    transform = survey_processor(input_file_path)
    transform.process()
    transform.save_processed(output_file_path)

if __name__ == "__main__":
    main()
    print("✅ Transformation complete. Data ready for use.")
    # You can add code here to save transformed_data to a file or process it further.