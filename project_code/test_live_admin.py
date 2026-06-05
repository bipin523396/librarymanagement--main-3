import requests
import re
import time

session = requests.Session()
response = session.get("https://librarymanagement-main-3tx9.onrender.com/en/library/login/")
csrftoken = session.cookies.get("bookhub_csrf_token") or session.cookies.get("csrftoken")

login_data = {
    "csrfmiddlewaretoken": csrftoken,
    "username": "admin",
    "password": "admin123"
}
headers = {"Referer": "https://librarymanagement-main-3tx9.onrender.com/en/library/login/"}

# Wait a bit to ensure Render deployed
time.sleep(30)

res = session.post("https://librarymanagement-main-3tx9.onrender.com/en/library/login/", data=login_data, headers=headers)
print(f"Login Status: {res.status_code}")

dash_res = session.get("https://librarymanagement-main-3tx9.onrender.com/en/library/admin-dashboard/")
print(f"Admin Dashboard Status: {dash_res.status_code}")

if dash_res.status_code == 500:
    exception_type = re.search(r'<th>Exception Type:</th>\s*<td>([^<]+)</td>', dash_res.text)
    exception_value = re.search(r'<th>Exception Value:</th>\s*<td><pre>([^<]+)</pre></td>', dash_res.text)
    if exception_type:
        print("Exception Type:", exception_type.group(1).strip())
    if exception_value:
        print("Exception Value:", exception_value.group(1).strip())
else:
    print("No 500 error on admin dashboard! Wait, what?")

