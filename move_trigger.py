import re

with open('library/templates/base.html', 'r') as f:
    html = f.read()

# 1. Extract the button code from the floating widget
button_pattern = re.compile(r'(<!-- Floating Toggle Button -->\s*<button id="chatbotToggleBtn".*?</button>)', re.DOTALL)
match = button_pattern.search(html)
if not match:
    print("Button not found in floating widget")
    exit(1)

btn_code = match.group(1)

# Clean up button code for nav (remove some large classes if needed, but let's keep it mostly same)
# Actually, the user wants it "beside login now option"
# In the nav, it was a smaller button before.

# 2. Remove it from the bottom-right container
html = button_pattern.sub('', html)

# 3. Insert it into the nav bar after "Join Now"
nav_insert_point = re.compile(r'(</a>\s*</div>\s*</div>\s*</nav>)', re.DOTALL)
# Find the specific div for login/signup
nav_group_pattern = re.compile(r'(<div class="flex items-center space-x-4">.*?</a>)', re.DOTALL)
nav_match = nav_group_pattern.search(html)

if nav_match:
    # Append button inside the flex container
    new_nav_content = nav_match.group(1) + '\n                ' + btn_code
    html = html.replace(nav_match.group(1), new_nav_content)

# 4. Modify classes of the button to fit better in nav if necessary
# Original floating button had w-14 h-14, let's make it slightly smaller for nav like before w-10 h-10
html = html.replace('w-14 h-14 sm:w-16 sm:h-16', 'w-10 h-10')
# Remove 'shadow-2xl' and 'fixed' if it had it (it didn't have fixed on button itself, but in container)
# The container was 'fixed bottom-6 right-6'.
# The popover itself also had 'fixed bottom-6 right-6' in its container.

# Need to ensure the popover stays fixed bottom right even if trigger is in nav
popover_container_pattern = re.compile(r'<div class="fixed bottom-6 right-6 z-\[9999\] flex flex-col items-end">', re.DOTALL)
# Remove the flex flex-col items-end part for the popover if the button is gone from there
html = html.replace('<div class="fixed bottom-6 right-6 z-[9999] flex flex-col items-end">', '<div id="aiChatWindowContainer" class="fixed bottom-6 right-6 z-[9999]">')

with open('library/templates/base.html', 'w') as f:
    f.write(html)
