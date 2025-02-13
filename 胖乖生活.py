import requests
import json
import os
from urllib.parse import quote
import time as timemodule
from datetime import datetime, timedelta, time

accounts = os.getenv('pgsh')
accounts_list = os.environ.get('pgsh').split('@')
num_of_accounts = len(accounts_list)
print(f"获取到 {num_of_accounts} 个账号")
for i, account in enumerate(accounts_list, start=1):
    name = ''
    token = account
    print(f"token为{token}")
    nameurl = "https://userapi.qiekj.com/user/info"
    nameheaders = {
        "Authorization": token,
        "Version": "1.38.0",
        "channel": "android_app",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Content-Length": "38",
        "Host": "userapi.qiekj.com",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "User-Agent": "okhttp/3.14.9"
    }
    namedata = f"token={token}"
    nameresponse = requests.post(url=nameurl, headers=nameheaders, data=namedata)
    if (nameresponse.json()['data']['userName'] == None):
        name = nameresponse.json()['data']['phone']
    else:
        name = nameresponse.json()['data']['userName']
    print(f"\n=======执行账号{i}:{name}=======")
    url = "https://userapi.qiekj.com/task/completed"
    headers = {
        "Host": "userapi.qiekj.com",
        "Authorization": token,
        "Version": "1.38.0",
        "channel": "android_app",
        "content-length": "60",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "User-Agent": "okhttp/3.14.9",
    }
    print(f"--APP视频--")
    for j in range(11):
        data = f"taskType=2&token={token}"
        response = requests.post(url, headers=headers, data=data).json()
        timemodule.sleep(5)
        if response['data'] == True:
            print(f"已完成{j + 1}次")
        else:
            print("APP广告任务完成")
            break
    print(f"--ZFB视频--")
    for t in range(11):
        data = f"taskType=9&token={token}"
        response = requests.post(url, headers=headers, data=data).json()
        timemodule.sleep(5)
        if response['data'] == True:
            print(f"已完成{t + 1}次")
        else:
            print("支付宝广告任务完成")
            break
    print(f"--看广告赚积分--")
    for m in range(8):
        data = f"taskCode=18893134-715b-4307-af1c-b5737c70f58d&token={token}"
        response = requests.post(url, headers=headers, data=data).json()
        timemodule.sleep(3)
        if response['data'] == True:
            print(f"已完成{m + 1}次")
        else:
            print("任务完成")
            break
    print(f"--报名积分打卡--")
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    encoded_current_time = quote(current_time)
    headers = {
        "Host": "userapi.qiekj.com",
        "Authorization": token,
        "Version": "1.38.0",
        "channel": "android_app",
        "content-length": "60",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "User-Agent": "okhttp/3.14.9",
    }
    url1 = "https://userapi.qiekj.com/markActivity/queryMarkTaskByStartTime"
    url2 = "https://userapi.qiekj.com/markActivity/doApplyTask"
    data4 = {'startTime': encoded_current_time, 'token': token}
    respones = requests.post(url1, headers=headers, data=data4).json()["data"]["taskCode"]
    data5 = {"taskCode": respones, "token": token, }
    respone = requests.post(url2, headers=headers, data=data5).json()["msg"]
    print(f'积分报名结果：{respone}')
    timemodule.sleep(2)
    print(f"--签到--")
    url = "https://userapi.qiekj.com/signin/signInAcList"
    data6 = {"token": token}
    response = requests.post(url, headers=headers, data=data6).json()["data"]["id"]
    url1 = "https://userapi.qiekj.com/signin/doUserSignIn"
    data7 = {"activityId": response, "token": token}
    qiandao = requests.post(url1, headers=headers, data=data7).json()
    if qiandao["msg"] == '成功':
        print("签到成功获得:", qiandao["data"]["totalIntegral"])
    else:
        print(qiandao["msg"])
        timemodule.sleep(2)
    print(f"--瓜分积分--")
    url1 = "https://userapi.qiekj.com/markActivity/queryMarkTaskByStartTime"
    url2 = "https://userapi.qiekj.com/markActivity/doMarkTask"
    url3 = "https://userapi.qiekj.com/markActivity/markTaskReward"
    current_datetime = datetime.now()
    yesterday_datetime = current_datetime - timedelta(days=1)
    yesterday_now = yesterday_datetime.replace(hour=current_datetime.hour, minute=current_datetime.minute,
                                               second=current_datetime.second)
    k = quote(yesterday_now.strftime("%Y-%m-%d %H:%M:%S"))
    data = {"startTime": k, "token": token}
    respones = requests.post(url1, headers=headers, data=data).json()["data"]["taskCode"]
    data1 = {"taskCode": respones, "token": token, }
    respone = requests.post(url2, headers=headers, data=data1).json()["msg"]
    current_time = datetime.now().time()
    afternoon_two = time(14, 10, 0)
    if current_time > afternoon_two:
        guafen = requests.post(url3, headers=headers, data=data1).json()["data"]
        print("获得:", guafen)
    else:
        print("当前未到瓜分时间")
        timemodule.sleep(2)
    print("--阶梯任务--")
    timemodule.sleep(2)
    url = "https://userapi.qiekj.com/ladderTask/applyLadderReward"
    data01 = f"rewardCode=reward_code_01&token={token}"
    data02 = f"rewardCode=reward_code_02&token={token}"
    data03 = f"rewardCode=reward_code_03&token={token}"
    headers = {
        "Authorization": token,
        "Version": "1.50.3",
        "channel": "android_app",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Content-Length": "64",
        "Host": "userapi.qiekj.com",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "User-Agent": "okhttp/3.14.9",
    }
    response01 = requests.post(url, headers=headers, data=data01).json()
    response02 = requests.post(url, headers=headers, data=data02).json()
    response03 = requests.post(url, headers=headers, data=data03).json()
    if response01['msg'] == '成功':
        print('已领取5积分')
    elif response01['msg'] == '已领取奖励':
        print('已领过')
    else:
        print("任务数量未达标")
    timemodule.sleep(5)
    if response02['msg'] == '成功':
        print('已领取10积分')
    elif response02['msg'] == '已领取奖励':
        print('已领过')
    else:
        print("任务数量未达标")
    timemodule.sleep(5)
    if response03['msg'] == '成功':
        print('已领取15积分')
    elif response03['msg'] == '已领取奖励':
        print('已领过')
    else:
        print("任务数量未达标")
    timemodule.sleep(2)
    print(f"--查询积分--")
    url = "https://userapi.qiekj.com/signin/getTotalIntegral"
    headers = {
        "Host": "userapi.qiekj.com",
        "Authorization": token,
        "Version": "1.38.0",
        "channel": "android_app",
        "content-length": "60",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Accept-Encoding": "gzip",
        "User-Agent": "okhttp/3.14.9",
    }
    data8 = f"token={token}"
    response = requests.post(url, headers=headers, data=data8)
    data = response.json()['data']
    if data is not None:
        print(f'账户剩余积分：{data}')
