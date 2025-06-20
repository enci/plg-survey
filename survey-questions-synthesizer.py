#!/usr/bin/env python3

import pandas as pd
import json
import re

class survey_questions_synthesizer:
    def __init__(self):
        self.questions_schema = {}
    
    def synthesize_questions(self):
        """Create comprehensive questions schema from CSV structure"""
        
        # Define the questions structure
        questions = {    

            # 0 - Identifier
            "id": {
                "question": "Id",
                "type": "identifier",
                "required": True
            },

            # 1        
            "professional_role": {
                "question": "How would you primarily describe your professional role?",
                "type": "single_choice",
                "options": [
                    "Level Designer",
                    "Game Designer",
                    "Technical Artist",
                    "Environment Artist",
                    "Programmer/Technical Designer",
                    "Academic/Researcher"
                ],
            },
            
            # 2
            "years_experience": {
                "question": "How many years of experience do you have in game development?",
                "type": "single_choice", 
                "options": ["0-2 years", "3-5 years", "6-10 years", "10+ years"]
            },
            
            # 3
            "game_engines": {
                "question": "Which game engine(s) do you primarily work with? (Select all that apply)",
                "type": "multiple_choice",
                "options": [
                    "Unity",
                    "Unreal Engine",
                    "Godot",
                    "Custom in-house engine", 
                    "GameMaker",
                ],
                "has_other": True
            },
            
            # 4
            "procedural_tools_experience": {
                "question": "How would you rate your current experience with the following procedural tools?",
                "type": "matrix",
                "items": [
                    "Houdini",
                    "Unreal Engine PCG tools", 
                    "Blender Geometry Nodes",
                    "Plugins/Tools that use Wave Function Collapse",
                    "Plugins/Tools that use other methods",
                    "Custom code-based PCG solutions"
                ],
                "scale": ["No Experience", "Limited Experience", "Moderate Experience", "Extensive Experience"]
            },
            
            # 5
            "current_pcg_usage": {
                "question": "If you use procedural generation, what aspects do you currently use it for? (Select all that apply)",
                "type": "multiple_choice",
                "options": [
                    "Terrain generation", "Decorative prop placement", "Enemy/NPC placement",
                    "City models", "Vegetation/foliage", "Mission/quest generation",
                    "Level layouts", "Texture generation", "Asset variations",
                    
                ],
                "has_other": True
            },
            
            # 6
            "level_generation_frequency": {
                "question": "How frequently do you incorporate procedural level generation (not just world building) in your design workflow?",
                "type": "single_choice",
                "options": [
                    "Always (essential part of workflow)",
                    "Often (most projects)", 
                    "Sometimes (about half of projects)",
                    "Rarely (a few projects)",
                    "Never"
                ]
            },
            
            # 7
            "primary_concerns": {
                "question": "What are your primary concerns when considering procedural level generation? (Select up to 3)",
                "type": "multiple_choice",
                "max_selections": 3,
                "options": [
                    "Difficulty in debugging unexpected outputs",
                    "Integration with existing workflows", 
                    "Unpredictable results affecting game balance",
                    "All levels ending up being more of the same",
                    "Technical complexity/learning curve",
                    "Performance impact",
                    "Limited control over final output",
                    
                ],
                "has_other": True
            },
            
            # 8
            "tool_view": {
                "question": "Which statement best describes your view on procedural level generation tools?",
                "type": "single_choice",
                "options": [
                    "I'm satisfied with the current PCG tools available",
                    "Existing PCG tools are too limited in what they can generate",
                    "I prefer handcrafting levels and don't see benefits in PCG tools",
                    "Most PCG tools are built for programmers, not designers",
                    "PCG tools don't give me enough control over the final output",
                    "PCG tools are too complex to integrate into my workflow"
                ],
                "has_other": True
            },
            
            # 9
            "critical_factors": {
                "question": "What do you consider the most critical factor when evaluating a new design tool? (Select up to 3)",
                "type": "multiple_choice",
                "max_selections": 3,
                "options": [
                    "Flexibility (ability to adapt to various use cases)",
                    "Familiarity (resemblance to tools you already know)",
                    "Simplicity (low barrier to entry)",
                    "Reliability (predictable, stable results)",
                    "Feature completeness (comprehensive capabilities)",
                    "Documentation and learning resources",
                    "Integration with existing workflows",
                    "Community support",
                    

                ],
                "has_other": True
            },
            
            # 10
            "node_tool_features": {
                "question": "If using a node-based tool for creating a procedural level generator, which features would be most important to you? (Rank top 3)",
                "type": "ranking",
                "max_selections": 3,
                "options": [
                    "Visual previews of generation steps",
                    "Easy debugging of unexpected results",
                    "Pre-built common PCG patterns/techniques (WFC, graph grammars, etc.)",
                    "Ability to mix procedural and hand-crafted content",
                    "Control over generation constraints and rules",
                    "Limited or no programming required",
                    "Runtime vs. offline generation options",
                    "Support for mission/gameplay integration"
                ]
            },
            
            # 11
            "realtime_feedback_importance": {
                "question": "How important is real-time feedback when configuring a procedural level generator?",
                "type": "single_choice",
                "options": ["Essential", "Very important", "Somewhat important", "Not important"]
            },
            
            # 12
            "preferred_approach": {
                "question": "Which approach to creating procedural generators would you prefer?",
                "type": "single_choice",
                "options": [
                    "Building generators from programming primitives (maximum flexibility)",
                    "Assembling generators from pre-built, configurable components (balanced approach)",
                    "Using templates with limited parameters to adjust (simpler, less flexible)",
                    "Mixed-initiative approach where the tool learns from my examples",
                    "Assembling generators from pre-built components, with the option to write custom components",
                    
                ],
                "has_other": True
            },
            
            # 13
            "integration_preference": {
                "question": "What level of integration would you prefer for a PCG level generation tool?",
                "type": "single_choice",
                "options": [
                    "Deep integration within existing engine (like Unreal Blueprint)",
                    "Plugin that works across multiple engines",            
                    "Standalone application that exports to game engines",
                    "Web-based tool accessible from anywhere",                    
                ],
                "has_other": True
            },
            
            # 14
            # Genre Interest Matrix
            "genre_interest": {
                "question": "If your project were of the following game genre, how interested would you be in using procedural level generation?",
                "type": "matrix",
                "items": [
                    "Action/Adventure",
                    "First-person Shooters", 
                    "Platformers",
                    "Racing games",
                    "Puzzle games", 
                    "RPGs",
                    "Strategy games",
                    "Roguelikes / Roguelites"
                ],
                "scale": ["Not Interested", "Somewhat Interested", "Interested", "Very Interested"]
            },
            
            # 15
            "level_representation": {
                "question": "How are levels typically represented and stored in your projects, especially when procedurally generated? (Select all that apply)",
                "type": "multiple_choice",
                "options": [
                    "Rectangular grid/tile-based",
                    "Hexagonal grid/tile-based", 
                    "Free-form geometry",
                    "Scene graph/hierarchical structure",
                    "Graph-based (nodes and connections)",
                    "Hierarchical/nested structures",
                    "Node-based graphs (mission/flow graphs)",
                    "Navigation mesh",
                    "Constraint-based representations (is this a known term)",
                    "Voxel-based",
                    
                ],
                "has_other": True
            },

            # 16
            "most_useful_approach": {
                "question": "Which of these approaches to level generation would be most useful to your workflow? (Select one)",
                "type": "single_choice",
                "options": [
                    "Mission-driven generation (gameplay goals determine level structure)",
                    "Space-driven generation (spatial layout determines gameplay possibilities)",
                    "Balanced approach (iterative refinement between mission and space)",
                    "Context-dependent (different approaches for different game sections)",
                    "Not sure/would need to experiment"
                ]
            },
            
            # 17
            "ai_role_preference": {
                "question": "What role would you prefer AI to play in your procedural level generation workflow? (Select up to 2)",
                "type": "multiple_choice",
                "max_selections": 2,
                "options": [
                    "Assistant-based (AI helps implement your design intentions)",
                    "Suggestion-based (AI proposes level designs for you to select and modify)",
                    "Learning-based (AI learns from your design patterns and mimics your style)",
                    "Analysis-based (AI analyzes and provides feedback on generated levels)",
                    "I prefer traditional rule-based PCG without AI involvement",
                    "Tool-based (AI enhances specific components of your manual design process)",
                    "I have no opinion/not sure"
                ],

            },
            
            # 18
            "ai_importance_factors": {
                "question": "When considering AI-assisted procedural level design, which is most important to you? (Select up to 2)",
                "type": "multiple_choice",
                "max_selections": 2,
                "options": [
                    "Maintaining creative control over the final output",
                    "Understanding how the AI makes its decisions",
                    "Speed of generation compared to traditional methods",
                    "Novelty/uniqueness of the generated content",
                    "Consistency with existing game assets and style",
                    "Learning from my design preferences over time"              
                ]
            },
            
            # 19
            "ai_concerns": {
                "question": "What concerns you most about using AI in procedural level generation? (Select up to 2)",
                "type": "multiple_choice", 
                "max_selections": 2,
                "options": [
                    "Unpredictable or inconsistent results",
                    "Lack of control over the generation process",
                    "Difficulty integrating with existing tools/workflows",
                    "Potential copyright/IP issues with AI-generated content",
                    "Performance and computational requirements",
                    "Lack of specialized AI tools for level design specifically",
                    "Other (please specify)"
                ],
                "has_other": True
            },
            
            # 20
            "desired_solutions": {
                "question": "Which problems do you wish a procedural level generation tool could solve for you?",
                "type": "multiple_choice",
                "common_themes": [
                    "Time savings compared to manual design",
                    "Ability to create more content variations with consistent quality",
                    "Improved iteration speed on level designs",
                    "Reduced technical barriers to procedural generation",
                    "Better integration with existing workflows",
                    "Community/marketplace of shareable generator components",
                    "Learning resources and examples for different game genres"
                ]
            },
            
            # 21
            "most_important_problem": {
                "question": "What is the single most important problem you would want a procedural level generation tool to solve in your workflow?",
                "type": "open_text",
                "note": "This is typically a more specific version of the previous question"
            }
        }
        
        return questions
    
    def save_questions_schema(self, output_file):
        """Save the synthesized questions schema to JSON"""
        questions = self.synthesize_questions()
        
        # Add metadata
        schema = {
            "survey_metadata": {
                "title": "Procedural Level Generation Survey",
                "total_questions": len(questions),
                "question_types": {
                    "identifier": len([q for q in questions.values() if q.get('type') == 'identifier']),
                    "single_choice": len([q for q in questions.values() if q.get('type') == 'single_choice']),
                    "multiple_choice": len([q for q in questions.values() if q.get('type') == 'multiple_choice']),
                    "matrix": len([q for q in questions.values() if q.get('type') == 'matrix']),
                    "ranking": len([q for q in questions.values() if q.get('type') == 'ranking']),
                    "open_text": len([q for q in questions.values() if q.get('type') == 'open_text'])                  
                }
            },
            "questions": questions
        }
        
        with open(output_file, 'w') as f:
            json.dump(schema, f, indent=2)
                        
        # Print question type summary
        print("📋 Question Types:")
        for qtype, count in schema["survey_metadata"]["question_types"].items():
            if count > 0:
                print(f"   {qtype}: {count}")
            
        print(f"📊 Total questions: {len(questions)}")
        print(f"💾 Questions schema saved to {output_file}")
        

def main():
    print("📊 Survey Questions Synthesizer 2.0\n")    
    output_file = "survey-questions-schema.json"    
    synthesizer = survey_questions_synthesizer()
    synthesizer.save_questions_schema(output_file)

if __name__ == "__main__":
    main()
    print("\n✅ Questions schema synthesis complete!")