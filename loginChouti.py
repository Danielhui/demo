import requests

response_login = requests.post(
    url = 'https://dig.chouti.com/login',
    headers = {
        'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36"
    },
    data = {
        "phone": "8615626926915",
        "password": "134679abc",
        "oneMonth": "1",
    }
)
cookie_dict = response_login.cookies.get_dict()

r1 = requests.post(
    url = 'https://dig.chouti.com/link/vote?linksId=20324196',
    headers = {
        'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36"
    },
    cookies = cookie_dict
)
