import re

with open('library/templates/base.html', 'r') as f:
    html = f.read()

# 1. Extract the aiChatWindowContainer block
window_pattern = re.compile(r'(<!-- Floating AI Chat Widget -->\s*<div id="aiChatWindowContainer".*?</div>\s*</div>)', re.DOTALL)
match = window_pattern.search(html)

if match:
    window_code = match.group(1)
    
    # Remove it from current place (after </nav>)
    html = html.replace(window_code, '')
    
    # Insert it before the last script tag or </body>
    if '</body>' in html:
        html = html.replace('</body>', window_code + '\n</body>')
    else:
        html += '\n' + window_code

with open('library/templates/base.html', 'w') as f:
    f.write(html)
