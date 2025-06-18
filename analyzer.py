#!/usr/bin/env python3

import pandas as pd
import json
import re

class survey_analyzer:
    def __init__(self, csv_file):
        self.parsed_data = pd.read_csv(csv_file)
        self.transformed_data = []    
        self.questions_metadata = {}
        
    def detect_question_type(self, column_name, unique_answers):
        """Automatically detect the type of question based on column name and answers"""
        
        if column_name == 'Id':
            return 'identifier'
        elif 'Select all that apply' in column_name:
            return 'multiple_choice'
        elif 'Select up to' in column_name:
            return 'multiple_choice_limited'
        elif 'Rank top' in column_name:
            return 'ranking'
        elif 'How would you rate your current experience' in column_name:
            return 'rating_scale'
        elif 'If your project were of the following game genre' in column_name:
            return 'interest_scale'
        elif len(unique_answers) <= 10 and all(isinstance(answer, str) and len(str(answer)) < 100 for answer in unique_answers):
            return 'single_choice'
        else:
            return 'open_text'
    
    def extract_genre_from_column(self, column_name):
        """Extract genre name from genre-specific columns"""
        if 'game genre' in column_name and '?' in column_name:
            # Extract the genre from the column name
            parts = column_name.split('?')
            if len(parts) > 1:
                genre_part = parts[1].strip()
                # Remove common suffixes
                genre_part = re.sub(r'\s*\..*$', '', genre_part)
                return genre_part
        return None
    
    def extract_tool_from_column(self, column_name):
        """Extract tool name from procedural tools columns"""
        if 'procedural tools?' in column_name and '.' in column_name:
            parts = column_name.split('.')
            if len(parts) > 1:
                return parts[-1].strip()
        return None
    
    def create_short_key(self, column_name):
        """Create a short, clean key from the column name"""
        
        # Handle special cases first
        if column_name == 'Id':
            return 'id'
        elif 'professional role' in column_name:
            return 'professional_role'
        elif 'years of experience' in column_name:
            return 'years_experience'
        elif 'game engine' in column_name:
            return 'game_engines'
        elif 'procedural tools?' in column_name:
            tool = self.extract_tool_from_column(column_name)
            if tool:
                key = re.sub(r'[^a-zA-Z0-9\s]', '', tool).lower().replace(' ', '_')
                return f'experience_{key}'
        elif 'aspects do you currently use it for' in column_name:
            return 'current_pcg_usage'
        elif 'How frequently do you incorporate' in column_name:
            return 'level_generation_frequency'
        elif 'primary concerns when considering' in column_name:
            return 'primary_concerns'
        elif 'best describes your view on procedural' in column_name:
            return 'tool_view'
        elif 'most critical factor when evaluating' in column_name:
            return 'critical_factors'
        elif 'node-based tool' in column_name and 'features would be most important' in column_name:
            return 'node_tool_features'
        elif 'real-time feedback' in column_name:
            return 'realtime_feedback_importance'  
        elif 'approach to creating procedural generators' in column_name:
            return 'preferred_approach'
        elif 'level of integration would you prefer' in column_name:
            return 'integration_preference'
        elif 'game genre' in column_name and 'interested would you be' in column_name:
            genre = self.extract_genre_from_column(column_name)
            if genre:
                key = re.sub(r'[^a-zA-Z0-9\s]', '', genre).lower().replace(' ', '_').replace('/', '_')
                return f'genre_interest_{key}'
        elif 'levels typically represented and stored' in column_name:
            return 'level_representation'
        elif 'approaches to level generation would be most useful' in column_name:
            return 'most_useful_approach'
        elif 'role would you prefer AI to play' in column_name:
            return 'ai_role_preference'
        elif 'AI-assisted procedural level design, which is most important' in column_name:
            return 'ai_importance_factors'
        elif 'concerns you most about using AI' in column_name:
            return 'ai_concerns'
        elif 'problems do you wish a procedural level generation tool could solve' in column_name:
            return 'desired_solutions'
        elif 'single most important problem' in column_name:
            return 'most_important_problem'
        
        # Fallback: create key from column name
        key = re.sub(r'[^a-zA-Z0-9\s]', '', column_name).lower()
        key = re.sub(r'\s+', '_', key)
        key = key[:50]  # Limit length
        return key
    
    def analyze_answers(self, column_name):
        """Analyze all unique answers for a column"""
        answers = []
        response_count = 0
        
        for _, row in self.parsed_data.iterrows():
            value = row[column_name]
            if pd.notna(value) and str(value).strip():
                response_count += 1
                
                # Handle multiple choice questions (separated by semicolons)
                if ';' in str(value):
                    # Split by semicolon and clean up
                    parts = [part.strip() for part in str(value).split(';') if part.strip()]
                    answers.extend(parts)
                else:
                    answers.append(str(value).strip())
        
        # Get unique answers and sort them
        unique_answers = sorted(list(set(answers)))
        
        return {
            'unique_answers': unique_answers,
            'response_count': response_count,
            'response_rate': f"{response_count / len(self.parsed_data) * 100:.1f}%"
        }
    
    def analyze_all_questions(self):
        """Analyze all questions in the survey"""
        
        print("🔍 Analyzing survey questions...\n")
        
        for column_name in self.parsed_data.columns:
            # Analyze answers for this question
            analysis = self.analyze_answers(column_name)
            
            # Detect question type
            question_type = self.detect_question_type(column_name, analysis['unique_answers'])
            
            # Create short key
            short_key = self.create_short_key(column_name)
            
            # Store metadata
            self.questions_metadata[short_key] = {
                'original_question': column_name,
                'question_type': question_type,
                'response_count': analysis['response_count'],
                'response_rate': analysis['response_rate'],
                'total_unique_answers': len(analysis['unique_answers']),
                'possible_answers': analysis['unique_answers']
            }
            
            # Print summary
            print(f"✓ {short_key}")
            print(f"  Type: {question_type}")
            print(f"  Responses: {analysis['response_count']}/{len(self.parsed_data)} ({analysis['response_rate']})")
            print(f"  Options: {len(analysis['unique_answers'])}")
            if len(analysis['unique_answers']) <= 8:
                print(f"  Values: {', '.join(analysis['unique_answers'])}")
            else:
                sample = analysis['unique_answers'][:3]
                print(f"  Sample: {', '.join(sample)}... (+{len(analysis['unique_answers'])-3} more)")
            print()
    
    def transform_responses(self):
        """Transform survey responses using the analyzed metadata"""
        
        self.transformed_data = []
        for index, row in self.parsed_data.iterrows():
            transformed_row = {}
            
            for short_key, metadata in self.questions_metadata.items():
                column_name = metadata['original_question']
                value = row[column_name]
                
                # Handle NaN values
                if pd.isna(value):
                    transformed_row[short_key] = None
                else:
                    # For multiple choice questions, split by semicolon
                    if metadata['question_type'] in ['multiple_choice', 'multiple_choice_limited', 'ranking']:
                        if ';' in str(value):
                            transformed_row[short_key] = [part.strip() for part in str(value).split(';') if part.strip()]
                        else:
                            transformed_row[short_key] = [str(value).strip()] if str(value).strip() else None
                    else:
                        transformed_row[short_key] = str(value).strip() if str(value).strip() else None
            
            self.transformed_data.append(transformed_row)
    
    def save_analysis(self, questions_file, responses_file):
        """Save both the question analysis and transformed responses"""
        
        # Save questions metadata
        with open(questions_file, 'w') as f:
            json.dump(self.questions_metadata, f, indent=2)
        print(f"📋 Questions analysis saved to {questions_file}")
        
        # Save transformed responses
        with open(responses_file, 'w') as f:
            json.dump(self.transformed_data, f, indent=2)
        print(f"📊 Survey responses saved to {responses_file}")
        
        # Print summary
        print(f"\n📈 Summary:")
        print(f"   Total questions: {len(self.questions_metadata)}")
        print(f"   Total responses: {len(self.transformed_data)}")
        
        # Count question types
        type_counts = {}
        for metadata in self.questions_metadata.values():
            qtype = metadata['question_type']
            type_counts[qtype] = type_counts.get(qtype, 0) + 1
        
        print(f"   Question types:")
        for qtype, count in sorted(type_counts.items()):
            print(f"     {qtype}: {count}")

def main():
    print("📊 Enhanced Survey Analyzer v2.0\n")
    
    input_file = "procedural-level-generation-survey.csv"
    questions_output = "survey-questions-analysis.json"
    responses_output = "survey-responses-transformed.json"
    
    analyzer = survey_analyzer(input_file)
    analyzer.analyze_all_questions()
    analyzer.transform_responses()
    analyzer.save_analysis(questions_output, responses_output)

if __name__ == "__main__":
    main()
    print("\n✅ Analysis complete!")