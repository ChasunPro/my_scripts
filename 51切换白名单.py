cron:0 0/5 * * * ? 
import requests
import json
import os

key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.Ijk3NjEwMzI1fFd1WWlEYWlMaSI.F2pOhjmo1BLyqcl_-bNjlwDwEoGLMxtMrMaLScAjB-w"

# 判断青龙版本
qlver = os.environ['QL_BRANCH']
if qlver >= 'v2.12.0':
    QLMain='/ql/data/scripts/ip.txt'
else:
    QLMain = '/ql/data/scripts/ip.txt'

## 获取本地IP
def get_ip():
    response = requests.get('https://myip.ipip.net/json')
    data = response.json()
    return data['data']['ip']

##将ip写入本地文件
def write_ip():
    ip = get_ip()
    with open(QLMain, "w+", encoding="utf-8") as f:
        f.truncate(0)
        f.write(ip)

## 读取文件内ip
def read_ip():
    with open(QLMain, "r", encoding="utf-8") as f:
        ip = f.read()
    return ip

## 查看白名单内ip
def get_iplist():
    ip = get_ip()
    ip_list = []
    while True:
        url = f"https://bapi.51daili.com/whiteIP?op=list&appkey={key}&whiteip={ip}"
        response = requests.request("GET",url).json()
        if not "Connection refused" in response['msg']:
            break
    for i in response['data']['list']:
        ip_list.append(i)
    print("当前出口IP：",ip)
    print("当前白名单IP:",str(ip_list))
    if ip in ip_list:
        code = "True"
    else:
        code = "False"
    return code

## 添加ip白名单
def get_add():
    ip = get_ip()
    while True:
        url = f"http://bapi.51daili.com/whiteIP?op=add&appkey={key}&whiteip={ip}"
        response = requests.request("GET", url).json()
        if not "Connection refused" in response['msg']:
            break
    return response['data']

## 删除ip白名单
def get_del():
    ip = read_ip()
    while True:
        url = f"http://bapi.51daili.com/whiteIP?op=del&appkey={key}&whiteip={ip}"
        response = requests.request("GET", url).json()
        if not "Connection refused" in response['msg']:
            break
if __name__ == '__main__':
    iplist = get_iplist()
    if iplist == "False":
        if os.path.exists(QLMain):
            print(get_add())
            write_ip()
        else:
            write_ip()
            print("这是第一次执行，再执行一次")
    else:
        print("ip已在白名单中")
