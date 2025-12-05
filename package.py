#!/usr/bin/env python3
"""
Package.py - Creates a distributable zip file of the website with all required files
"""

import os
import zipfile
import json
from pathlib import Path
from datetime import datetime


def get_website_files():
    """Return list of files needed for the website to function"""
    return [
        'index.html',
        'app.js',
        'procedural-level-generation-survey.json',
        'survey-questions-schema.json',
        'survey-options-mapping.json',
        'license.txt',
    ]


def anonymize_html(html_content):
    """
    Remove names and institutions from HTML for review/submission purposes
    
    Args:
        html_content (str): Original HTML content
    
    Returns:
        str: Anonymized HTML content
    """
    import re
    
    # Remove names and institutions from "About the Survey" section
    html_content = re.sub(
        r'This survey is part of doctoral research by Bojan Endrovski, supervised by Rafa Bidarra and Joris Dormans\.\s+',
        '',
        html_content
    )
    
    # Replace footer with generic text
    html_content = re.sub(
        r'<p>Supported by Delft University of Technology and Breda University of Applied Sciences</p>\s+<p>Survey Analysis Tool \| Created by Bojan Endrovski</p>',
        '<p>Survey Analysis Tool | For review purposes only</p>',
        html_content
    )
    
    # Add review notice at the top of the about section
    html_content = re.sub(
        r'(<div class="description">)',
        r'<p><strong>⚠️ This survey data is for review purposes only.</strong></p>\n                \1',
        html_content,
        count=1,
        flags=re.DOTALL
    )
    
    return html_content


def get_data_files():
    """Return list of data files to include"""
    return [
        'procedural-level-generation-survey.csv',
        'pcg_workshop_papers.json',
    ]


def create_package(output_filename=None, include_data=True, anonymize=False):
    """
    Create a zip package of the website with all necessary files
    
    Args:
        output_filename (str): Name of the output zip file (default: survey-website-{timestamp}.zip)
        include_data (bool): Whether to include data files (default: True)
        anonymize (bool): Whether to anonymize names/institutions for review (default: False)
    
    Returns:
        str: Path to created zip file
    """
    
    # Get current directory
    current_dir = Path.cwd()
    
    # Generate default filename with timestamp if not provided
    if output_filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f'survey-website-{timestamp}.zip'
    
    # Ensure output filename ends with .zip
    if not output_filename.endswith('.zip'):
        output_filename += '.zip'
    
    output_path = current_dir / output_filename
    
    print(f"Creating website package: {output_filename}")
    print(f"Output path: {output_path}")
    
    website_files = get_website_files()
    data_files = get_data_files() if include_data else []
    all_files = website_files + data_files
    
    # Track what's being added
    added_files = []
    missing_files = []
    
    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file in all_files:
                file_path = current_dir / file
                
                if file_path.exists():
                    # Special handling for index.html if anonymizing
                    if file == 'index.html' and anonymize:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        anonymized_content = anonymize_html(content)
                        zf.writestr(file, anonymized_content)
                        added_files.append(file)
                        print(f"  ✓ Added: {file} (anonymized)")
                    else:
                        # Add file to zip, preserving relative path
                        zf.write(file_path, arcname=file)
                        added_files.append(file)
                        print(f"  ✓ Added: {file}")
                else:
                    missing_files.append(file)
                    print(f"  ✗ Missing: {file}")
            
            # Create a README for the package
            readme_content = create_readme(added_files, missing_files, include_data)
            zf.writestr('README.txt', readme_content)
            print(f"  ✓ Added: README.txt")
    
    except Exception as e:
        print(f"Error creating package: {e}")
        raise
    
    print(f"\n✓ Package created successfully!")
    print(f"  Location: {output_path}")
    print(f"  Size: {output_path.stat().st_size / 1024:.1f} KB")
    print(f"  Files included: {len(added_files)}")
    
    if missing_files:
        print(f"  Files missing: {len(missing_files)}")
        for mf in missing_files:
            print(f"    - {mf}")
    
    return str(output_path)


def create_readme(added_files, missing_files, include_data):
    """Create a README file for the package"""
    
    content = []
    content.append("=" * 60)
    content.append("PROCEDURAL LEVEL GENERATION SURVEY - WEBSITE PACKAGE")
    content.append("=" * 60)
    content.append("")
    content.append(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    content.append("")
    content.append("USAGE:")
    content.append("-" * 60)
    content.append("1. Extract all files from this zip")
    content.append("2. Open 'index.html' in a web browser")
    content.append("3. The survey interface should load automatically")
    content.append("")
    content.append("INCLUDED FILES:")
    content.append("-" * 60)
    for f in added_files:
        content.append(f"  • {f}")
    content.append("")
    
    if missing_files:
        content.append("NOTE: The following files were missing and not included:")
        content.append("-" * 60)
        for f in missing_files:
            content.append(f"  • {f}")
        content.append("")
    
    content.append("REQUIREMENTS:")
    content.append("-" * 60)
    content.append("  • A modern web browser (Chrome, Firefox, Safari, Edge)")
    content.append("  • No server or installation required")
    content.append("  • All functionality is client-side")
    content.append("")
    content.append("FEATURES:")
    content.append("-" * 60)
    content.append("  • Interactive survey analysis dashboard")
    content.append("  • Real-time filtering and visualization")
    content.append("  • Demographic breakdown charts")
    content.append("  • Question statistics and analytics")
    content.append("")
    content.append("=" * 60)
    
    return "\n".join(content)


if __name__ == '__main__':
    import sys
    
    output_file = None
    include_data = True
    anonymize = False
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    if '--no-data' in sys.argv:
        include_data = False
    if '--anonymize' in sys.argv:
        anonymize = True
    
    try:
        zip_path = create_package(output_file, include_data, anonymize)
        print(f"\nPackage ready at: {zip_path}")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
