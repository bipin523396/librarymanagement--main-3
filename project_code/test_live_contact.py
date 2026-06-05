import requests

session = requests.Session()
response = session.get("https://librarymanagement-main-3tx9.onrender.com/en/library/contact/")
csrftoken = session.cookies.get("bookhub_csrf_token") or session.cookies.get("csrftoken")

if not csrftoken:
    print("No CSRF token found!")

contact_data = {
    "csrfmiddlewaretoken": csrftoken,
    "name": "Admin Tester",
    "email": "tester@example.com",
    "subject": "Test from AI",
    "message": "Testing the 500 error resolution."
}

headers = {
    "Referer": "https://librarymanagement-main-3tx9.onrender.com/en/library/contact/"
}

res = session.post("https://librarymanagement-main-3tx9.onrender.com/en/library/submit-contact/", data=contact_data, headers=headers)
print(f"Status Code: {res.status_code}")

if res.status_code == 500:
    import re
    exception_type = re.search(r'<th>Exception Type:</th>\s*<td>([^<]+)</td>', res.text)
    exception_value = re.search(r'<th>Exception Value:</th>\s*<td><pre>([^<]+)</pre></td>', res.text)
    if exception_type:
        print("Exception Type:", exception_type.group(1).strip())
    if exception_value:
        print("Exception Value:", exception_value.group(1).strip())
else:
    print("No 500 error on contact POST!")

