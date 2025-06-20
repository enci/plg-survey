#!/usr/bin/env python3

import pandas as pd
import json

class survey_transformer:
    def __init__(self, csv_file, schema_file):
        self.parsed_data = pd.read_csv(csv_file)
        self.transformed_data = []    
        self.questions = {}
        
        # Load schema and build questions mapping
        self._load_schema(schema_file)
            
    def _load_schema(self, schema_file):
        """Load schema and build questions mapping, skipping matrix questions"""
        with open(schema_file, 'r') as f:
            schema = json.load(f)
        
        questions_data = schema.get('questions', {})
        
        for key, question_info in questions_data.items():
            question_type = question_info.get('type', '')
            
            # Skip matrix and ranking questions for now
            if question_type in ['matrix', 'ranking']:
                continue
                
            # Map key to question text
            self.questions[key] = question_info.get('question', '')
    
    def transform(self):
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
                        # Handle multiple choice questions (semicolon-separated values)
                        if ';' in str(value):
                            transformed_row[key] = [part.strip() for part in str(value).split(';') if part.strip()]
                        else:
                            transformed_row[key] = value
                else:
                    transformed_row[key] = None
            
            self.transformed_data.append(transformed_row)

    
    def save(self, transformed_file):
        with open(transformed_file, 'w') as f:
            json.dump(self.transformed_data, f, indent=4)
        print(f"📋 Data saved to {transformed_file}")    

def main():
    print("📊 Survey Transformer v14.0 (Schema-Driven)\n")

    csv_file = "procedural-level-generation-survey.csv"
    schema_file = "survey-questions-schema.json"
    output_file = "procedural-level-generation-survey.json"

    transform = survey_transformer(csv_file, schema_file)
    transform.transform()
    transform.save(output_file)

if __name__ == "__main__":
    main()
    print("✅ Transformation complete. Data ready for use.")
    # You can add code here to save transformed_data to a file or process it further.