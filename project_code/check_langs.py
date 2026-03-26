import django
from django.conf import settings
from django.utils.translation import get_language_info

# Setup minimal settings
if not settings.configured:
    settings.configure(
        LANGUAGES=[
            ('en', 'English'),
            ('hi', 'Hindi'),
            ('ta', 'Tamil'),
            ('te', 'Telugu'),
            ('kn', 'Kannada'),
            ('ml', 'Malayalam'),
            ('mr', 'Marathi'),
            ('bn', 'Bengali'),
            ('gu-in', 'Gujarati (India)'), # Try this
            ('pa', 'Punjabi'),
            ('ne', 'Nepali'),
        ]
    )

from django.conf.locale import LANG_INFO
print(f"Total languages in LANG_INFO: {len(LANG_INFO)}")
print("Checking 'guj':")
if 'guj' in LANG_INFO:
    print(f"OK: guj -> {LANG_INFO['guj']['name']}")
else:
    print("MISSING: guj")
