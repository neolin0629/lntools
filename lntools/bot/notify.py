import json
import requests


def notify_feishu(webhook, message):
    """
    通知飞书
    :param webhook_url: 飞书webhook地址
    :param message: 通知内容
    :return:
    """
    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        "msg_type": "text",
        "content": {
            "text": message
        }
    }

    try:
        response = requests.post(
            webhook,
            headers=headers,
            data=json.dumps(data),
            timeout=10  # 设置超时时间为10秒
        )
        response.raise_for_status()
        print(f"通知发送成功: {message}")
    except requests.exceptions.RequestException as e:
        print(f"通知发送失败: {str(e)}")
