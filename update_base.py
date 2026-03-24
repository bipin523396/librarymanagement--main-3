import re

with open('library/templates/base.html', 'r') as f:
    content = f.read()

# 1. Look for the script block at the end and replace with partial
# Finding the entire <script> block for AI Chatbot
chatbot_script_pattern = re.compile(r'// AI Chatbot Logic.*?function dragEnd', re.DOTALL)
# Actually it's easier to find the whole <script> if it starts after footer
# Lines in my previous view around 171 started Accessibility Controls
# AI Chatbot Logic was around 255.

# Let's just find the start of AI Chatbot Logic and go to the end of that script tag
content = re.sub(r'// AI Chatbot Logic.*?</script>', '{% include "chatbot_partial.html" with show_floating_button=False %}\n    </script>', content, flags=re.DOTALL)

# 2. Remove the HTML widget at the bottom
content = re.sub(r'<!-- Floating AI Chat Widget -->.*?</html>', '</html>', content, flags=re.DOTALL)

# 3. Wait, I should keep exactly what's needed for the partial to work.
# The partial contains its own <script> and HTML.
# So I should remove the old HTML and the old JS.

with open('library/templates/base.html', 'w') as f:
    f.write(content)
