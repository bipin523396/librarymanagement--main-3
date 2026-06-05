import requests

session = requests.Session()
response = session.get("https://librarymanagement-main-3tx9.onrender.com/en/library/signup/")
csrftoken = session.cookies.get("bookhub_csrf_token") or session.cookies.get("csrftoken")

signup_data = {
    "csrfmiddlewaretoken": csrftoken,
    "username": "aitestuser99",
    "email": "aitestuser99@example.com",
    "password": "Password123!",
    "confirm_password": "Password123!"
}

headers = {
    "Referer": "https://librarymanagement-main-3tx9.onrender.com/en/library/signup/"
}

res = session.post("https://librarymanagement-main-3tx9.onrender.com/en/library/signup/", data=signup_data, headers=headers)
print(f"Signup POST Status Code: {res.status_code}")

if res.status_code == 500:
    import re
    exception_type = re.search(r'<th>Exception Type:</th>\s*<td>([^<]+)</td>', res.text)
    exception_value = re.search(r'<th>Exception Value:</th>\s*<td><pre>([^<]+)</pre></td>', res.text)
    if exception_type:
        print("Exception Type:", exception_type.group(1).strip())
    if exception_value:
        print("Exception Value:", exception_value.group(1).strip())
    with open("signup_500.html", "w") as f:
        f.write(res.text)
else:
    # Now try to access the dashboard
    dash_res = session.get("https://librarymanagement-main-3tx9.onrender.com/en/library/dashboard/")
    print(f"Dashboard GET Status Code: {dash_res.status_code}")
    if dash_res.status_code == 500:
        import re
        exception_type = re.search(r'<th>Exception Type:</th>\s*<td>([^<]+)</td>', dash_res.text)
        exception_value = re.search(r'<th>Exception Value:</th>\s*<td><pre>([^<]+)</pre></td>', dash_res.text)
        if exception_type:
            print("Exception Type:", exception_type.group(1).strip())
        if exception_value:
            print("Exception Value:", exception_value.group(1).strip())
        with open("dashboard_500.html", "w") as f:
            f.write(dash_res.text)
