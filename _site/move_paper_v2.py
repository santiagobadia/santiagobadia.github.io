with open('_site/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Look for the row containing the DOI
import re
# Find all pub-rows
rows = content.split('<div class="pub-row">')
new_rows = [rows[0]]
block_to_move = None

for row in rows[1:]:
    # We need to re-add the prefix because we split on it
    full_row_content = '<div class="pub-row">' + row
    if "10.1007/s10208-025-09734-6" in full_row_content:
        # This is the row to move. 
        # But wait, we need to find WHERE it ends.
        # Since they are nested or just sequential, let's look for the next pub-row or end of grid.
        # Actually, let's just find the end of the div.
        # It's better to use a regex that matches the whole block until the next <div class="pub-row"> or </div>\s*</div> (end of grid)
        match = re.search(r'<div class="pub-row">.*?(?=<div class="pub-row">|</div>\s*</div>\s*</div>\s*<h2>)', full_row_content, re.DOTALL)
        if match:
            block_to_move = match.group(0)
            # Remove it from here
            # But the 'row' variable is just a part of the split.
            # This logic is a bit flawed. Let's try re.sub
            continue
    new_rows.append(row)

# Let's try again with a better regex on the WHOLE content
pattern = r'<div class="pub-row">.*?10\.1007/s10208-025-09734-6.*?</div>\s*</div>\s*</div>'
match = re.search(pattern, content, re.DOTALL)
if match:
    block = match.group(0)
    print("Found block to move")
    content = content.replace(block, "")
    block = block.replace("2024", "2025")
    # Insert at top of 2025
    target = '<h2>2025</h2>
    <div class="publications-grid">'
    if target in content:
        content = content.replace(target, target + "
      " + block)
        with open('_site/index.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Moved successfully")
    else:
        print("Target 2025 grid not found")
else:
    print("Block not found with regex")
