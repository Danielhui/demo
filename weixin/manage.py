from flask import Flask,request,render_template,session,jsonify
import time
import requests
import re
from bs4 import BeautifulSoup
import json

app = Flask(__name__)
app.debug = True
app.secret_key = 'asdf3sdfsdf'



def xml_parser(text):
    dic = {}
    soup = BeautifulSoup(text,'html.parser')
    div = soup.find(name='error')
    for item in div.find_all(recursive=False):
        dic[item.name] = item.text
    return dic

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        ctime = str(int(time.time() * 1000))
        qcode_url = "https://login.wx.qq.com/jslogin?appid=wx782c26e4c19acffb&redirect_uri=https%3A%2F%2Fwx.qq.com%2Fcgi-bin%2Fmmwebwx-bin%2Fwebwxnewloginpage&fun=new&lang=zh_CN&_={0}".format(ctime)

        ret = requests.get(qcode_url)
        qcode = re.findall('uuid = "(.*)";',ret.text)[0]
        session['qcode'] = qcode
        return render_template('login.html',qcode=qcode)
    else:
        pass
@app.route('/check_login')
def check_login():
    """
    发送GET请求检测是否已经扫码、登录
    https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid=QbeUOBatKw==&tip=0&r=-1036255891&_=1525749595604
    :return:
    """
    response = {'code':408}
    qcode = session.get('qcode')
    ctime = str(int(time.time() * 1000))
    check_url = "https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid={0}&tip=0&r=-1036255891&_={1}".format(qcode,ctime)
    ret = requests.get(check_url)
    if "code=201" in ret.text:
        # 扫码成功
        src = re.findall("userAvatar = '(.*)';",ret.text)[0]
        response['code'] = 201
        response['src'] = src
    elif 'code=200' in ret.text:
        # 确认登录
        redirect_uri = re.findall('redirect_uri="(.*)";',ret.text)[0]

        # 向redirect_uri地址发送请求，获取凭证相关信息
        redirect_uri = redirect_uri + "&fun=new&version=v2"
        ticket_ret = requests.get(redirect_uri)
        ticket_dict = xml_parser(ticket_ret.text)
        session['ticket_dict'] = ticket_dict
        session['ticket_cookie'] = ticket_ret.cookies.get_dict()
        response['code'] = 200
    return jsonify(response)

@app.route('/index')
def index():
    """
    用户数据的初始化
    https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxinit?r=-1039465096&lang=zh_CN&pass_ticket=q9TOX4RI4VmNiHXW9dUUl1oMzoQK2X2f3H3kn0VYm5YGNwUMO2THYMznv8DSXqp0

    :return:
    """
    ticket_dict = session.get('ticket_dict')
    init_url = "https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxinit?r=-1039465096&lang=zh_CN&pass_ticket={0}".format(ticket_dict.get('pass_ticket'))

    data_dict = {
        "BaseRequest":{
            "DeviceID":"e586351620227078",
            "Sid":ticket_dict.get('wxsid'),
            "Uin":ticket_dict.get('wxuin'), 
            "Skey":ticket_dict.get('skey'),
        }
    }

    init_ret = requests.post(
        url=init_url,
        json=data_dict
    )
    init_ret.encoding = 'utf-8'
    user_dict = init_ret.json()
    print(user_dict)
    session['current_user'] = user_dict['User']
    # for user in user_dict['ContactList']:
    #     print(user.get('NickName'))
    return render_template('index.html',user_dict=user_dict, )

@app.route('/get_img')
def get_img():
    #获取头像
    current_user = session['current_user']
    ticket_cookie = session.get('ticket_cookie')
    head_url = "https://wx.qq.com" + current_user['HeadImgUrl']
    img_ret = requests.get(head_url,cookies=ticket_cookie,headers={"Content-Type":"image/jpeg"})

    return img_ret.content

@app.route('/user_list')
def user_list():
    ticket_dict = session.get('ticket_dict')
    ticket_cookie = session.get('ticket_cookie')
    
    ctime = str(int(time.time() * 1000))
    skey = ticket_dict.get('skey')
    user_list_url = "https://webpush.wx.qq.com/cgi-bin/mmwebwx-bin/synccheck?r={0}&skey={1}".format(ctime,skey)
    print(user_list_url)

    r1 = requests.get(user_list_url, ticket_cookie)
    r1.encoding = "utf-8"
    wx_user_list = r1.json()
    for item in wx_user_list:
        print(item)

    return (wx_user_dict.MemberCount, wx_user_list.MemberList)

@app.route('/send', methods = ['GET','POST'])
def send():
    if request.method == "GET":
        return render_template('send.html')
    current_user = session['current_user']

    from_user = current_user['UserName']
    to = requests.form.get('to')
    content = requests.form.get('content')

    msg_url = "从url中取，拼接字符串"
    data_dict = {
        "BaseRequest":{
            "DeviceID":"e586351620227078",
            "Sid":ticket_dict.get('wxsid'),
            "Uin":ticket_dict.get('wxuin'), 
            "Skey":ticket_dict.get('skey'),
        },
        "Msg":{
            
        }
    }


if __name__ == '__main__':
    app.run()