import requests
from bs4 import BeautifulSoup
import json
import re

def fetch_and_parse_pcg_papers():
    """Fetch PCG workshop database and parse all papers."""

    url = "https://www.pcgworkshop.com/database.php"

    # Fetch the page
    response = requests.get(url)
    response.encoding = 'utf-8'
    html_content = response.text

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    papers = []

    # Find all document divs (each represents a paper)
    documents = soup.find_all('div', class_='document')

    for doc in documents:
        # Extract title
        title_elem = doc.find('h3', class_='title')
        title = title_elem.get_text().strip() if title_elem else None

        # Extract year
        year_elem = doc.find('h5', class_='year')
        year = int(year_elem.get_text().strip()) if year_elem else None

        # Extract authors
        authors_elem = doc.find('h4', class_='authors')
        authors = authors_elem.get_text().strip() if authors_elem else None

        # Extract abstract (inside document-accordion)
        abstract = None
        abstract_div = doc.find('div', class_='abstract')
        if abstract_div:
            # Remove the "Abstract" label and get just the text
            abstract_text = abstract_div.get_text()
            # Remove "Abstract" prefix if present
            abstract_text = re.sub(r'^\s*Abstract\s*', '', abstract_text, flags=re.IGNORECASE)
            abstract = abstract_text.strip()

        # Extract keywords
        keywords = None
        keywords_div = doc.find('div', class_='keywords')
        if keywords_div:
            keywords_text = keywords_div.get_text()
            # Remove "Keywords" prefix if present
            keywords_text = re.sub(r'^\s*Keywords\s*', '', keywords_text, flags=re.IGNORECASE)
            keywords = keywords_text.strip()

        # Extract citation/bibtex
        bibtex = None
        bibtex_div = doc.find('div', class_='bibtex')
        if bibtex_div:
            bibtex_text = bibtex_div.get_text()
            # Remove "Citation" prefix if present
            bibtex_text = re.sub(r'^\s*Citation\s*', '', bibtex_text, flags=re.IGNORECASE)
            bibtex = bibtex_text.strip()

        # Only add if we have at least title and year
        if title and year:
            paper_data = {
                'title': title,
                'year': year,
                'authors': authors,
                'abstract': abstract,
                'keywords': keywords,
                'citation': bibtex
            }
            papers.append(paper_data)

    # Create output structure
    if papers:
        output = {
            'source': 'PCG Workshop Database',
            'url': url,
            'total_papers': len(papers),
            'years_covered': f"{min(p['year'] for p in papers)}-{max(p['year'] for p in papers)}",
            'papers': sorted(papers, key=lambda x: (-x['year'], x['title']))
        }
    else:
        output = {
            'source': 'PCG Workshop Database',
            'url': url,
            'total_papers': 0,
            'years_covered': 'N/A',
            'papers': []
        }

    return output

def main():
    print("Fetching PCG Workshop papers...")
    data = fetch_and_parse_pcg_papers()

    if data['total_papers'] == 0:
        print("\nNo papers found! The website structure may have changed.")
        return

    # Save to JSON file
    output_file = 'pcg_workshop_papers.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nSuccessfully extracted {data['total_papers']} papers")
    print(f"Years covered: {data['years_covered']}")
    print(f"Saved to: {output_file}")

    # Print sample
    if data['papers']:
        print(f"\nSample paper:")
        sample = data['papers'][0]
        print(f"  Title: {sample['title']}")
        print(f"  Year: {sample['year']}")
        print(f"  Authors: {sample['authors']}")
        if sample.get('abstract'):
            print(f"  Abstract: {sample['abstract'][:150]}...")
        if sample.get('keywords'):
            print(f"  Keywords: {sample['keywords']}")

if __name__ == '__main__':
    main()