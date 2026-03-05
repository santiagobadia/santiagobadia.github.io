import json
import re
import os

def clean_latex_smart(text):
    if not text:
        return ''
    
    text = text.replace('\textendash', '-')
    text = text.replace('\textemdash', '--')
    
    # 1. Broadly clean up common co-author names using exact mappings
    # This is much safer than complex regex for a known dataset
    fixes = {
        "Jes'us": "Jesús",
        "Jes'u": "Jesús",
        "Mart'in": "Martín",
        "Mart'i": "Martín",
        "Guti'errez": "Gutiérrez",
        "Guti'e": "Gutiérrez",
        "Guill'en": "Guillén",
        "Guill'e": "Guillén",
        "Colom'es": "Colomés",
        "Colom'e": "Colomés",
        "J'er'emie": "Jérémie",
        "J'e": "Jérémie",
        "Kj'ol": "kjøl",
        "Andr'e": "André"
    }

    # First handle raw LaTeX accents if they are still there
    # patterns like {\'u} or {\'u} or \'u or \'{u}
    text = re.sub(r'\{\\+["\'`~=^]\'?([a-zA-Z])\}?', r"\1'", text)
    text = re.sub(r'\\+["\'`~=^]\'?([a-zA-Z])\}?', r"\1'", text)
    
    # This might result in things like u' or i'
    # So let's handle those
    name_fixes = {
        "u'": "ú",
        "i'": "í",
        "e'": "é",
        "a'": "á",
        "o'": "ó",
        "n~": "ñ",
        "u\"": "ü"
    }
    
    # Actually, it's easier to just strip braces and backslashes 
    # and THEN apply the mapping for known co-author strings
    
    text = text.replace('$', '')
    text = text.replace('{', '').replace('}', '')
    text = text.replace('\\', '')
    
    # Now text might be "Jes'us Bonilla" or "Alberto F. Mart'in"
    for bad, good in fixes.items():
        text = text.replace(bad, good)
        
    for bad, good in name_fixes.items():
        text = text.replace(bad, good)
    
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_field(body, field_name):
    # Case insensitive search for field_name = {
    match = re.search(rf'{field_name}\s*=\s*{{', body, re.IGNORECASE)
    if not match:
        return ''
    
    start = match.end()
    brace_count = 1
    for i in range(start, len(body)):
        if body[i] == '{': brace_count += 1
        elif body[i] == '}': brace_count -= 1
        if brace_count == 0:
            return body[start:i]
    return ''

def main():
    home = os.path.expanduser('~')
    doi_bib = os.path.join(home, 'gh/santiagobadia/resume/bib/doi-works.bib')
    arxiv_bib = os.path.join(home, 'gh/santiagobadia/resume/bib/arxiv-works.bib')

    raw_data = {}

    def process_bib(path):
        if not os.path.exists(path): return
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split entries by @
        entries = content.split('\n@')
        for entry in entries:
            if not entry.strip(): continue
            try:
                first_brace = entry.find('{')
                first_comma = entry.find(',')
                eid = entry[first_brace+1:first_comma].strip()
                
                title = extract_field(entry, 'title')
                authors = extract_field(entry, 'author')
                
                if eid:
                    raw_data[eid] = {
                        'title': clean_latex_smart(title),
                        'authors': clean_latex_smart(authors).replace(' and ', ', ')
                    }
            except:
                continue

    process_bib(doi_bib)
    process_bib(arxiv_bib)

    with open('_data/publications.json', 'r') as f:
        pubs = json.load(f)

    for p in pubs:
        lookup_ids = [p.get('id')]
        if p.get('doi'):
            lookup_ids.append(p['doi'].replace('/', '_'))
            
        found = False
        for lid in lookup_ids:
            if lid in raw_data:
                p['title'] = raw_data[lid]['title']
                p['authors'] = raw_data[lid]['authors']
                found = True
                break
        
        if not found:
            p_title_norm = re.sub(r'[^a-z0-9]', '', p['title'].lower())
            for eid, data in raw_data.items():
                r_title_norm = re.sub(r'[^a-z0-9]', '', data['title'].lower())
                if p_title_norm == r_title_norm:
                    p['authors'] = data['authors']
                    break

    with open('_data/publications.json', 'w') as f:
        json.dump(pubs, f, indent=4, ensure_ascii=False)
    print("Final author fix completed.")

if __name__ == "__main__":
    main()