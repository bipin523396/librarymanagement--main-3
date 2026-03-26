import re

with open('library/templates/base.html', 'r') as f:
    content = f.read()

# Update drag header selector
old_selector = "const chatHeader = chatPopover.querySelector('.bg-white.px-5.py-4');"
new_selector = "const chatHeader = chatPopover.querySelector('.from-orange-600.to-orange-500');"
content = content.replace(old_selector, new_selector)

with open('library/templates/base.html', 'w') as f:
    f.write(content)
