import requests
import re

session = requests.Session()
response = session.get("https://librarymanagement-main-3tx9.onrender.com/en/library/login/")
csrftoken = session.cookies.get("bookhub_csrf_token") or session.cookies.get("csrftoken")

# 1. Signup a new user
username = "aitestuser_102"
signup_data = {
    "csrfmiddlewaretoken": csrftoken,
    "username": username,
    "email": f"{username}@example.com",
    "password": "Password123!",
    "confirm_password": "Password123!"
}

headers = {"Referer": "https://librarymanagement-main-3tx9.onrender.com/en/library/signup/"}
res = session.post("https://librarymanagement-main-3tx9.onrender.com/en/library/signup/", data=signup_data, headers=headers)
print(f"Signup Status: {res.status_code}")

# 2. Access dashboard
dash_res = session.get("https://librarymanagement-main-3tx9.onrender.com/en/library/dashboard/")
print(f"Dashboard Status: {dash_res.status_code}")

if dash_res.status_code == 500:
    exception_type = re.search(r'<th>Exception Type:</th>\s*<td>([^<]+)</td>', dash_res.text)
    exception_value = re.search(r'<th>Exception Value:</th>\s*<td><pre>([^<]+)</pre></td>', dash_res.text)
    if exception_type:
        print("Exception Type:", exception_type.group(1).strip())
    if exception_value:
        print("Exception Value:", exception_value.group(1).strip())

