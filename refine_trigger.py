import re

with open('library/templates/base.html', 'r') as f:
    html = f.read()

# Current button location is between login and signup
# Let's move it to the end of the flex container

btn_code_pattern = re.compile(r'(<!-- Floating Toggle Button -->\s*<button id="chatbotToggleBtn".*?</button>)', re.DOTALL)
match = btn_code_pattern.search(html)

if match:
    btn_code = match.group(1)
    # Remove it from current place
    html = html.replace(btn_code, '')
    
    # Insert it at the end of the space-x-4 div
    # Find the closing tag of that div
    # The div is <div class="flex items-center space-x-4">
    
    # More robust way: find the </a> wrapping Join Now and insert after it
    join_now_pattern = re.compile(r'(<a href="{% url \'signup\' %}">.*?</a>)', re.DOTALL)
    join_now_match = join_now_pattern.search(html)
    if join_now_match:
        html = html.replace(join_now_match.group(1), join_now_match.group(1) + '\n                ' + btn_code)

with open('library/templates/base.html', 'w') as f:
    f.write(html)
