import requests
from bs4 import BeautifulSoup

respose_1 = requests.get(
    url = 'https://github.com/login',
)
bs_1 = BeautifulSoup(respose_1.text, 'html.parser')
token = bs_1.find(name="input",attrs={'name':"authenticity_token"}).get('value')
cookie1 = respose_1.cookies.get_dict()

response_login = requests.post(
    url = 'https://github.com/session',
    headers = {
        'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36"
    },
    data = {
        "commit": "Sign in",
        "utf8": "✓",
        "authenticity_token": token,
        "login": "xxx",
        "password":" xxx",
    },
    cookies = cookie1
)
cookie2= response_login.cookies.get_dict()

respose_2 = requests.get(
    url = 'https://github.com/Danielhui',
    cookies = cookie2,
)

bs_2 = BeautifulSoup(respose_2.text, "html.parser")
userName = bs_2.find(name = 'span', attrs= {"class":"p-name vcard-fullname d-block overflow-hidden"}).get_text()
img_1 = bs_2.find(name="img", attrs={"class":"avatar width-full rounded-2"}).get("src")
file_name = userName + ".jpg"
print(1111)
ret_img = requests.get(
    url = img_1
)
with open(file_name,"wb") as f:
    f.write(ret_img.content)
print("My name is :"+ userName)
