import requests
from bs4 import BeautifulSoup

ret = requests.get(url = "https://www.autohome.com.cn/news/")
ret.encoding = ret.apparent_encoding

soup = BeautifulSoup(ret.text, "html.parser")

div = soup.find(name = 'div', id = "auto-channel-lazyload-article")
li_list = div.find_all(name = 'li')
for li in li_list:
    h3 = li.find(name = 'h3')
    if not h3:
        continue

    p = li.find(name = "p")
    a = li.find(name = "img")
    src = a.get("src")

    file_name = src.rsplit('__', maxsplit=1)[1]
    ret_img = requests.get(
        url = "https:" + src
    )
    with open(file_name,"wb") as f:
        f.write(ret_img.content)



    print(h3.text, a.get('href'))
    print(p.text)
    print("===="*23)




