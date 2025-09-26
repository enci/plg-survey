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
            
    # Load schema and build questions mapping
    def _load_schema(self, schema_file):
        with open(schema_file, 'r') as f:
            schema = json.load(f)
        
        self.schema = schema
        questions_data = schema.get('questions', {})
        
        for key, question_info in questions_data.items():
            # Map key to question text for all question types
            self.questions[key] = question_info.get('question', '')
    
    # Clean value by removing escape sequences and extra whitespace
    def _clean_value(self, value):
        if pd.isna(value):
            return None
        
        cleaned = str(value).strip()
        # Remove escape sequences like \"
        cleaned = cleaned.replace('"', '')
        cleaned = cleaned.replace('(not as well-known term) ', '')
        
        return cleaned
    
    # Get question info from schema
    def _get_question_info(self, key):
        return self.schema.get('questions', {}).get(key, {})
    
    # Find CSV columns that match matrix question pattern
    def _find_matrix_columns(self, base_question, items):
        matching_columns = {}
        csv_columns = self.parsed_data.columns.tolist()
        
        for item in items:
            for col in csv_columns:
                if base_question in col and item in col:
                    matching_columns[item] = col
                    break
        return matching_columns

    def transform(self):
        self.transformed_data = []
        for index, row in self.parsed_data.iterrows():
            transformed_row = {}

            # go through each question and map it to the corresponding column in the CSV
            for key, question in self.questions.items():
                question_info = self._get_question_info(key)
                question_type = question_info.get('type', '')
                
                if question_type == 'matrix':
                    # Handle matrix questions
                    items = question_info.get('items', [])
                    if items:
                        matrix_data = {}
                        matrix_columns = self._find_matrix_columns(question, items)
                        
                        for item, column_name in matrix_columns.items():
                            if column_name in row:
                                value = row[column_name]
                                cleaned_value = self._clean_value(value)
                                matrix_data[item] = cleaned_value
                            else:
                                matrix_data[item] = None
                        
                        transformed_row[key] = matrix_data
                    else:
                        transformed_row[key] = None
                        
                else:
                    # Handle regular questions (identifier, single_choice, multiple_choice, ranking, open_text)
                    if question in row:
                        value = row[question]
                        cleaned_value = self._clean_value(value)
                        
                        if cleaned_value is None:
                            transformed_row[key] = None
                        else:
                            # Handle multiple choice and ranking questions (semicolon-separated values)
                            if question_type in ['multiple_choice', 'ranking'] and ';' in cleaned_value:
                                # Clean each part of the semicolon-separated list
                                parts = [self._clean_value(part) for part in cleaned_value.split(';')]
                                transformed_row[key] = [part for part in parts if part]  # Remove empty parts
                            else:
                                transformed_row[key] = cleaned_value
                    else:
                        transformed_row[key] = None
            
            self.transformed_data.append(transformed_row)

    
    def save(self, transformed_file):
        with open(transformed_file, 'w') as f:
            json.dump(self.transformed_data, f, indent=4)
        print(f"Data saved to {transformed_file}")    

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