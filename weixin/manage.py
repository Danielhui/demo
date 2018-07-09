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
    print(123123124)
    user_list_url = "https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxgetcontact?lang=zh_CN&r={0}&seq=0&skey={1}".format(ctime,skey)
    # print(user_list_url)
    # ua_headers = {
    # "Host": "wx.qq.com",
    # "Pragma": "no-cache",
    # "Referer": "https://wx.qq.com/?&lang=zh_CN",
    # "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    # }


    r1 = requests.get(user_list_url, cookies = ticket_cookie)
    r1.encoding = "utf-8"
    wx_user_list = r1.json()
    # for item in wx_user_list:
    #     print(item)


    #return (wx_user_dict.MemberCount, wx_user_list.MemberList)
    return render_template("user_list.html",wx_user_dict=wx_user_list)

@app.route('/send', methods = ['GET','POST'])
def send():
    if request.method == "GET":
        return render_template('send.html')
    current_user = session['current_user']
    ticket_dict = session.get('ticket_dict')


    from_user = current_user['UserName']
    to = request.form.get('to')
    content = request.form.get('content')
    ctime = str(int(time.time() * 1000))


    msg_url = "https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsendmsg"
    data_dict = {
        "BaseRequest":{
            "DeviceID":"e586351620227078",
            "Sid":ticket_dict.get('wxsid'),
            "Uin":ticket_dict.get('wxuin'), 
            "Skey":ticket_dict.get('skey'),
        },
        "Msg":{
            "ClientMsgId":ctime,
            "Content":content,
            "FromUserName":from_user,
            "LocalID":ctime,
            "ToUserName":to,
            "Type":1,
            
        }
    }
    ticket_cookie = session.get('ticket_cookie')

    ret = requests.post(
        url = msg_url,
        data = bytes(json.dumps(data_dict,ensure_ascii=False),encoding = "utf-8"),
        cookies = ticket_cookie
    )

    return ret.text

def get_msg(request):
    ticket_cookie = session.get('ticket_cookie')
    ticket_dict = session.get('ticket_dict')

    sync_url="https://webpush.wx.qq.com/cgi-bin/mmwebwx-bin/synccheck"
    sync_data_list = []
    for item in USER_INIT_DATA['SyncKey']['List']:
        temp = "%s_%s" %(item['Key'],item['Val'])
        sync_data_list.append(temp)
    sync_data_list = "|".join(sync_data_list)
    nid = int(time.time())
    sync_dict = {
        "r":nid,
        "skey":ticket_dict['skey'],
        "sid":ticket_dict["wxsid"],
        "uin":ticket_dict["wxuin"],
        "deviced":"e586351620227078",
        "synckey":sync_data_list
    }
    # all_cookie = {}
    # all_cookie.update(LOGIN_COOKIE_DICT)
    # all_cookie.update(TICKET_COOKIE_DICT)
    ticket_cookie = session.get('ticket_cookie')
    response_sync = requests.get(sync_url, params=sync_dict, cookies=ticket_cookie)
    print(response_sync.text)
    if 'selector:"2"' in response_sync.text:
        fetch_msg_url = "https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsync?sid=%s&skey=%s&pass_ticket=%s"%(ticket_dict['wsid'],ticket_dict['skey'],ticket_dict['pass_ticket'])
        form_data = {

        }
        response_fetch_msg = requests.post(fetch_msg_url,json=form_data)
        response_fetch_msg.encoding = 'utf-8'
        res_fetch_msg_dict = json.loads(response_fetch_msg.text)
        USER_INIT_DATA['SyncKey'] = res_fetch_msg_dict['Synckey']
        for item in res_fetch_msg_dict['AddMsgList']:
            print(item['Content'],"::::",item['FromUserName'],"to",item['ToUserName'])
    return "ok"





if __name__ == '__main__':
    app.run()