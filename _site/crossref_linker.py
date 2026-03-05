import os
import re
import json
import urllib.request
import time
from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def get_crossref_metadata(doi):
    url = f"https://api.crossref.org/works/{doi}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'AcademicProfileBuilder/1.0 (mailto:test@example.com)'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))['message']
            
            title = data.get('title', [''])[0]
            
            authors_list = data.get('author', [])
            authors = ", ".join([f"{a.get('given', '')} {a.get('family', '')}".strip() for a in authors_list])
            
            # Get year
            year = ""
            if 'published-print' in data:
                year = str(data['published-print']['date-parts'][0][0])
            elif 'published-online' in data:
                year = str(data['published-online']['date-parts'][0][0])
            elif 'issued' in data:
                year = str(data['issued']['date-parts'][0][0])
                
            journal = data.get('container-title', [''])[0]
            volume = data.get('volume', '')
            pages = data.get('page', '')
            
            return {
                "title": title,
                "authors": authors,
                "year": year,
                "journal": journal,
                "volume": volume,
                "pages": pages,
                "doi": doi,
                "url": f"https://doi.org/{doi}"
            }
    except Exception as e:
        print(f"Failed to fetch Crossref for {doi}: {e}")
        return None

def normalize_title(text):
    if not text: return ""
    return re.sub(r'[^a-z0-9]', '', text.lower())

def main():
    pub_dir = os.path.expanduser('~/gh/articles/02_published/')
    
    # 1. Get all DOIs from folders
    dois = []
    if os.path.exists(pub_dir):
        for folder in os.listdir(pub_dir):
            # match folder patterns like 2025-10.1016:j.cma.2025.118610 or 202X-10.1007:s10208-025-09734-6
            match = re.search(r'\d{3}[0-9X]-(10\..+)', folder)
            if match:
                doi = match.group(1).replace(':', '/')
                dois.append(doi)
            elif folder.startswith("10."):
                doi = folder.replace(':', '/')
                dois.append(doi)
                
    print(f"Found {len(dois)} DOIs in {pub_dir}")
    
    # 2. Load current publications.json
    with open('publications.json', 'r', encoding='utf-8') as f:
        pubs = json.load(f)
        
    # Create a quick lookup for existing DOIs in our json
    existing_dois = {p.get('doi'): p for p in pubs if p.get('doi')}
    
    # 3. Fetch metadata for DOIs and merge
    new_pubs_from_crossref = []
    for doi in dois:
        if doi in existing_dois:
            # We already have this DOI, just ensure formatting is good
            continue
            
        print(f"Fetching metadata for {doi}...")
        meta = get_crossref_metadata(doi)
        time.sleep(0.2) # rate limiting
        
        if meta:
            new_pubs_from_crossref.append(meta)

    # 4. Merge new Crossref data with existing arXiv data
    for c_pub in new_pubs_from_crossref:
        c_title_norm = normalize_title(c_pub['title'])
        matched = False
        
        for p in pubs:
            p_title_norm = normalize_title(p['title'])
            
            # Match if titles are very similar (sometimes arxiv titles differ slightly from published)
            if similar(c_title_norm, p_title_norm) > 0.85:
                print(f"Merging arXiv {p.get('arxiv')} with DOI {c_pub['doi']}")
                # Update the existing entry with full published details, but keep arxiv link
                p['title'] = c_pub['title']
                p['authors'] = c_pub['authors'] if c_pub['authors'] else p['authors']
                p['year'] = c_pub['year']
                p['journal'] = c_pub['journal']
                p['volume'] = c_pub['volume']
                p['pages'] = c_pub['pages']
                p['doi'] = c_pub['doi']
                p['url'] = c_pub['url'] # prefer DOI url over arxiv url
                if 'id' in p and not p['id'].startswith('10.'):
                    p['id'] = c_pub['doi'].replace('/', '_')
                matched = True
                break
                
        if not matched:
            # This is a published paper that had no arXiv equivalent in our list
            c_pub['id'] = c_pub['doi'].replace('/', '_')
            c_pub['arxiv'] = ""
            pubs.append(c_pub)
            
    # Re-sort by year
    pubs.sort(key=lambda x: str(x.get('year', '0')), reverse=True)
    
    with open('publications.json', 'w', encoding='utf-8') as f:
        json.dump(pubs, f, indent=4, ensure_ascii=False)
        
    print("Done. publications.json has been updated with full journal info.")

if __name__ == "__main__":
    main()
