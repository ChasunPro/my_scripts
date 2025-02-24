from typing import Optional, Tuple
import json
import requests
import datetime
import random
import time
import re
import os
import sys
import concurrent.futures

ENABLE_CONCURRENT = True  # 是否启用并发执行
MAX_WORKERS = 5  # 最大并发数量

# 配置日志格式
def log(text: str, level: str = "INFO") -> None:
    """统一日志输出格式
    
    Args:
        text: 日志内容
        level: 日志级别，默认为 INFO
    """
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] [{level}] {text}")

def get_env() -> Optional[str]:
    """获取环境变量"""
    try:
        # 内置测试账号
        default_account = ""  
        
        if "kwyy" in os.environ:
            return os.environ["kwyy"]
        # 尝试从配置文件读取
        if os.path.exists("config.txt"):
            with open("config.txt", "r", encoding="utf-8") as f:
                for line in f.readlines():
                    if line.startswith("kwyy="):
                        return line.split("=")[1].strip()
        # 如果环境变量和配置文件都没有，返回默认账号
        log("使用内置测试账号运行")
        return default_account
    except Exception as e:
        log(f"获取环境变量失败: {str(e)}")
        return None

def login(phone: str, password: str, max_retries: int = 3) -> Tuple[str, str, str, str, str]:
    """登录酷我音乐
    
    Args:
        phone: 手机号
        password: 密码
        max_retries: 最大重试次数，默认3次
    """
    auth_url = 'http://kwrw.linzixuan.work/login?km=填写你的卡密'
    login_data = {
        'phone': phone,
        'password': password
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Connection': 'keep-alive',
        'Accept': 'application/json'
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                auth_url,
                json=login_data,
                headers=headers,
                timeout=(5, 15)  # (连接超时, 读取超时)
            )
            
            # 检查响应状态码
            response.raise_for_status()
            
            result = response.json()
            if result.get('code') != 200:
                raise Exception(f"登录失败: {result.get('error', '未知错误')}")
                
            data = result['data']
            return (
                data['username'],
                data['loginSid'], 
                data['loginUid'],
                data['appUid'],
                data['devId']
            )
            
        except requests.Timeout:
            if attempt < max_retries - 1:
                retry_delay = (attempt + 1) * 2  # 递增延迟
                log(f"登录超时，{retry_delay}秒后进行第{attempt + 2}次重试...", "WARN")
                time.sleep(retry_delay)
            else:
                raise Exception("登录服务连续超时，请稍后重试")
                
        except requests.RequestException as e:
            if attempt < max_retries - 1:
                retry_delay = (attempt + 1) * 2
                log(f"登录请求异常: {str(e)}，{retry_delay}秒后进行第{attempt + 2}次重试...", "WARN")
                time.sleep(retry_delay)
            else:
                raise Exception(f"登录服务异常: {str(e)}")
                
        except Exception as e:
            raise Exception(f"登录失败: {str(e)}")

def randomtime():
    random_number = random.randint(1, 5)
    time.sleep(random_number)
    return

def signvideo(loginUid, loginSid, appUid):  # 签到广告奖励
    url = 'https://integralapi.kuwo.cn/api/v1/online/sign/v1/earningSignIn/newDoListen'
    params = {
        'loginUid': loginUid,
        'loginSid': loginSid,
        'appUid': appUid,
        'terminal': 'ar',
        'from': 'sign',
        'adverId': '20130802-14795506463',
        'token': '',
        'extraGoldNum': '100',
        'clickExtraGoldNum': '0',
        'surpriseType': '',
        'verificationId': 'BiXdGRsLjE%252B80I0ekQ6PIxbE2c%252FKyDCJSZQ7KxXsKHE1vO6SDz%252FKJIoDdVbBBzzmi76q7NTHX6vcx1PrX38%252F7xA%253D%253D',
        'mobile': ''
    }

    headers = {
        'Host': 'integralapi.kuwo.cn',
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Not A(Brand";v="99", "Android WebView";v="121", "Chromium";v="121"',
        'Accept': 'application/json, text/plain, */*',
        'sec-ch-ua-mobile': '?1',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 14; POCO F2 Pro Build/UQ1A.240105.004; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/121.0.6167.101 Mobile Safari/537.36/ kuwopage',
        'sec-ch-ua-platform': '"Android"',
        'Origin': 'https://h5app.kuwo.cn',
        'X-Requested-With': 'cn.kuwo.player',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        #'Referer': 'https://h5app.kuwo.cn/apps/earning-sign/index.html?FULLHASARROW=1&showtab=0&kwflag=2642624794_1710263536072',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    response = requests.get(url, params=params, headers=headers)
    r_json = response.json()
    if '成功' in response.text:
        adtype = r_json['data']['obtain']
        print(f'签到广告>>>{adtype}金币')
    else:
        description = r_json['data']['description']
        print(f'签到广告>>>{description}')

def Homepage(loginUid, loginSid, appUid):  # 主页的广告

    url = "https://integralapi.kuwo.cn/api/v1/online/sign/v1/earningSignIn/newDoListen"
    params = {
        'loginUid': loginUid,
        'loginSid': loginSid,
        'appUid': appUid,
        'terminal': 'ar',
        'from': 'surprise',
        'goldNum': '70',
        'adverId': '20130702-14823094126',
        'token': '',
        'clickExtraGoldNum': '0',
        'surpriseType': '',
        'verificationId': '',
        'mobile': ''
    }

    headers = {
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Not A(Brand";v="99", "Android WebView";v="121", "Chromium";v="121"',
        'Accept': 'application/json, text/plain, */*',
        'sec-ch-ua-mobile': '?1',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 14; POCO F2 Pro Build/UQ1A.240105.004; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/121.0.6167.101 Mobile Safari/537.36/ kuwopage',
        'sec-ch-ua-platform': '"Android"',
        'Origin': 'https://h5app.kuwo.cn',
        'X-Requested-With': 'cn.kuwo.player',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        #'Referer': 'https://h5app.kuwo.cn/apps/earning-sign/index.html?FULLHASARROW=1&showtab=0&kwflag=2642624794_1710349908737',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    response = requests.get(url, params=params, headers=headers)
    r_json = response.json()
    if '成功' in response.text:
        adtype = r_json['data']['obtain']
        print(f'主页广告>>>{adtype}金币')
    else:
        description = r_json['data']['description']
        print(f'主页广告>>>{description}')

def openbox(loginUid, loginSid, devId, appUid):
    current_hour = datetime.datetime.now().time().hour

    time_ranges = {
        0: "00-08",
        8: "08-10",
        10: "10-12",
        12: "12-14",
        14: "14-16",
        16: "16-18",
        18: "18-20",
        20: "20-24"
    }

    for start_hour, time_range in time_ranges.items():
        if start_hour <= current_hour < start_hour + 2:
            print(f"当前时间处于 {time_range} 时间段")
            break
    url = "https://integralapi.kuwo.cn/api/v1/online/sign/new/newBoxFinish"
    params = {
        'loginUid': loginUid,
        'loginSid': loginSid,
        'devId': devId,
        'appUid': appUid,
        'source': 'kwplayer_ar_10.7.6.2_qq.apk',
        'version': 'kwplayer_ar_10.7.6.2',
        'r': '0.6345674327264215',
        'action': 'new',
        'time': f'{time_range}',
        'goldNum': '23',
        'extraGoldnum': '0',
        'clickExtraGoldNum': '0'
    }

    headers = {
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Not A(Brand";v="99", "Android WebView";v="121", "Chromium";v="121"',
        'Accept': 'application/json, text/plain, */*',
        'sec-ch-ua-mobile': '?1',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 14; POCO F2 Pro Build/UQ1A.240105.004; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/121.0.6167.101 Mobile Safari/537.36/ kuwopage',
        'sec-ch-ua-platform': '"Android"',
        'Origin': 'https://h5app.kuwo.cn',
        'X-Requested-With': 'cn.kuwo.player',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        #'Referer': 'https://h5app.kuwo.cn/apps/earning-sign/index.html?FULLHASARROW=1&showtab=0&kwflag=2642624794_1710342600688',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    response = requests.get(url, params=params, headers=headers)
    r_json = response.json()
    if '成功' in response.text:
        adtype = r_json['data']['obtain']
        print(f'时间段开宝箱>>>{adtype}金币')
    else:
        description = r_json['data']['description']
        print(f'时间段开宝箱>>>{description}')
    # 开宝箱的弹窗视频

    url = "https://integralapi.kuwo.cn/api/v1/online/sign/v1/earningSignIn/newDoListen"
    params = {
        "loginUid": loginUid,
        "loginSid": loginSid,
        "appUid": appUid,
        "terminal": "ar",
        "from": "sign",
        "adverId": "20130802-13379713291",
        "token": "",
        "extraGoldNum": "88",
        "clickExtraGoldNum": "0",
        "surpriseType": "",
        "verificationId": "",
        "mobile": ""
    }

    headers = {
        "Connection": "keep-alive",
        "sec-ch-ua": '"Not A(Brand";v="99", "Android WebView";v="121", "Chromium";v="121"',
        "Accept": "application/json, text/plain, */*",
        "sec-ch-ua-mobile": "?1",
        "User-Agent": "Mozilla/5.0 (Linux; Android 14; POCO F2 Pro Build/UQ1A.240105.004; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/121.0.6167.101 Mobile Safari/537.36/ kuwopage",
        "sec-ch-ua-platform": '"Android"',
        "Origin": "https://h5app.kuwo.cn",
        "X-Requested-With": "cn.kuwo.player",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        #"Referer": "https://h5app.kuwo.cn/apps/earning-sign/index.html?FULLHASARROW=1&showtab=0&kwflag=2642624794_1710342600688",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    response = requests.get(url, params=params, headers=headers)
    r_json = response.json()
    if '成功' in response.text:
        adtype = r_json['data']['obtain']
        print(f'开宝箱弹窗>>>{adtype}金币')
    else:
        description = r_json['data']['description']
        print(f'开宝箱弹窗>>>{description}')

def sign(loginUid, loginSid, appUid):  # 签到
    # 签到没抓到
    # 签到弹窗

    url = "https://integralapi.kuwo.cn/api/v1/online/sign/v1/earningSignIn/newDoListen"
    params = {
        'loginUid': loginUid,
        'loginSid': loginSid,
        'appUid': appUid,
        'terminal': 'ar',
        'from': 'sign',
        'adverId': '20130802-13379713291',
        'token': '',
        'extraGoldNum': '88',
        'clickExtraGoldNum': '0',
        'surpriseType': '',
        'verificationId': '',
        'mobile': ''
    }

    headers = {
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Not A(Brand";v="99", "Android WebView";v="121", "Chromium";v="121"',
        'Accept': 'application/json, text/plain, */*',
        'sec-ch-ua-mobile': '?1',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 14; POCO F2 Pro Build/UQ1A.240105.004; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/121.0.6167.101 Mobile Safari/537.36/ kuwopage',
        'sec-ch-ua-platform': '"Android"',
        'Origin': 'https://h5app.kuwo.cn',
        'X-Requested-With': 'cn.kuwo.player',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        #'Referer': 'https://h5app.kuwo.cn/apps/earning-sign/index.html?FULLHASARROW=1&showtab=0&kwflag=2642624794_1710342600688',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    response = requests.get(url, params=params, headers=headers)

def draw(loginUid, loginSid, appUid):  # 抽奖
    # 首次免费抽
    url = "https://integralapi.kuwo.cn/api/v1/online/sign/loterry/getLucky"
    params = {
        "loginUid": loginUid,
        "loginSid": loginSid,
        "appUid": appUid,
        'source': 'kwplayer_ar_10.7.6.2_qq.apk',
        'type': 'free'
    }

    headers = {
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Not A(Brand";v="99", "Android WebView";v="121", "Chromium";v="121"',
        'Accept': 'application/json, text/plain, */*',
        'sec-ch-ua-mobile': '?1',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 14; POCO F2 Pro Build/UQ1A.240105.004; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/121.0.6167.101 Mobile Safari/537.36/ kuwopage',
        'sec-ch-ua-platform': '"Android"',
        'Origin': 'https://h5app.kuwo.cn',
        'X-Requested-With': 'cn.kuwo.player',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://h5app.kuwo.cn/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    response = requests.get(url, params=params, headers=headers)
    r_json = response.json()
    if '金币' in response.text:
        adtype = r_json['data']['loterryname']
        print(f'广告抽奖>>>{adtype}')
    else:
        description = r_json['msg']
        print(f'免广告抽奖>>>{description}')
    #  看视频抽
    randomtime()
    url = "https://integralapi.kuwo.cn/api/v1/online/sign/loterry/getLucky"
    params = {
        "loginUid": loginUid,
        "loginSid": loginSid,
        "appUid": appUid,
        'source': 'kwplayer_ar_10.7.6.2_qq.apk',
        'type': 'video'
    }

    headers = {
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Not A(Brand";v="99", "Android WebView";v="121", "Chromium";v="121"',
        'Accept': 'application/json, text/plain, */*',
        'sec-ch-ua-mobile': '?1',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 14; POCO F2 Pro Build/UQ1A.240105.004; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/121.0.6167.101 Mobile Safari/537.36/ kuwopage',
        'sec-ch-ua-platform': '"Android"',
        'Origin': 'https://h5app.kuwo.cn',
        'X-Requested-With': 'cn.kuwo.player',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://h5app.kuwo.cn/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    response = requests.get(url, params=params, headers=headers)
    r_json = response.json()
    if '金币' in response.text:
        adtype = r_json['data']['loterryname']
        print(f'广告抽奖>>>{adtype}')
    else:
        description = r_json['msg']
        print(f'广告抽奖>>>{description}')

def video(loginUid, loginSid, appUid):  # 看视频

    url = "https://integralapi.kuwo.cn/api/v1/online/sign/v1/earningSignIn/newDoListen"
    params = {
        'loginUid': loginUid,
        'loginSid': loginSid,
        'appUid': appUid,
        'terminal': 'ar',
        'from': 'videoadver',
        'goldNum': '58',
        'adverId': '',
        'token': '',
        'extraGoldNum': '0',
        'clickExtraGoldNum': '0',
        'surpriseType': '',
        'verificationId': '',
        'mobile': ''
    }

    headers = {
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Not A(Brand";v="99", "Android WebView";v="121", "Chromium";v="121"',
        'Accept': 'application/json, text/plain, */*',
        'sec-ch-ua-mobile': '?1',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 14; POCO F2 Pro Build/UQ1A.240105.004; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/121.0.6167.101 Mobile Safari/537.36/ kuwopage',
        'sec-ch-ua-platform': '"Android"',
        'Origin': 'https://h5app.kuwo.cn',
        'X-Requested-With': 'cn.kuwo.player',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        #'Referer': 'https://h5app.kuwo.cn/apps/earning-sign/index.html?FULLHASARROW=1&showtab=0&kwflag=2642624794_1710342600688',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    response = requests.get(url, params=params, headers=headers)
    r_json = response.json()
    if '成功' in response.text:
        adtype = r_json['data']['obtain']
        print(f'创意视频>>>{adtype}金币')
    else:
        description = r_json['data']['description']
        print(f'创意视频>>>{description}')
    randomtime()
    # 看广告后的弹窗

    url = "https://integralapi.kuwo.cn/api/v1/online/sign/v1/earningSignIn/newDoListen"
    params = {
        'loginUid': loginUid,
        'loginSid': loginSid,
        'appUid': appUid,
        'terminal': 'ar',
        'from': 'videoadver',
        'adverId': '20130802-14824211622',
        'token': '',
        'extraGoldNum': '110',
        'clickExtraGoldNum': '0',
        'surpriseType': '',
        'verificationId': '',
        'mobile': '',
        'listenTime': '0'
    }
    headers = {
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Not A(Brand";v="99", "Android WebView";v="121", "Chromium";v="121"',
        'Accept': 'application/json, text/plain, */*',
        'sec-ch-ua-mobile': '?1',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 14; POCO F2 Pro Build/UQ1A.240105.004; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/121.0.6167.101 Mobile Safari/537.36/ kuwopage',
        'sec-ch-ua-platform': '"Android"',
        'Origin': 'https://h5app.kuwo.cn',
        'X-Requested-With': 'cn.kuwo.player',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        #'Referer': 'https://h5app.kuwo.cn/apps/earning-sign/index.html?FULLHASARROW=1&showtab=0&kwflag=2642624794_1710342600688',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    response = requests.get(url, params=params, headers=headers)
    r_json = response.json()
    if '成功' in response.text:
        adtype = r_json['data']['obtain']
        print(f'创意视频弹窗>>>{adtype}金币')
    else:
        description = r_json['data']['description']
        print(f'创意视频弹窗>>>{description}')

def collect(loginUid, loginSid, appUid):  # 收藏歌曲

    url = "https://integralapi.kuwo.cn/api/v1/online/sign/v1/earningSignIn/newDoListen"
    params = {
        'loginUid': loginUid,
        'loginSid': loginSid,
        'appUid': appUid,
        'terminal': 'ar',
        'from': 'collect',
        'goldNum': '18',
        'adverId': '',
        'token': '',
        'clickExtraGoldNum': '0',
        'surpriseType': '',
        'verificationId': '',
        'mobile': ''
    }

    headers = {
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Not A(Brand";v="99", "Android WebView";v="121", "Chromium";v="121"',
        'Accept': 'application/json, text/plain, */*',
        'sec-ch-ua-mobile': '?1',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 14; POCO F2 Pro Build/UQ1A.240105.004; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/121.0.6167.101 Mobile Safari/537.36/ kuwopage',
        'sec-ch-ua-platform': '"Android"',
        'Origin': 'https://h5app.kuwo.cn',
        'X-Requested-With': 'cn.kuwo.player',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        #'Referer': 'https://h5app.kuwo.cn/apps/earning-sign/index.html?FULLHASARROW=1&showtab=0&kwflag=2642624794_1710342600688',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    response = requests.get(url, params=params, headers=headers)
    r_json = response.json()
    if '成功' in response.text:
        adtype = r_json['data']['obtain']
        print(f'收藏歌曲>>>{adtype}金币')
    else:
        description = r_json['data']['description']
        print(f'收藏歌曲>>>{description}')

    # 收藏弹窗

    url = "https://integralapi.kuwo.cn/api/v1/online/sign/v1/earningSignIn/newDoListen"
    params = {
        'loginUid': loginUid,
        'loginSid': loginSid,
        'appUid': appUid,
        'terminal': 'ar',
        'from': 'collect',
        'goldNum': '0',
        'adverId': '',
        'token': '',
        'extraGoldNum': '60',
        'clickExtraGoldNum': '0',
        'surpriseType': '',
        'verificationId': '',
        'mobile': '',
        'listenTime': '0'
    }
    randomtime()
    headers = {
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Not A(Brand";v="99", "Android WebView";v="121", "Chromium";v="121"',
        'Accept': 'application/json, text/plain, */*',
        'sec-ch-ua-mobile': '?1',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 14; POCO F2 Pro Build/UQ1A.240105.004; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/121.0.6167.101 Mobile Safari/537.36/ kuwopage',
        'sec-ch-ua-platform': '"Android"',
        'Origin': 'https://h5app.kuwo.cn',
        'X-Requested-With': 'cn.kuwo.player',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        #'Referer': 'https://h5app.kuwo.cn/apps/earning-sign/index.html?FULLHASARROW=1&showtab=0&kwflag=2642624794_1710342600688',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    response = requests.get(url, params=params, headers=headers)
    r_json = response.json()
    if '成功' in response.text:
        adtype = r_json['data']['obtain']
        print(f'收藏歌曲弹窗>>>{adtype}金币')
    else:
        description = r_json['data']['description']
        print(f'收藏歌曲弹窗>>>{description}')

def listentomusic(loginUid, loginSid, appUid):
    times = ['5', '10', '20', '30']
    goldNums = ['43', '57', '60', '99']
    extraGoldNum = ['68', '68', '68', '68']
    url2 = "https://integralapi.kuwo.cn/api/v1/online/sign/v1/earningSignIn/newDoListen"
    url = "https://integralapi.kuwo.cn/api/v1/online/sign/v1/earningSignIn/newDoListen"
    headers = {
        "Host": "integralapi.kuwo.cn",
        "Connection": "keep-alive",
        "sec-ch-ua": '"Not A(Brand";v="99", "Android WebView";v="121", "Chromium";v="121"',
        "Accept": "application/json, text/plain, */*",
        "sec-ch-ua-mobile": "?1",
        "User-Agent": "Mozilla/5.0 (Linux; Android 14; POCO F2 Pro Build/UQ1A.240105.004; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/121.0.6167.101 Mobile Safari/537.36/ kuwopage",
        "sec-ch-ua-platform": '"Android"',
        "Origin": "https://h5app.kuwo.cn",
        "X-Requested-With": "cn.kuwo.player",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        #"Referer": "https://h5app.kuwo.cn/apps/earning-sign/index.html?FULLHASARROW=1&showtab=0&kwflag=2642626091_1711184117441",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    goldNum = 0
    for time in times:
        goldNumcoin = goldNums[goldNum]
        extraGoldNumcoin = extraGoldNum[goldNum]
        params = {
            'loginUid': loginUid,
            'loginSid': loginSid,
            'appUid': appUid,
            "terminal": "ar",
            "from": "listen",
            "goldNum": goldNumcoin,
            "adverId": "",
            "token": "",
            "clickExtraGoldNum": "0",
            "surpriseType": "",
            "verificationId": "",
            "mobile": "",
            "listenTime": time
        }
        params2 = {
            'loginUid': loginUid,
            'loginSid': loginSid,
            'appUid': appUid,
            "terminal": "ar",
            "from": "listen",
            "adverId": "20130802-15030283408",
            "token": "",
            "extraGoldNum": extraGoldNumcoin,
            "clickExtraGoldNum": "0",
            "surpriseType": "",
            "verificationId": "",
            "mobile": "",
            "listenTime": time
        }
        goldNum = goldNum + 1
        response = requests.get(url, params=params, headers=headers)
        r_json = response.json()
        if '成功' in response.text:
            adtype = r_json['data']['obtain']
            print(f'听音乐弹窗>>>{adtype}金币')
        else:
            description = r_json['data']['description']
            print(f'听音乐弹窗>>>{description}')
        randomtime()
        response2 = requests.get(url2, params=params2, headers=headers)
        r_json = response2.json()
        if '成功' in response2.text:
            adtype = r_json['data']['obtain']
            print(f'听音乐>>>{adtype}金币')
        else:
            description = r_json['data']['description']
            print(f'听音乐>>>{description}')
        randomtime()

def task(phone: str, password: str):
    """执行任务的主函数"""
    account_prefix = f"账号[{phone[-4:]}]"
    log(f"{account_prefix} 开始执行任务...")
    
    try:
        log(f"{account_prefix} 正在登录...")
        try:
            username, loginSid, loginUid, appUid, devId = login(phone, password)
            log(f"{account_prefix} 登录成功: {username}")
        except Exception as e:
            log(f"{account_prefix} 登录失败: {str(e)}", "ERROR")
            return  # 登录失败直接返回，不执行后续任务
        
        tasks = [
            ("签到视频", lambda: signvideo(loginUid, loginSid, appUid)),
            ("主页任务", lambda: Homepage(loginUid, loginSid, appUid)),
            ("开宝箱", lambda: openbox(loginUid, loginSid, devId, appUid)),
            ("抽奖", lambda: draw(loginUid, loginSid, appUid)),
            ("观看视频1", lambda: video(loginUid, loginSid, appUid)),
            ("观看视频2", lambda: video(loginUid, loginSid, appUid)),
            ("收藏任务", lambda: collect(loginUid, loginSid, appUid)),
            ("听音乐", lambda: listentomusic(loginUid, loginSid, appUid))
        ]
        
        for task_name, task_func in tasks:
            try:
                log(f"{account_prefix} 执行{task_name}...")
                task_func()
                randomtime()
            except Exception as e:
                log(f"{account_prefix} {task_name}执行失败: {str(e)}", "ERROR")
                
        log(f"{account_prefix} 所有任务执行完成!", "SUCCESS")
        
    except Exception as e:
        log(f"{account_prefix} 任务执行出错: {str(e)}", "ERROR")

def main():
    """主函数"""
    log("酷我音乐任务开始执行", "START")
    print("=" * 50)
    
    # 获取环境变量
    kwyy = get_env()
    if not kwyy:
        log("未找到环境变量 kwyy", "ERROR")
        sys.exit(1)
        
    if '#' not in kwyy:
        log("变量格式不正确，应该包含'#'分隔符", "ERROR")
        sys.exit(1)
        
    # 处理多账号情况
    accounts = kwyy.split('&')
    tasks = []
    
    for account in accounts:
        try:
            params = account.split('#')
            if len(params) < 2:
                log(f"变量格式不完整: {params}", "ERROR")
                continue
                
            phone = params[0]
            password = params[1]
            tasks.append((phone, password))
            
        except Exception as e:
            log(f"账号参数解析出错: {str(e)}", "ERROR")
            continue
    
    log(f"共检测到 {len(tasks)} 个账号")
    print("=" * 50)
    
    if ENABLE_CONCURRENT:
        log(f"开始并发执行任务 (最大并发数: {MAX_WORKERS})")
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(task, phone, password) for phone, password in tasks]
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    log(f"任务执行异常: {str(e)}", "ERROR")
    else:
        log("开始顺序执行任务")
        for phone, password in tasks:
            print("-" * 30)
            task(phone, password)
            
    print("=" * 50)
    log("酷我音乐任务执行完毕", "END")

if __name__ == "__main__":
    main()
