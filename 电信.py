import os
import re
import sys
import ssl
import time
import json
import base64
import random
import certifi
import aiohttp
import asyncio
import certifi
import datetime
import requests
import binascii
import urllib3
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.ssl_ import create_urllib3_context
from lxml import etree
from http import cookiejar
from Crypto.Cipher import AES
from Crypto.Cipher import DES3
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Util.Padding import pad, unpad
from aiohttp import ClientSession, TCPConnector
from concurrent.futures import ThreadPoolExecutor

import subprocess  # windows下 subprocess 要在execjs 前设置enconding= "utf-8",否者瑞数加密.js文件读取会出错
from functools import partial

subprocess.Popen = partial(subprocess.Popen, encoding="utf-8")
import execjs

# 总计运行时间run_num * diffValue
# 并发，1秒2条请求，总计4秒
run_num = os.environ.get('reqNUM') or "40"
# 并发间隔
diffValue = 1
'''
变量: 手机号@服务密码
多个变量&隔开
corn 58 9,13,23 * * *
'''
MAX_RETRIES = 3
RATE_LIMIT = 10  # 每秒请求数限制
ORIGIN_CIPHERS = ('DEFAULT@SECLEVEL=1')
log_data = {}
_js_code = """
delete __filename
delete __dirname
ActiveXObject = undefined

window = global;


content="content_code"


navigator = {"platform": "Linux aarch64"}
navigator = {"userAgent": "CtClient;11.0.0;Android;13;22081212C;NTIyMTcw!#!MTUzNzY"}

location={
    "href": "https://",
    "origin": "",
    "protocol": "",
    "host": "",
    "hostname": "",
    "port": "",
    "pathname": "",
    "search": "",
    "hash": ""
}

i = {length: 0}
base = {length: 0}
div = {
    getElementsByTagName: function (res) {
        console.log('div中的getElementsByTagName：', res)
        if (res === 'i') {
            return i
        }
    return '<div></div>'

    }
}

script = {

}
meta = [
    {charset:"UTF-8"},
    {
        content: content,
        getAttribute: function (res) {
            console.log('meta中的getAttribute：', res)
            if (res === 'r') {
                return 'm'
            }
        },
        parentNode: {
            removeChild: function (res) {
                console.log('meta中的removeChild：', res)

              return content
            }
        },

    }
]
form = '<form></form>'


window.addEventListener= function (res) {
        console.log('window中的addEventListener:', res)

    }


document = {


    createElement: function (res) {
        console.log('document中的createElement：', res)


       if (res === 'div') {
            return div
        } else if (res === 'form') {
            return form
        }
        else{return res}




    },
    addEventListener: function (res) {
        console.log('document中的addEventListener:', res)

    },
    appendChild: function (res) {
        console.log('document中的appendChild：', res)
        return res
    },
    removeChild: function (res) {
        console.log('document中的removeChild：', res)
    },
    getElementsByTagName: function (res) {
        console.log('document中的getElementsByTagName：', res)
        if (res === 'script') {
            return script
        }
        if (res === 'meta') {
            return meta
        }
        if (res === 'base') {
            return base
        }
    },
    getElementById: function (res) {
        console.log('document中的getElementById：', res)
        if (res === 'root-hammerhead-shadow-ui') {
            return null
        }
    }

}

setInterval = function () {}
setTimeout = function () {}
window.top = window


'ts_code'



function main() {
    cookie = document.cookie.split(';')[0]
    return cookie
}
"""


class RateLimiter:
    def __init__(self, rate_limit):
        self.rate_limit = rate_limit
        self.tokens = rate_limit
        self.updated_at = time.monotonic()

    async def acquire(self):
        while self.tokens < 1:
            self.add_new_tokens()
            await asyncio.sleep(0.1)
        self.tokens -= 1

    def add_new_tokens(self):
        now = time.monotonic()
        time_since_update = now - self.updated_at
        new_tokens = time_since_update * self.rate_limit
        if new_tokens > 1:
            self.tokens = min(self.tokens + new_tokens, self.rate_limit)
            self.updated_at = now


class AsyncSessionManager:
    def __init__(self):
        self.session = None
        self.connector = None

    async def __aenter__(self):
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.set_ciphers('DEFAULT@SECLEVEL=0')
        self.connector = TCPConnector(ssl=ssl_context, limit=1000)
        self.session = ClientSession(connector=self.connector)
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
        await self.connector.close()


async def retry_request(session, method, url, **kwargs):
    for attempt in range(MAX_RETRIES):
        try:
            await asyncio.sleep(1)
            async with session.request(method, url, **kwargs) as response:
                return await response.json()
                # return await response.json()

        except (aiohttp.ClientConnectionError, aiohttp.ServerTimeoutError) as e:
            print(f"请求失败，第 {attempt + 1} 次重试: {e}")
            if attempt == MAX_RETRIES - 1:
                raise
            await asyncio.sleep(2 ** attempt)


class BlockAll(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False


def printn(m):
    print(f'\n{m}')


class DESAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        """
        A TransportAdapter that re-enables 3DES support in Requests.
        """
        CIPHERS = ORIGIN_CIPHERS.split(':')
        random.shuffle(CIPHERS)
        CIPHERS = ':'.join(CIPHERS)
        self.CIPHERS = CIPHERS + ':!aNULL:!eNULL:!MD5'
        super().__init__(*args, **kwargs)

    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context(ciphers=self.CIPHERS)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        kwargs['ssl_context'] = context
        return super(DESAdapter, self).init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        context = create_urllib3_context(ciphers=self.CIPHERS)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        kwargs['ssl_context'] = context
        return super(DESAdapter, self).proxy_manager_for(*args, **kwargs)


requests.packages.urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
context = ssl.create_default_context()
context.set_ciphers('DEFAULT@SECLEVEL=0')  # 低安全级别0/1
context.check_hostname = False  # 禁用主机
context.verify_mode = ssl.CERT_NONE  # 禁用证书

runTime = 0
key = b'1234567`90koiuyhgtfrdews'
iv = 8 * b'\0'

public_key_b64 = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBkLT15ThVgz6/NOl6s8GNPofdWzWbCkWnkaAm7O2LjkM1H7dMvzkiqdxU02jamGRHLX/ZNMCXHnPcW/sDhiFCBN18qFvy8g6VYb9QtroI09e176s+ZCtiv7hbin2cCTj99iUpnEloZm19lwHyo69u5UMiPMpq0/XKBO8lYhN/gwIDAQAB
-----END PUBLIC KEY-----'''

public_key_data = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC+ugG5A8cZ3FqUKDwM57GM4io6JGcStivT8UdGt67PEOihLZTw3P7371+N47PrmsCpnTRzbTgcupKtUv8ImZalYk65dU8rjC/ridwhw9ffW2LBwvkEnDkkKKRi2liWIItDftJVBiWOh17o6gfbPoNrWORcAdcbpk2L+udld5kZNwIDAQAB
-----END PUBLIC KEY-----'''


# 获取数字前三位获取手机号码前三位
def get_first_three(value):
    # 处理数字情况
    if isinstance(value, (int, float)):
        return int(str(value)[:3])
    elif isinstance(value, str):
        return str(value)[:3]
    else:
        raise TypeError("error")


# 转换时间秒
def run_Time(hour, miute, second):
    date = datetime.datetime.now()
    date_zero = datetime.datetime.now().replace(year=date.year, month=date.month, day=date.day, hour=hour, minute=miute,
                                                second=second)
    date_zero_time = int(time.mktime(date_zero.timetuple()))
    return date_zero_time


# DES加密text
def encrypt(text):
    cipher = DES3.new(key, DES3.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(text.encode(), DES3.block_size))
    return ciphertext.hex()


# DES解密text
def decrypt(text):
    ciphertext = bytes.fromhex(text)
    cipher = DES3.new(key, DES3.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), DES3.block_size)
    return plaintext.decode()


def b64(plaintext):
    public_key = RSA.import_key(public_key_b64)
    cipher = PKCS1_v1_5.new(public_key)
    ciphertext = cipher.encrypt(plaintext.encode())
    return base64.b64encode(ciphertext).decode()


def encrypt_para(plaintext):
    if not isinstance(plaintext, str):
        plaintext = json.dumps(plaintext)
    public_key = RSA.import_key(public_key_data)
    cipher = PKCS1_v1_5.new(public_key)
    ciphertext = cipher.encrypt(plaintext.encode())
    return binascii.hexlify(ciphertext).decode()


def encode_phone(text):
    encoded_chars = []
    for char in text:
        encoded_chars.append(chr(ord(char) + 2))
    return ''.join(encoded_chars)


def getApiTime(api_url):
    try:
        with requests.get(api_url) as response:
            if (not response or not response.text):
                return time.time()
            json_data = json.loads(response.text)
            if (json_data.get("api") and json_data.get("api") not in ("time")):
                timestamp_str = json_data.get('data', {}).get('t', '')
            else:
                timestamp_str = json_data.get('currentTime', {})
            timestamp = int(timestamp_str) / 1000.0  # 将毫秒转为秒
            difftime = time.time() - timestamp
            return difftime;
    except Exception as e:
        print(f"获取时间失败: {e}")
        return 0;


def userLoginNormal(phone, password, ss):
    alphabet = 'abcdef0123456789'
    uuid = [''.join(random.sample(alphabet, 8)), ''.join(random.sample(alphabet, 4)),
            '4' + ''.join(random.sample(alphabet, 3)), ''.join(random.sample(alphabet, 4)),
            ''.join(random.sample(alphabet, 12))]
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    loginAuthCipherAsymmertric = 'iPhone 14 15.4.' + uuid[0] + uuid[1] + phone + timestamp + password[:6] + '0$$$0.'
    r = ss.post('https://appgologin.189.cn:9031/login/client/userLoginNormal', json={
        "headerInfos": {"code": "userLoginNormal", "timestamp": timestamp, "broadAccount": "", "broadToken": "",
                        "clientType": "#9.6.1#channel50#iPhone 14 Pro Max#", "shopId": "20002", "source": "110003",
                        "sourcePassword": "Sid98s", "token": "", "userLoginName": phone}, "content": {"attach": "test",
                                                                                                      "fieldData": {
                                                                                                          "loginType": "4",
                                                                                                          "accountType": "",
                                                                                                          "loginAuthCipherAsymmertric": b64(
                                                                                                              loginAuthCipherAsymmertric),
                                                                                                          "deviceUid":
                                                                                                              uuid[0] +
                                                                                                              uuid[1] +
                                                                                                              uuid[2],
                                                                                                          "phoneNum": encode_phone(
                                                                                                              phone),
                                                                                                          "isChinatelecom": "0",
                                                                                                          "systemVersion": "15.4.0",
                                                                                                          "authentication": password}}},
                verify=certifi.where()).json()
    # r = await retry_request(ss,"POST",'https://appgologin.189.cn:9031/login/client/userLoginNormal',json={"headerInfos": {"code": "userLoginNormal", "timestamp": timestamp, "broadAccount": "", "broadToken": "", "clientType": "#9.6.1#channel50#iPhone 14 Pro Max#", "shopId": "20002", "source": "110003", "sourcePassword": "Sid98s", "token": "", "userLoginName": phone}, "content": {"attach": "test", "fieldData": {"loginType": "4", "accountType": "", "loginAuthCipherAsymmertric": b64(loginAuthCipherAsymmertric), "deviceUid": uuid[0] + uuid[1] + uuid[2], "phoneNum": encode_phone(phone), "isChinatelecom": "0", "systemVersion": "15.4.0", "authentication": password}}},verify=certifi.where())
    l = r['responseData']['data']['loginSuccessResult']
    if l:
        load_token[phone] = l
        with open(load_token_file, 'w') as f:
            json.dump(load_token, f)
        ticket = get_ticket(phone, l['userId'], l['token'], ss)
        return ticket
    return False


async def exchangeForDay(phone, session, run_Time, rid, stime):
    async def delayed_conversion(delay):
        await asyncio.sleep(delay)
        await conversionRights(phone, rid, session)

    tasks = [asyncio.create_task(delayed_conversion(i * stime)) for i in range(int(run_Time))]
    await asyncio.gather(*tasks)


def get_ticket(phone, userId, token, ss):
    r = ss.post('https://appgologin.189.cn:9031/map/clientXML',
                data='<Request><HeaderInfos><Code>getSingle</Code><Timestamp>' + datetime.datetime.now().strftime(
                    "%Y%m%d%H%M%S") + '</Timestamp><BroadAccount></BroadAccount><BroadToken></BroadToken><ClientType>#9.6.1#channel50#iPhone 14 Pro Max#</ClientType><ShopId>20002</ShopId><Source>110003</Source><SourcePassword>Sid98s</SourcePassword><Token>' + token + '</Token><UserLoginName>' + phone + '</UserLoginName></HeaderInfos><Content><Attach>test</Attach><FieldData><TargetId>' + encrypt(
                    userId) + '</TargetId><Url>4a6862274835b451</Url></FieldData></Content></Request>',
                headers={'user-agent': 'CtClient;10.4.1;Android;13;22081212C;NTQzNzgx!#!MTgwNTg1'},
                verify=certifi.where())
    tk = re.findall('<Ticket>(.*?)</Ticket>', r.text)
    if len(tk) == 0:
        return False
    return decrypt(tk[0])


# async def check(s,item,ckvalue):
#     checkGoods = s.get('https://wapact.189.cn:9001/gateway/standQuery/detailNew/check?activityId=' + item, cookies=ckvalue).json()
#     return checkGoods

async def conversionRights(phone, aid, session):
    global js, rs, ck, log_data
    if rs:
        bd = js.call("main").split("=")
        ck[bd[0]] = bd[1]
    value = {
        "phone": phone,
        "rightsId": aid
    }
    paraV = encrypt_para(value)
    response = session.post('https://wapside.189.cn:9001/jt-sign/paradise/conversionRights', json={"para": paraV},
                            cookies=ck)
    login = response.json()
    printn(f"{get_first_three(phone)},{str(datetime.datetime.now())[11:23]}:{login} ")
    try:
        if login['resoultCode'] == '0' or login["resoultMsg"][:5] == "权益已兑换":
            day = datetime.datetime.now().strftime("%Y%m")
            with open(f"{day}.log", "w", encoding='utf-8') as f:
                log_data[f"{phone}"] = "5元权益到账"
                json.dump(log_data, f)
                f.close()
    except:
        pass


async def getLevelRightsList(phone, session):
    global js, rs, ck
    if rs:
        bd = js.call("main").split("=")
        ck[bd[0]] = bd[1]
    value = {
        "phone": phone
    }
    paraV = encrypt_para(value)
    data = session.post('https://wapside.189.cn:9001/jt-sign/paradise/getLevelRightsList', json={"para": paraV},
                        cookies=ck).json()
    if data.get('code') == 401:
        print(f"获取失败:{data},原因大概是sign过期了")
        return None
    current_level = int(data['currentLevel'])
    key_name = 'V' + str(current_level)
    ids = [item['id'] for item in data.get(key_name, []) if item.get('name') == '话费']
    return ids


async def getSign(ticket, session):
    global js, ck, rs
    try:
        if rs:
            bd = js.call('main').split('=')
            ck[bd[0]] = bd[1]
        response_data = session.get('https://wapside.189.cn:9001/jt-sign/ssoHomLogin?ticket=' + ticket, cookies=ck)

        response_data = response_data.json()['sign']
        print(response_data)
        return response_data
    except Exception as e:
        print(e)


ck = {}
rs = 0
js = None


async def first_request(ss, res=''):
    global js, fw, ck, rs
    url = 'https://wapact.189.cn:9001/gateway/standExchange/detailNew/exchange'
    if res == '':
        response = ss.get(url)
        res = response.text
    soup = BeautifulSoup(res, 'html.parser')
    scripts = soup.find_all('script')
    for script in scripts:
        if 'src' in str(script):
            rsurl = re.findall('src="([^"]+)"', str(script))[0]
        if '$_ts=window' in script.get_text():
            ts_code = script.get_text()
            rs = 1
    urls = url.split('/')
    rsurl = urls[0] + '//' + urls[2] + rsurl
    # print(rsurl)
    ts_code += ss.get(rsurl).text
    content_code = soup.find_all('meta')[1].get('content')
    try:
        with open("瑞数通杀.js", "r", encoding='utf-8') as f:
            js_code_ym = f.read()
            rs = 1
    except:
        js_code_ym = _js_code
        rs = 1
    js_code = js_code_ym.replace('content_code', content_code).replace("'ts_code'", ts_code)
    js = execjs.compile(js_code)
    for cookie in ss.cookies:
        ck[cookie.name] = cookie.value
    print(ck)
    return content_code, ts_code, ck


async def qgNight(phone, ticket, timeValue, isTrue, ss):
    if isTrue:
        runTime = run_Time(23, 59, 8) + 0.65
    else:
        runTime = run_Time(0, 0, 0) + 0.65
    if runTime > (time.time() + timeValue):
        difftime = runTime - time.time() - timeValue
        printn(f"当前时间:{str(datetime.datetime.now())[11:23]},跟设定的时间不同,等待{difftime}秒开始兑换每天一次的")
        await asyncio.sleep(difftime)

    session = ss
    session.headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36",
        "Referer": "https://wapact.189.cn:9001/JinDouMall/JinDouMall_independentDetails.html"}
    # session.mount('https://', DESAdapter())
    # session.verify = False  # 禁用证书验证
    # session.ssl = context
    # session.set_policy(BlockAll)

    if rs:
        bd = js.call('main').split('=')
        ck[bd[0]] = bd[1]
    else:
        await first_request(session)

    sign = await getSign(ticket, session)
    if sign:
        print(f"当前时间:{str(datetime.datetime.now())[11:23]}获取到了Sign:" + sign)
        session.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36",
            "sign": sign}
    else:
        print("未能获取sign。")
        return
    # await asyncio.sleep(10)直接延迟也行，或者用下面的等待一段时间。之所以这样是要先获取sign省一些步骤。
    if isTrue:
        runTime2 = run_Time(23, 59, 40) + 0.65
    else:
        runTime2 = run_Time(0, 0, 0) + 0.65
    if runTime2 > (time.time() + timeValue):
        difftime = runTime2 - time.time() - timeValue
        printn(f"获得到sign等待下")
        await asyncio.sleep(difftime)
    rightsId = await getLevelRightsList(phone, session)
    if rightsId:
        print("获取到了rightsId:" + rightsId[0])
    else:
        print("未能获取rightsId。")
        return
    printn(f"{str(datetime.datetime.now())[11:23]} 时间到开始兑换每天一次的")
    await exchangeForDay(phone, session, 5, rightsId[0], 4.625)


def isChecked(phone):
    global log_data
    try:
        day = datetime.datetime.now().strftime("%Y%m")
        with open(f'{day}.log', 'r', encoding='utf-8') as f:
            log_data = json.load(f)
            for dkey, dval in log_data.items():
                if dkey == phone:
                    return True
    except:
        pass
    return False


cfcs = 10
yc = 0.1
wt = 0
kswt = 0.6  # 提前1秒运行，根据时间59分59秒做偏差
jdaid = '60dd79533dc03d3c76bdde30'
yf = datetime.datetime.now().strftime("%Y%m")
jp = {"9": {}, "12": {}, "13": {}, "23": {}}
try:
    with open('电信金豆换话费1.log') as fr:
        dhjl = json.load(fr)
except:
    dhjl = {}
if yf not in dhjl:
    dhjl[yf] = {}
wxp = {}
errcode = {
    "0": "兑换成功",
    "412": "兑换次数已达上限",
    "413": "商品已兑完",
    "420": "未知错误",
    "410": "该活动已失效~",
    "Y0001": "当前等级不足，去升级兑当前话费",
    "Y0002": "使用翼相连网络600分钟或连接并拓展网络500分钟可兑换此奖品",
    "Y0003": "使用翼相连共享流量400M或共享WIFI：2GB可兑换此奖品",
    "Y0004": "使用翼相连共享流量2GB可兑换此奖品",
    "Y0005": "当前等级不足，去升级兑当前话费",
    "E0001": "您的网龄不足10年，暂不能兑换"
}


# 手机号，session,运行次数，延时间隔（延时时间=延时间隔*次数），话费标题，金额
async def exchangeForDayEx(phone, session, run_Time, delayInterval, title, aid):
    async def delayed_conversion(delay):
        await asyncio.sleep(delay)
        await exchange(phone, session, title, aid)

    tasks = [asyncio.create_task(delayed_conversion(i * delayInterval)) for i in range(int(run_Time))]
    await asyncio.gather(*tasks)


async def exchange(phone, s, title, aid):
    try:
        s.cookies.set_policy(BlockAll())
        if rs:
            bd = js.call('main').split('=')
            ck[bd[0]] = bd[1]
        r = s.post('https://wapact.189.cn:9001/gateway/standExchange/detailNew/exchange', json={"activityId": aid},
                   cookies=ck)
        r_log = f"响应码 {r.status_code}"
        res_log = f"{str(datetime.datetime.now())[11:22]} {get_first_three(phone)} {title} {r_log}"
        if '$_ts=window' in r.text:
            first_request(r.text)
            return
        r = r.json()
        if r["code"] == 0:
            if r["biz"] != {} and r["biz"]["resultCode"] in errcode:
                res_log = f'{str(datetime.datetime.now())[11:22]} {get_first_three(phone)} {title} {errcode[r["biz"]["resultCode"]]} {r_log}'
                if r["biz"]["resultCode"] in ["0", "412"]:
                    if r["biz"]["resultCode"] == "0":
                        msg = str(datetime.datetime.now())[11:22] + get_first_three(phone) + ":" + title + "兑换成功"
                        printn(msg)
                    if phone not in dhjl[yf][title]:
                        dhjl[yf][title] += "#" + phone
                        with open('电信金豆换话费1.log', 'w') as f:
                            json.dump(dhjl, f, ensure_ascii=False)
        else:
            res_log = f'{str(datetime.datetime.now())[11:22]} {get_first_three(phone)} {r} {r_log}'
    except Exception as e:
        printn(e)
        pass
    printn(res_log)


async def dh(phone, s, title, aid, wt):
    # 超时等待
    while wt > time.time():
        pass
    printn(f"{str(datetime.datetime.now())[11:22]} {get_first_three(phone)} {title} 开始兑换")
    await exchangeForDayEx(phone, s, run_num, diffValue, title, aid)


def queryInfo(phone, s):
    global rs
    a = 1
    while a < 10:
        if rs:
            bd = js.call('main').split('=')
            ck[bd[0]] = bd[1]
        r = s.get('https://wapact.189.cn:9001/gateway/golden/api/queryInfo', cookies=ck).json()
        try:
            printn(f'{get_first_three(phone)} 金豆余额 {r["biz"]["amountTotal"]}')
            amountTotal = r["biz"]["amountTotal"]
        except:
            amountTotal = 0
        if amountTotal < 3000:
            if rs == 1:
                bd = js.call('main').split('=')
                ck[bd[0]] = bd[1]
            res = s.post('http://wapact.189.cn:9000/gateway/standExchange/detailNew/exchange',
                         json={"activityId": jdaid},
                         cookies=ck).text
            if '$_ts=window' in res:
                first_request()
                rs = 1
            time.sleep(3)
        else:
            return r
        a += 1
    return r


async def ks(phone, ticket, diffTime, h, ss):
    global wt, run_Time, js, ck, rs
    s = ss
    s.headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36",
        "Referer": "https://wapact.189.cn:9001/JinDouMall/JinDouMall_independentDetails.html"}

    s.timeout = 30
    if rs:
        bd = js.call('main').split('=')
        ck[bd[0]] = bd[1]
    login = s.post('https://wapact.189.cn:9001/unified/user/login',
                   json={"ticket": ticket, "backUrl": "https%3A%2F%2Fwapact.189.cn%3A9001",
                         "platformCode": "P201010301", "loginType": 2}, cookies=ck).json()
    if login['code'] == 0:
        printn(get_first_three(phone) + " 获取token成功")
        ss.headers["Authorization"] = "Bearer " + login["biz"]["token"]
        queryInfo(phone, s)
        if rs:
            bd = js.call('main').split('=')
            ck[bd[0]] = bd[1]
        queryBigDataAppGetOrInfo = s.get(
            'https://wapact.189.cn:9001/gateway/golden/api/queryBigDataAppGetOrInfo?floorType=0&userType=1&page&1&order=2&tabOrder=',
            cookies=ck).json()
        # printn(queryBigDataAppGetOrInfo)
        for i in queryBigDataAppGetOrInfo["biz"]["ExchangeGoodslist"]:
            if '话费' not in i["title"]:
                continue
            if '0.5元' in i["title"] or '5元' in i["title"]:
                jp["9"][i["title"]] = i["id"]
            elif '1元' in i["title"] or '10元' in i["title"]:
                jp["13"][i["title"]] = i["id"]
            else:
                jp["12"][i["title"]] = i["id"]
        if 11 > h > 1:
            h = 9
        elif 23 > h > 1:
            h = 13
        else:
            h = 23
        if len(sys.argv) == 2:
            h = int(sys.argv[1])
        d = jp[str(h)]
        wt = run_Time(h, 59, 59) + kswt - diffTime
        if jp["12"] != {}:
            d.update(jp["12"])
            wt = 0
        tasks = []
        for di in d:
            if di not in dhjl[yf]:
                dhjl[yf][di] = ""
            if phone in dhjl[yf][di]:
                printn(f"{get_first_three(phone)} {di} 已兑换")
            else:
                printn(f"{get_first_three(phone)} {di}")
                if wt - time.time() > 20 * 60:
                    print("等待时间超过20分钟")
                    return
                tasks.append(dh(phone, s, di, d[di], wt))
    else:
        printn(f"{get_first_three(phone)} 获取token {login['message']}")
    await asyncio.gather(*tasks)


async def qgDay(phone, ticket, hour, isTrue, diffTime, ss):
    global js, rs, ck
    if rs:
        bd = js.call('main').split('=')
        ck[bd[0]] = bd[1]
    else:
        await first_request(ss)
    await ks(phone, ticket, diffTime, hour, ss)


load_token_file = 'chinaTelecom_cache.json'
try:
    with open(load_token_file, 'r') as f:
        load_token = json.load(f)
except:
    load_token = {}


async def main(timeDiff, isTRUE, hour):
    global runTime, js_codeRead, js, ck, rs
    tasks = []
    phone_list = PHONES.split('&')
    day = datetime.datetime.now().strftime("%Y%m")
    for phoneV in phone_list:
        value = phoneV.split('@')
        phone, password = value[0], value[1]
        ss = requests.session()
        ticket = False
        if phone in load_token:
            printn(f'{get_first_three(phone)} 使用缓存登录')
            ticket = get_ticket(phone, load_token[phone]['userId'], load_token[phone]['token'], ss)
        if ticket == False:
            printn(f'{get_first_three(phone)} 使用密码登录')
            ticket = userLoginNormal(phone, password, ss)
        printn(f'{get_first_three(phone)}开始登录')
        ss.verify = False
        # ss.cookies.set_policy(BlockAll())
        ss.mount('https://', DESAdapter())
        if ticket:
            if hour > 15:  # 凌晨场次
                if isChecked(phone):
                    printn(f"{get_first_three(phone)}权益已兑换")
                    continue
                else:
                    tasks.append(qgNight(phone, ticket, timeDiff, isTRUE, ss))
                await asyncio.sleep(1)
            else:  # 十点//十四点场次
                tasks.append(qgDay(phone, ticket, hour, isTRUE, timeDiff, ss))
                await asyncio.sleep(1)
        else:
            printn(f'{get_first_three(phone)} 登录失败')
    await asyncio.gather(*tasks)


PHONES = os.environ.get('jdhf')
if __name__ == "__main__":
    h = datetime.datetime.now().hour
    # h=23                    #手动设置场次的时间
    print("当前小时为: " + str(h))
    if 10 > h > 0:
        print("当前小时为: " + str(h) + "已过0点但未到10点开始准备抢十点场次")
        wttime = run_Time(9, 59, 18)  # 抢十点场次
    elif 14 >= h >= 10:
        print("当前小时为: " + str(h) + "已过10点但未到14点开始准备抢十四点场次")
        wttime = run_Time(13, 59, 18)  # 抢十四点场次
    else:
        print("当前小时为: " + str(h) + "已过14点开始准备抢凌晨")
        wttime = run_Time(23, 58, 58)  # 抢凌晨
    # isTRUE=False
    isTRUE = True  # isTRUE等于False则表示忽略所有直接运行(14点后运行程序则会开始23点开启凌晨)
    if (wttime > time.time()):
        wTime = wttime - time.time()
        print("未到时间,计算后差异:" + str(wTime) + "秒")
        if isTRUE:
            print("开始等待:")
            time.sleep(wTime)
    global timeValue, timeDiff
    timeValue = getApiTime("https://f.m.suning.com/api/ct.do")
    timeDiff = timeValue if timeValue > 0 else 0
    print(f"苏宁校时误差{timeDiff}秒")
    asyncio.run(main(timeDiff, isTRUE, h))
    print("所有任务都已执行完毕!")
