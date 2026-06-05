import requests

session = requests.Session()
response = session.get("https://librarymanagement-main-3tx9.onrender.com/en/library/login/")
csrftoken = session.cookies.get("bookhub_csrf_token") or session.cookies.get("csrftoken")

if not csrftoken:
    print("No CSRF token found!")
    for c in session.cookies:
        print(c.name, c.value)

login_data = {
    "csrfmiddlewaretoken": csrftoken,
    "username": "admin",
    "password": "wrongpassword"
}

headers = {
    "Referer": "https://librarymanagement-main-3tx9.onrender.com/en/library/login/"
}

res = session.post("https://librarymanagement-main-3tx9.onrender.com/en/library/login/", data=login_data, headers=headers)
print(f"Status Code: {res.status_code}")

if res.status_code == 500:
    # Print the Exception Type and Value from Django debug page
    import re
    exception_type = re.search(r'<th>Exception Type:</th>\s*<td>([^<]+)</td>', res.text)
    exception_value = re.search(r'<th>Exception Value:</th>\s*<td><pre>([^<]+)</pre></td>', res.text)
    if exception_type:
        print("Exception Type:", exception_type.group(1).strip())
    if exception_value:
        print("Exception Value:", exception_value.group(1).strip())
    # Save the full HTML for manual inspection if needed
    with open("live_500.html", "w") as f:
        f.write(res.text)
else:
    print("No 500 error on login POST!")

