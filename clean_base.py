import re

with open('library/templates/base.html', 'r') as f:
    lines = f.readlines()

# The garbage is likely between the </nav> and the first real section or footer
# Based on previous view_file:
# 137:     </nav>
# 138: 
# 139:         
# 140:                     <div>
# ...
# 209: 
# 210:     {% block content %}{% endblock %}

# Let's target the block from 139 to 209
# Actually, I'll just look for the first <div>...</div> block after </nav> that isn't supposed to be there.

# Re-read the whole thing
content = "".join(lines)

# Target the specific broken block
# It starts after </nav> and ends before {% block content %}
broken_pattern = re.compile(r'</nav>\s*<div>.*?</div>\s*(?={% block content %})', re.DOTALL)
content = broken_pattern.sub('</nav>\n\n    ', content)

with open('library/templates/base.html', 'w') as f:
    f.write(content)
