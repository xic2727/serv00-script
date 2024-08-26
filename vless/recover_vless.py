import os
import json
import subprocess
import requests

def send_feishu_message(message):
    url = f"{FEISHU_WEBHOOK_URL}"
    payload = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": "serv00自动登录脚本",
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

# 从环境变量中获取密钥
accounts_json = os.getenv('ACCOUNTS_JSON')
telegram_token = os.getenv('TELEGRAM_TOKEN')
telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')

# 检查并解析 JSON 字符串
try:
    servers = json.loads(accounts_json)
except json.JSONDecodeError:
    error_message = "ACCOUNTS_JSON 参数格式错误"
    print(error_message)
    send_telegram_message(telegram_token, telegram_chat_id, error_message)
    exit(1)

# 初始化汇总消息
summary_message = "serv00-vless 恢复操作结果：\n"

# 默认恢复命令
default_restore_command = "cd ~/domains/$USER.serv00.net/vless && ./check_vless.sh"

# 遍历服务器列表并执行恢复操作
for server in servers:
    host = server['host']
    port = server['port']
    username = server['username']
    password = server['password']
    cron_command = server.get('cron', default_restore_command)

    print(f"连接到 {host}...")

    # 执行恢复命令（这里假设使用 SSH 连接和密码认证）
    restore_command = f"sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -p {port} {username}@{host} '{cron_command}'"
    try:
        output = subprocess.check_output(restore_command, shell=True, stderr=subprocess.STDOUT)
        summary_message += f"\n成功恢复 {host} 上的 vless 服务：\n{output.decode('utf-8')}"
    except subprocess.CalledProcessError as e:
        summary_message += f"\n无法恢复 {host} 上的 vless 服务：\n{e.output.decode('utf-8')}"

# 发送汇总消息到 Telegram
send_feishu_message(summary_message)
