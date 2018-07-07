import requests
from bs4 import BeautifulSoup

class MyGithub:
    def __init__(self, email, psw):
        self.email = email
        self.password = psw
        self.token = None
        self.cookies = None
        self.run()

    def run(self):
        r1 = requests.get(
            url='https://github.com/login',
        )
        soup = BeautifulSoup(r1.text, 'html.parser')
        self.token = soup.find(name='input', attrs={'name': 'authenticity_token'}).get('value')
        self.cookies = r1.cookies.get_dict()
        

    def logon(self):
        '''登录并返回登录信息'''
        r2 = requests.post(
            url='https://github.com/session',
            data={
                'commit': 'Sign in',
                'utf8': '✓',
                'authenticity_token': self.token,
                'login': self.email,
                'password': self.password,
            },
            cookies=self.cookies
        )
        soup2 = BeautifulSoup(r2.text, 'html.parser')
        msg = soup2.find(name='div', id='js-flash-container').text.strip()
        if msg:
            print(msg)
            return False
        else:
            print('login success')
            self.name = soup2.find(name='meta', attrs={'name': "octolytics-actor-login"}).get('content')
            return True

    def print_profile(self):
        '''负责打印用户信息'''
        r3 = requests.get(
            url='https://github.com/%s' % self.name,
            cookies=self.cookies
        )
        soup3 = BeautifulSoup(r3.text, 'html.parser')
        p_name = soup3.find(name='span', attrs={'class': 'p-name'})
        p_nickname = soup3.find(name='span', attrs={'class': 'p-nickname'})
        p_note = soup3.find(name='div', attrs={'class': 'p-note user-profile-bio'})
        h3 = soup3.find(name='h3')
        text_center = soup3.find(name='div', attrs={'class': 'text-center text-gray pt-3'})

        print('%s(%s)' % (p_nickname.text, p_name.text))
        #print(p_note.text)
        print(h3.text.strip())
        #print(text_center.text)


if __name__ == '__main__':
    test = MyGithub('1106233055hui@gmail.com', 'dengni21')  # 填入正确的用户名密码会得到用户信息
    if test.logon():
        test.print_profile()
