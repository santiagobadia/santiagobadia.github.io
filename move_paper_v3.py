with open('_site/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
# Simpler pattern that matches the row containing the DOI
# We look for the pub-row start and the specific DOI, then until the end of that row's container structure
pattern = r'<div class="pub-row">\s*<div class="pub-thumb">.*?10\.1007/s10208-025-09734-6.*?</div>\s*</div>\s*</div>'
match = re.search(pattern, content, re.DOTALL)

if not match:
    # Maybe it has no thumb? (But this one should have one based on user screenshot)
    pattern = r'<div class="pub-row">.*?10\.1007/s10208-025-09734-6.*?</div>\s*</div>'
    match = re.search(pattern, content, re.DOTALL)

if match:
    block = match.group(0)
    print("Found block to move")
    content = content.replace(block, "")
    block = block.replace(", 2024", ", 2025")
    
    target = '<h2>2025</h2>
    <div class="publications-grid">'
    if target in content:
        content = content.replace(target, target + "
      " + block)
        with open('_site/index.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Moved successfully")
    else:
        # Try without newline
        target = '<h2>2025</h2><div class="publications-grid">'
        if target in content:
             content = content.replace(target, target + block)
             with open('_site/index.html', 'w', encoding='utf-8') as f:
                f.write(content)
             print("Moved successfully (alt target)")
        else:
            print("Target 2025 grid not found")
else:
    print("Block not found with regex")
