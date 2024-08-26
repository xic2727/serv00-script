import os
import json
import subprocess
from datetime import datetime, timedelta
import requests
import paramiko


def format_to_iso(date):
    return date.strftime('%Y-%m-%d %H:%M:%S')

def send_feishu_message(message):
    url = f"{FEISHU_WEBHOOK_URL}"
    payload = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": "vless存活检查脚本",
                    "content": [
                        [{
                            "tag": "text",
                            "text": message
                        },
                        {
                            "tag": "at",
                            "user_id": "5c668c8f"
                        }]
                    ]
                }
            }
        }
    }
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            print(f"发送消息到feishu失败: {response.text}")
    except Exception as e:
        print(f"发送消息到feishu出错: {e}")


# SSH 连接并执行命令
def check_and_start_v2ray(hostname, port, username, password):
    try:
        # 创建SSH客户端对象
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # 连接到服务器
        ssh.connect(hostname, port, username, password)

        # 检查v2ray进程是否启动
        stdin, stdout, stderr = ssh.exec_command('pgrep xray')
        process_id = stdout.read().decode().strip()

        if process_id:
            print(f"xray 进程已启动，PID: {process_id}")
        else:
            print("xray 进程未启动。正在启动 xray...")
            # 启动 xray 进程
            start_command = 'cd /home/$USER/domains/$USER.serv00.net/xray && nohup ./xray run >> ./output.log 2>&1 &'
            ssh.exec_command(start_command)
            print("xray 已启动。")
            now_beijing = format_to_iso(datetime.utcnow() + timedelta(hours=8))
            send_feishu_message(f"{now_beijing} xray进程未启动，已为您启动xray")

        # 关闭SSH连接
        ssh.close()

    except Exception as e:
        print(f"发生错误: {str(e)}")


# 从环境变量中获取密钥
accounts_json = os.getenv('ACCOUNTS_JSON')
FEISHU_WEBHOOK_URL = os.getenv('FEISHU_WEBHOOK_URL')


# 检查并解析 JSON 字符串
try:
    servers = json.loads(accounts_json)
except json.JSONDecodeError:
    error_message = "ACCOUNTS_JSON 参数格式错误"
    print(error_message)
    send_feishu_message(error_message)
    exit(1)



# 遍历服务器列表并执行恢复操作
for server in servers:
    host = server['host']
    port = server['port']
    username = server['username']
    password = server['password']

    if server['type'] == "vless":
        print(f"连接到 {host}...")
        check_and_start_vless(host, port, username, password)
