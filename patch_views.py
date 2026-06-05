import re

with open('project_code/library/views.py', 'r') as f:
    content = f.read()

images = [
    "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=400&q=80",
    "https://images.unsplash.com/photo-1589998059171-988d887df646?auto=format&fit=crop&w=400&q=80",
    "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=400&q=80",
    "https://images.unsplash.com/photo-1495640388908-05fa85288e61?auto=format&fit=crop&w=400&q=80",
    "https://images.unsplash.com/photo-1535905557558-afc4877a26fc?auto=format&fit=crop&w=400&q=80",
    "https://images.unsplash.com/photo-1476275466078-4007374efac4?auto=format&fit=crop&w=400&q=80",
    "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?auto=format&fit=crop&w=400&q=80",
    "https://images.unsplash.com/photo-1511108690759-009324a5033d?auto=format&fit=crop&w=400&q=80",
    "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?auto=format&fit=crop&w=400&q=80",
    "https://images.unsplash.com/photo-1517770413964-df8ca61194a6?auto=format&fit=crop&w=400&q=80"
]

# Add images to BOOKS_DATA
for i in range(10):
    find_str = f'", "status": "Available"}}'
    replace_str = f'", "status": "Available", "image": "{images[i]}"}}'
    content = content.replace(find_str, replace_str, 1)

    find_str2 = f'", "status": "Low Stock"}}'
    replace_str2 = f'", "status": "Low Stock", "image": "{images[i]}"}}'
    content = content.replace(find_str2, replace_str2, 1)

# Update insert
content = content.replace("'image': '',", "'image': data.get('image', ''),")

with open('project_code/library/views.py', 'w') as f:
    f.write(content)

