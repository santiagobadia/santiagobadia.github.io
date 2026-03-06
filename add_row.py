import json
import re

with open('_site/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

doi = "10.1016/j.jcp.2025.114547"
title = "Unfitted finite element interpolated neural networks"
authors = "Wei Li, Alberto F. Martín, Santiago Badia"
year = "2026"
journal = "Journal of Computational Physics"
url = f"https://doi.org/{doi}"
arxiv = "2407.13314"
image = "/assets/images/publications/10.1016_j.jcp.2025.114547.png"

row_html = f"""
      <div class="pub-row">
        <div class="pub-thumb">
          <div class="thumb-box">
            <img src="{image}" alt="{title}">
          </div>
        </div>
        <div class="pub-content">
          <div class="pub-title">
            <a href="{url}">{title}</a>
          </div>
          <div class="pub-authors">{authors}</div>
          <div class="pub-venue">
            <em>{journal}</em>, {year}
          </div>
          <div class="pub-links">
              <a href="{url}">DOI</a>
               / 
              <a href="https://arxiv.org/abs/{arxiv}">arXiv</a>
          </div>
        </div>
      </div>"""

# Find <h2>2026</h2>
target = '<h2>2026</h2>
    <div class="publications-grid">'
if target in content:
    content = content.replace(target, target + "
" + row_html)
    with open('_site/index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Added JCP paper to 2026 section")
else:
    print("2026 section not found")
