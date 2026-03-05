import os
import re
import json
import urllib.request
import time

arxiv_data = {
    "2506.11956": "Analysis of BDDC preconditioners for non-conforming polytopal hybrid discretisation methods",
    "2508.15320": "Reduced basis solvers for unfitted methods on parameterized domains",
    "2508.17705": "Energy minimisation using overlapping tensor-product free-knot B-splines",
    "2508.17687": "A convergence framework for energy minimisation of linear self-adjoint elliptic PDEs in nonlinear approximation spaces",
    "2409.15863": "A discrete trace theory for non-conforming polytopal hybrid discretisation methods",
    "2411.08064": "Energy and entropy conserving compatible finite elements with upwinding for the thermal shallow water equations",
    "2411.04591": "Compatible finite element interpolated neural networks",
    "2403.14054": "Adaptive Finite Element Interpolated Neural Networks",
    "2410.13023": "STLCutters.jl: A scalable geometrical framework library for unfitted finite element discretisations",
    "2405.10478": "GridapTopOpt.jl: A scalable Julia toolbox for level set-based topology optimisation",
    "2401.12649": "Space-time unfitted finite elements on moving explicit geometry representations",
    "2311.14363": "High order unfitted finite element discretizations for explicit boundary representations",
    "2303.13672": "Neural Level Set Topology Optimization Using Unfitted Finite Elements",
    "2303.11617": "Adaptive quadratures for nonlinear approximation of low-dimensional PDEs using smooth neural networks",
    "2307.10605": "Model order reduction with novel discrete empirical interpolation methods in space-time",
    "2306.06304": "Finite element interpolated neural networks for solving forward and inverse problems",
    "2306.11213": "Efficient and reliable divergence-conforming methods for an elasticity-poroelasticity interface problem",
    "2206.03626": "Space-time unfitted finite element methods for time-dependent problems on moving domains",
    "2208.08538": "Stability and conditioning of immersed finite element methods: analysis and remedies",
    "2201.06632": "Robust high-order unfitted finite elements by interpolation-based discrete extension",
    "2207.10975": "Bound-preserving finite element approximations of the Keller-Segel equations",
    "2109.09983": "Conditioning of a Hybrid High-Order scheme on meshes with small faces",
    "2110.01378": "Geometrical discretisations for unfitted finite elements on explicit boundary representations"
}

def clean_latex(text):
    if not text:
        return ""
    text = text.replace('\\textendash', '-')
    text = text.replace('\\textemdash', '--')
    text = text.replace('\"', '')
    text = text.replace("\'.", "")
    text = text.replace('\\`', '')
    text = text.replace('\\~', '')
    text = text.replace('\\=', '')
    text = text.replace('\\', '')
    text = text.replace('{', '').replace('}', '')
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def normalize_title(text):
    if not text: return ""
    # remove non-alphanumeric and lowercase for comparison
    return re.sub(r'[^a-z0-9]', '', clean_latex(text).lower())

def get_arxiv_info(arxiv_id):
    # Fetch title and authors from arXiv API
    url = f'http://export.arxiv.org/api/query?id_list={arxiv_id}'
    try:
        with urllib.request.urlopen(url) as response:
            xml_data = response.read().decode('utf-8')
            
            title_match = re.search(r'<entry>\s*<id>.*?</id>.*?<title>(.*?)</title>', xml_data, re.DOTALL)
            title = clean_latex(title_match.group(1).replace('\n', ' ')) if title_match else ""
            
            authors_matches = re.findall(r'<author>\s*<name>(.*?)</name>', xml_data, re.DOTALL)
            authors = ", ".join(authors_matches) if authors_matches else "Santiago Badia et al."
            
            year_match = re.search(r'<published>(\d{4})', xml_data)
            year = year_match.group(1) if year_match else "20" + arxiv_id[:2]
            
            doi_match = re.search(r'<arxiv:doi xmlns:arxiv="http://arxiv.org/schemas/atom">(.*?)</arxiv:doi>', xml_data)
            doi = doi_match.group(1) if doi_match else ""

            journal_match = re.search(r'<arxiv:journal_ref xmlns:arxiv="http://arxiv.org/schemas/atom">(.*?)</arxiv:journal_ref>', xml_data)
            journal = journal_match.group(1) if journal_match else "arXiv"

            return {
                "title": title,
                "authors": authors,
                "year": year,
                "doi": doi,
                "journal": journal
            }
    except Exception as e:
        print(f"Error fetching {arxiv_id}: {e}")
        return None

def main():
    home = os.path.expanduser('~')
    doi_bib = os.path.join(home, 'gh/santiagobadia/resume/bib/doi-works.bib')
    arxiv_bib = os.path.join(home, 'gh/santiagobadia/resume/bib/arxiv-works.bib')
    
    def parse_file(path):
        if not os.path.exists(path): return []
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        entries = re.findall(r'@(article|misc)\{(.*?),\s*(.*?)\n\}', content, re.DOTALL)
        results = []
        for etype, eid, ebody in entries:
            def get_field(field_name, body):
                pattern1 = field_name + " = {"
                pattern2 = field_name + " = \""
                
                idx1 = body.find(pattern1)
                idx2 = body.find(pattern2)
                
                if idx1 != -1:
                    start = idx1 + len(pattern1)
                    end = body.find("}", start)
                    return body[start:end]
                elif idx2 != -1:
                    start = idx2 + len(pattern2)
                    end = body.find("\"", start)
                    return body[start:end]
                else:
                    m = re.search(field_name + r'\s*=\s*(\d+)', body)
                    if m:
                        return m.group(1)
                return ""

            title = get_field('title', ebody)
            # clean up (**)
            title = title.replace('(**)', '').strip()
            authors = get_field('author', ebody)
            year = get_field('year', ebody)
            journal = get_field('journal', ebody)
            volume = get_field('volume', ebody)
            pages = get_field('pages', ebody)
            doi = get_field('doi', ebody)
            url = get_field('url', ebody)
            arxiv = get_field('eprint', ebody)
            
            if not journal and etype == 'misc':
                journal = "arXiv"

            results.append({
                'id': eid,
                'title': clean_latex(title),
                'authors': clean_latex(authors).replace(' and ', ', '),
                'year': year,
                'journal': clean_latex(journal),
                'volume': clean_latex(volume),
                'pages': clean_latex(pages),
                'doi': doi,
                'url': url,
                'arxiv': arxiv
            })
        return results

    pubs_doi = parse_file(doi_bib)
    pubs_arxiv = parse_file(arxiv_bib)
    
    merged_pubs = {}
    
    # First, add all DOI publications
    for p in pubs_doi:
        # Use normalized title as key to merge
        ntitle = normalize_title(p['title'])
        merged_pubs[ntitle] = p
        
    # Then merge arXiv ones
    for p in pubs_arxiv:
        ntitle = normalize_title(p['title'])
        if ntitle in merged_pubs:
            # Merge arxiv info into existing DOI pub
            merged_pubs[ntitle]['arxiv'] = p.get('arxiv', '')
            if not merged_pubs[ntitle]['arxiv'] and p.get('url', ''):
                # fallback id
                if "arxiv" in p.get('url', ''):
                    match = re.search(r'abs/([\d\.]+)', p['url'])
                    if match:
                        merged_pubs[ntitle]['arxiv'] = match.group(1)
        else:
            merged_pubs[ntitle] = p
            
    # Also incorporate the specific arxiv_data list from the user's PDF
    for aid, atitle in arxiv_data.items():
        ntitle = normalize_title(atitle)
        if ntitle in merged_pubs:
            merged_pubs[ntitle]['arxiv'] = aid
            # if the title was weird, replace with proper one from arxiv_data
            if merged_pubs[ntitle]['title'].startswith("Recent work on arXiv"):
                merged_pubs[ntitle]['title'] = atitle
        else:
            print(f"Fetching arXiv metadata for {aid}...")
            # We don't have it at all, let's fetch metadata from arxiv to get authors
            arxiv_meta = get_arxiv_info(aid)
            time.sleep(1) # respectful delay
            
            if arxiv_meta:
                merged_pubs[ntitle] = {
                    'id': aid,
                    'title': arxiv_meta['title'],
                    'authors': arxiv_meta['authors'], 
                    'year': arxiv_meta['year'],
                    'journal': arxiv_meta['journal'],
                    'volume': "",
                    'pages': "",
                    'doi': arxiv_meta['doi'],
                    'url': f"https://arxiv.org/abs/{aid}",
                    'arxiv': aid
                }
            else:
                merged_pubs[ntitle] = {
                    'id': aid,
                    'title': atitle,
                    'authors': "Santiago Badia et al.", 
                    'year': "20" + aid[:2],
                    'journal': "arXiv",
                    'volume': "",
                    'pages': "",
                    'doi': "",
                    'url': f"https://arxiv.org/abs/{aid}",
                    'arxiv': aid
                }
            
    final_list = list(merged_pubs.values())
    final_list.sort(key=lambda x: str(x.get('year', '0')), reverse=True)
    
    with open('publications.json', 'w', encoding='utf-8') as f:
        json.dump(final_list, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()