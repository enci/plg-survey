#!/usr/bin/env python3

import pandas as pd
import json

class survey_transformer:
    def __init__(self, csv_file):
        self.parsed_data = pd.read_csv(csv_file)
        self.transformed_data = []

    def transform(self):
        self.transformed_data = []
        for index, row in self.parsed_data.iterrows():
            transformed_row = {
                "id": row['Id'],                
            }
            self.transformed_data.append(transformed_row)
    
    def save(self, output_file):
        with open(output_file, 'w') as f:
            json.dump(self.transformed_data, f, indent=4)
        print(f"Data saved to {output_file}")


def main():
    print("📊 Survey Transformer v13.0\n")

    input_file_path = "Procedural Level Generation Survey.csv"
    output_file_path = "Procedural Level Generation Survey.json"

    transform = survey_transformer(input_file_path)
    transform.transform()
    transform.save(output_file_path)

if __name__ == "__main__":
    main()
    print("✅ Transformation complete. Data ready for use.")
    # You can add code here to save transformed_data to a file or process it further. 

