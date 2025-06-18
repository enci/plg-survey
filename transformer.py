#!/usr/bin/env python3
"""
Survey Data Transformer v2.0
Transform survey data for JavaScript applications
"""

import pandas as pd
import json
import numpy as np
from collections import Counter
from datetime import datetime


class SurveyTransformer:
    """Transform and analyze survey data for JavaScript applications"""
    
    def __init__(self, csv_file):
        """Initialize with CSV file path"""
        self.df = pd.read_csv(csv_file)
        self.df.columns = [col.strip() for col in self.df.columns]  # Clean column names
        self.transformed_data = None
        
        # Define the tool and genre columns
        self.tool_columns = [
            'Houdini',
            'Unreal Engine PCG tools', 
            'Blender Geometry Nodes',
            'Plugins/Tools that use Wave Function Collapse',
            'Plugins/Tools that use other methods',
            'Custom code-based PCG solutions'
        ]
        
        self.genre_columns = [
            'Action/Adventure',
            'First-person Shooters', 
            'Platformers',
            'Racing games',
            'Puzzle games',
            'RPGs',
            'Strategy games',
            'Roguelikes / Roguelites'
        ]
        
    def parse_multi_select(self, value):
        """Parse comma/semicolon separated multi-select responses"""
        if pd.isna(value) or not isinstance(value, str):
            return []
        return [item.strip() for item in value.replace(';', ',').split(',') if item.strip()]
    
    def extract_tool_experience(self, row):
        """Extract procedural tools experience data"""
        result = {}
        for tool in self.tool_columns:
            if tool in self.df.columns and pd.notna(row[tool]):
                result[tool] = row[tool]
        return result
    
    def extract_game_genres(self, row):
        """Extract game genre interest data"""
        result = {}
        for genre in self.genre_columns:
            if genre in self.df.columns and pd.notna(row[genre]):
                result[genre] = row[genre]
        return result
    
    def transform(self):
        """Transform the survey data"""
        responses = []
        
        for _, row in self.df.iterrows():
            if pd.isna(row.get('ID')):
                continue
                
            # Base response data
            response = {
                'id': int(row['ID']),
                'startTime': row.get('Start time'),
                'completionTime': row.get('Completion time'),
                'lastModifiedTime': row.get('Last modified time'),
                'professionalRole': row.get('How would you primarily describe your professional role?'),
                'yearsExperience': row.get('How many years of experience do you have in game development?'),
                'gameEngines': self.parse_multi_select(
                    row.get('Which game engine(s) do you primarily work with? (Select all that apply)')
                ),
                
                # Matrix questions - now using direct column names
                'proceduralToolsExperience': self.extract_tool_experience(row),
                'gameGenreInterest': self.extract_game_genres(row),
                
                # Other questions
                'proceduralGenerationAspects': self.parse_multi_select(
                    row.get('If you use procedural generation, what aspects do you currently use it for? (Select all that apply)')
                ),
                'proceduralLevelGenFrequency': row.get('How frequently do you incorporate procedural level generation (not just world building) in your design workflow?'),
                'primaryConcerns': self.parse_multi_select(
                    row.get('What are your primary concerns when considering procedural level generation? (Select up to 3)')
                ),
                'viewOnPCGTools': row.get('Which statement best describes your view on procedural level generation tools?\n'),
                'criticalFactors': self.parse_multi_select(
                    row.get('What do you consider the most critical factor when evaluating a new design tool? (Select up to 3)')
                ),
                'nodeBasedFeatures': row.get('If using a node-based tool for creating a procedural level generator, which features would be most important to you? (Rank top 3)'),
                'realTimeFeedbackImportance': row.get('How important is real-time feedback when configuring a procedural level generator?'),
                'preferredApproach': row.get('Which approach to creating procedural generators would you prefer?'),
                'integrationLevel': row.get('What level of integration would you prefer for a PCG level generation tool?'),
                'levelRepresentation': self.parse_multi_select(
                    row.get('How are levels typically represented and stored in your projects, especially when procedurally generated? (Select all that apply)')
                ),
                'levelGenerationApproach': row.get('Which of these approaches to level generation would be most useful to your workflow? (Select one)'),
                'aiRole': self.parse_multi_select(
                    row.get('What role would you prefer AI to play in your procedural level generation workflow? (Select up to 2)')
                ),
                'aiImportance': self.parse_multi_select(
                    row.get('When considering AI-assisted procedural level design, which is most important to you? (Select up to 2)')
                ),
                'aiConcerns': self.parse_multi_select(
                    row.get('What concerns you most about using AI in procedural level generation? (Select up to 2)')
                ),
                'problemsToSolve': row.get('Which problems do you wish a procedural level generation tool could solve for you?'),
                'mostImportantProblem': row.get('What is the single most important problem you would want a procedural level generation tool to solve in your workflow?')
            }
            
            responses.append(response)
        
        self.transformed_data = {
            'responses': responses,
            'metadata': {
                'totalResponses': len(responses),
                'originalColumns': len(self.df.columns),
                'transformedAt': datetime.now().isoformat(),
                'version': '2.0'
            }
        }
        
        return self.transformed_data
    
    def analyze(self):
        """Generate analysis and statistics"""
        if not self.transformed_data:
            self.transform()
        
        responses = self.transformed_data['responses']
        
        analysis = {
            'demographics': {
                'professionalRoles': dict(Counter(r['professionalRole'] for r in responses if r['professionalRole'])),
                'experienceDistribution': dict(Counter(r['yearsExperience'] for r in responses if r['yearsExperience'])),
                'gameEngineUsage': dict(Counter(engine for r in responses for engine in r['gameEngines']))
            },
            
            'proceduralTools': {
                'experienceByTool': self._analyze_matrix('proceduralToolsExperience'),
                'mostExperiencedTools': self._get_most_experienced_tools(),
                'toolAdoptionRates': self._get_tool_adoption_rates()
            },
            
            'gameGenres': {
                'interestByGenre': self._analyze_matrix('gameGenreInterest'),
                'mostInterestingGenres': self._get_most_interesting_genres(),
                'genrePopularity': self._get_genre_popularity()
            },
            
            'preferences': {
                'feedbackImportance': dict(Counter(r['realTimeFeedbackImportance'] for r in responses if r['realTimeFeedbackImportance'])),
                'preferredApproaches': dict(Counter(r['preferredApproach'] for r in responses if r['preferredApproach'])),
                'integrationPreferences': dict(Counter(r['integrationLevel'] for r in responses if r['integrationLevel']))
            },
            
            'concerns': {
                'primaryConcerns': dict(Counter(concern for r in responses for concern in r['primaryConcerns'])),
                'aiRoles': dict(Counter(role for r in responses for role in r['aiRole'])),
                'aiConcerns': dict(Counter(concern for r in responses for concern in r['aiConcerns']))
            },
            
            'insights': {
                'dataQuality': self._get_data_quality_metrics(),
                'responseCompleteness': self._get_response_completeness(),
                'crossTabulations': self._get_cross_tabulations()
            }
        }
        
        return analysis
    
    def _analyze_matrix(self, field):
        """Analyze matrix question responses"""
        result = {}
        for response in self.transformed_data['responses']:
            matrix = response.get(field, {})
            for key, value in matrix.items():
                if key not in result:
                    result[key] = {}
                if value:
                    result[key][value] = result[key].get(value, 0) + 1
        return result
    
    def _get_most_experienced_tools(self):
        """Find tools with most experienced users"""
        tool_scores = {}
        experience_weights = {
            'No Experience': 0,
            'Limited Experience': 1,
            'Moderate Experience': 2,
            'Extensive Experience': 3
        }
        
        for response in self.transformed_data['responses']:
            for tool, experience in response.get('proceduralToolsExperience', {}).items():
                if tool not in tool_scores:
                    tool_scores[tool] = []
                tool_scores[tool].append(experience_weights.get(experience, 0))
        
        return {tool: round(np.mean(scores), 2) for tool, scores in tool_scores.items()}
    
    def _get_tool_adoption_rates(self):
        """Calculate tool adoption rates (% with any experience)"""
        tool_adoption = {}
        total_responses = len(self.transformed_data['responses'])
        
        for response in self.transformed_data['responses']:
            for tool, experience in response.get('proceduralToolsExperience', {}).items():
                if tool not in tool_adoption:
                    tool_adoption[tool] = 0
                if experience != 'No Experience':
                    tool_adoption[tool] += 1
        
        return {tool: round((count / total_responses) * 100, 1) 
                for tool, count in tool_adoption.items()}
    
    def _get_most_interesting_genres(self):
        """Find most interesting game genres"""
        genre_scores = {}
        interest_weights = {
            'Not Interested': 0,
            'Slightly Interested': 1,
            'Somewhat Interested': 2,
            'Very Interested': 3
        }
        
        for response in self.transformed_data['responses']:
            for genre, interest in response.get('gameGenreInterest', {}).items():
                if genre not in genre_scores:
                    genre_scores[genre] = []
                genre_scores[genre].append(interest_weights.get(interest, 0))
        
        return {genre: round(np.mean(scores), 2) for genre, scores in genre_scores.items()}
    
    def _get_genre_popularity(self):
        """Calculate genre popularity (% very interested)"""
        genre_popularity = {}
        total_responses = len(self.transformed_data['responses'])
        
        for response in self.transformed_data['responses']:
            for genre, interest in response.get('gameGenreInterest', {}).items():
                if genre not in genre_popularity:
                    genre_popularity[genre] = 0
                if interest == 'Very Interested':
                    genre_popularity[genre] += 1
        
        return {genre: round((count / total_responses) * 100, 1) 
                for genre, count in genre_popularity.items()}
    
    def _get_data_quality_metrics(self):
        """Get data quality metrics"""
        responses = self.transformed_data['responses']
        total = len(responses)
        
        return {
            'totalResponses': total,
            'responsesWithToolExperience': len([r for r in responses if r['proceduralToolsExperience']]),
            'responsesWithGenreInterest': len([r for r in responses if r['gameGenreInterest']]),
            'responsesWithGameEngines': len([r for r in responses if r['gameEngines']]),
            'completionRate': round((total / total) * 100, 1) if total > 0 else 0
        }
    
    def _get_response_completeness(self):
        """Analyze response completeness"""
        responses = self.transformed_data['responses']
        total = len(responses)
        
        completeness = {}
        key_fields = ['professionalRole', 'yearsExperience', 'gameEngines', 'proceduralToolsExperience']
        
        for field in key_fields:
            complete_responses = 0
            for r in responses:
                if field == 'gameEngines' and r[field]:
                    complete_responses += 1
                elif field == 'proceduralToolsExperience' and r[field]:
                    complete_responses += 1
                elif r.get(field):
                    complete_responses += 1
            
            completeness[field] = round((complete_responses / total) * 100, 1)
        
        return completeness
    
    def _get_cross_tabulations(self):
        """Generate useful cross-tabulations"""
        responses = self.transformed_data['responses']
        
        # Experience vs Role
        exp_role_cross = {}
        for r in responses:
            if r['yearsExperience'] and r['professionalRole']:
                key = f"{r['yearsExperience']}__{r['professionalRole']}"
                exp_role_cross[key] = exp_role_cross.get(key, 0) + 1
        
        # Engine vs Experience  
        engine_exp_cross = {}
        for r in responses:
            if r['yearsExperience'] and r['gameEngines']:
                for engine in r['gameEngines']:
                    key = f"{engine}__{r['yearsExperience']}"
                    engine_exp_cross[key] = engine_exp_cross.get(key, 0) + 1
        
        return {
            'experienceByRole': exp_role_cross,
            'engineByExperience': engine_exp_cross
        }
    
    def save_json(self, filename='survey-data.json'):
        """Save transformed data as JSON"""
        if not self.transformed_data:
            self.transform()
            
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.transformed_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved {len(self.transformed_data['responses'])} responses to {filename}")
        return filename
    
    def save_analysis(self, filename='survey-analysis.json'):
        """Save analysis results as JSON"""
        analysis = self.analyze()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Saved analysis to {filename}")
        return filename
    
    def generate_survey_schema(self):
        """Generate survey schema with all questions and their possible options"""
        if not self.transformed_data:
            self.transform()
        
        responses = self.transformed_data['responses']
        
        # Extract unique values for each field
        def get_unique_values(field_name, is_multi_select=False):
            values = set()
            for response in responses:
                value = response.get(field_name)
                if is_multi_select and isinstance(value, list):
                    values.update(value)
                elif value and not is_multi_select:
                    values.add(value)
            # Filter out NaN values and convert to list
            filtered_values = [v for v in values if pd.notna(v) and v != '']
            return sorted(filtered_values)
        
        def get_matrix_options(field_name):
            options = {}
            for response in responses:
                matrix = response.get(field_name, {})
                for key, value in matrix.items():
                    if key not in options:
                        options[key] = set()
                    if value and pd.notna(value):
                        options[key].add(value)
            # Filter out NaN values and sort
            return {key: sorted([v for v in values if pd.notna(v) and v != '']) 
                   for key, values in options.items()}
        
        schema = {
            "metadata": {
                "title": "Procedural Level Generation Survey",
                "version": "2.0",
                "totalQuestions": 21,
                "generatedAt": datetime.now().isoformat()
            },
            "questions": [
                {
                    "id": "professionalRole",
                    "question": "How would you primarily describe your professional role?",
                    "type": "single_select",
                    "options": get_unique_values('professionalRole')
                },
                {
                    "id": "yearsExperience", 
                    "question": "How many years of experience do you have in game development?",
                    "type": "single_select",
                    "options": get_unique_values('yearsExperience')
                },
                {
                    "id": "gameEngines",
                    "question": "Which game engine(s) do you primarily work with? (Select all that apply)",
                    "type": "multi_select",
                    "options": get_unique_values('gameEngines', True)
                },
                {
                    "id": "proceduralToolsExperience",
                    "question": "How would you rate your current experience with the following procedural tools?",
                    "type": "matrix",
                    "tools": list(self.tool_columns),
                    "options": get_matrix_options('proceduralToolsExperience')
                },
                {
                    "id": "proceduralGenerationAspects",
                    "question": "If you use procedural generation, what aspects do you currently use it for? (Select all that apply)",
                    "type": "multi_select", 
                    "options": get_unique_values('proceduralGenerationAspects', True)
                },
                {
                    "id": "proceduralLevelGenFrequency",
                    "question": "How frequently do you incorporate procedural level generation (not just world building) in your design workflow?",
                    "type": "single_select",
                    "options": get_unique_values('proceduralLevelGenFrequency')
                },
                {
                    "id": "primaryConcerns",
                    "question": "What are your primary concerns when considering procedural level generation? (Select up to 3)",
                    "type": "multi_select",
                    "options": get_unique_values('primaryConcerns', True)
                },
                {
                    "id": "viewOnPCGTools",
                    "question": "Which statement best describes your view on procedural level generation tools?",
                    "type": "single_select",
                    "options": get_unique_values('viewOnPCGTools')
                },
                {
                    "id": "criticalFactors",
                    "question": "What do you consider the most critical factor when evaluating a new design tool? (Select up to 3)",
                    "type": "multi_select",
                    "options": get_unique_values('criticalFactors', True)
                },
                {
                    "id": "nodeBasedFeatures",
                    "question": "If using a node-based tool for creating a procedural level generator, which features would be most important to you? (Rank top 3)",
                    "type": "ranking",
                    "options": get_unique_values('nodeBasedFeatures')
                },
                {
                    "id": "realTimeFeedbackImportance",
                    "question": "How important is real-time feedback when configuring a procedural level generator?",
                    "type": "single_select",
                    "options": get_unique_values('realTimeFeedbackImportance')
                },
                {
                    "id": "preferredApproach",
                    "question": "Which approach to creating procedural generators would you prefer?",
                    "type": "single_select",
                    "options": get_unique_values('preferredApproach')
                },
                {
                    "id": "integrationLevel",
                    "question": "What level of integration would you prefer for a PCG level generation tool?",
                    "type": "single_select",
                    "options": get_unique_values('integrationLevel')
                },
                {
                    "id": "gameGenreInterest",
                    "question": "If your project were of the following game genre, how interested would you be in using procedural level generation?",
                    "type": "matrix",
                    "genres": list(self.genre_columns),
                    "options": get_matrix_options('gameGenreInterest')
                },
                {
                    "id": "levelRepresentation",
                    "question": "How are levels typically represented and stored in your projects, especially when procedurally generated? (Select all that apply)",
                    "type": "multi_select",
                    "options": get_unique_values('levelRepresentation', True)
                },
                {
                    "id": "levelGenerationApproach",
                    "question": "Which of these approaches to level generation would be most useful to your workflow? (Select one)",
                    "type": "single_select",
                    "options": get_unique_values('levelGenerationApproach')
                },
                {
                    "id": "aiRole",
                    "question": "What role would you prefer AI to play in your procedural level generation workflow? (Select up to 2)",
                    "type": "multi_select",
                    "options": get_unique_values('aiRole', True)
                },
                {
                    "id": "aiImportance",
                    "question": "When considering AI-assisted procedural level design, which is most important to you? (Select up to 2)",
                    "type": "multi_select",
                    "options": get_unique_values('aiImportance', True)
                },
                {
                    "id": "aiConcerns",
                    "question": "What concerns you most about using AI in procedural level generation? (Select up to 2)",
                    "type": "multi_select",
                    "options": get_unique_values('aiConcerns', True)
                },
                {
                    "id": "problemsToSolve",
                    "question": "Which problems do you wish a procedural level generation tool could solve for you?",
                    "type": "open_text",
                    "options": [],
                    "note": "Open-ended text responses"
                },
                {
                    "id": "mostImportantProblem",
                    "question": "What is the single most important problem you would want a procedural level generation tool to solve in your workflow?",
                    "type": "open_text",
                    "options": [],
                    "note": "Open-ended text responses"
                }
            ]
        }
        
        return schema
    
    def save_schema(self, filename='survey-schema.json'):
        """Save survey schema with questions and options"""
        schema = self.generate_survey_schema()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved survey schema ({len(schema['questions'])} questions) to {filename}")
        return filename
    
    def export_for_js(self, data_file='survey-data.json', analysis_file='survey-analysis.json', schema_file='survey-schema.json'):
        """Export data, analysis, and schema for JavaScript apps"""
        self.save_json(data_file)
        self.save_analysis(analysis_file)
        self.save_schema(schema_file)
        
        # Print summary
        if self.transformed_data:
            print(f"\n📊 Survey Export Complete:")
            print(f"   Total responses: {len(self.transformed_data['responses'])}")
            
            # File size estimation
            json_str = json.dumps(self.transformed_data)
            size_kb = len(json_str.encode('utf-8')) / 1024
            print(f"   JSON file size: ~{size_kb:.1f}KB")
            
            # Data quality metrics
            analysis = self.analyze()
            quality = analysis['insights']['dataQuality']
            print(f"   Complete responses: {quality['responsesWithToolExperience']}/{quality['totalResponses']}")
            
            # Schema info
            schema = self.generate_survey_schema()
            print(f"   Survey questions: {len(schema['questions'])}")


def main():
    """Transform survey data for JavaScript applications"""
    
    print("🚀 Survey Data Transformer v2.0\n")
    
    # Initialize transformer
    transformer = SurveyTransformer('procedural-level-generation-survey.csv')
    
    # Transform and export for JavaScript (now includes schema)
    transformer.export_for_js()
    
    # Get analysis for insights
    analysis = transformer.analyze()
    
    # Print key insights
    print(f"\n🔍 Key Insights:")
    
    # Tool experience
    tool_scores = analysis['proceduralTools']['mostExperiencedTools']
    top_tools = sorted(tool_scores.items(), key=lambda x: x[1], reverse=True)[:3]
    print(f"   Most experienced tools: {', '.join([f'{tool} ({score:.1f})' for tool, score in top_tools])}")
    
    # Tool adoption
    adoption = analysis['proceduralTools']['toolAdoptionRates']
    top_adoption = sorted(adoption.items(), key=lambda x: x[1], reverse=True)[:3]
    print(f"   Highest adoption: {', '.join([f'{tool} ({rate}%)' for tool, rate in top_adoption])}")
    
    # Genre interest
    genre_scores = analysis['gameGenres']['mostInterestingGenres']
    top_genres = sorted(genre_scores.items(), key=lambda x: x[1], reverse=True)[:3]
    print(f"   Most interesting genres: {', '.join([f'{genre} ({score:.1f})' for genre, score in top_genres])}")


if __name__ == '__main__':
    main()