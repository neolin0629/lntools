import json
import time
import requests

from lntools.utils.log import Logger

log = Logger("lntools.bot.notify")


def notify_feishu(
    webhook: str,
    message: str,
    msg_type: str = "text",
    retries: int = 3,
    timeout: int = 10
) -> bool:
    """
    发送飞书通知
    
    Args:
        webhook: 飞书 webhook 地址
        message: 通知内容
        msg_type: 消息类型，"text" 或 "post"
        retries: 失败重试次数，默认3次
        timeout: 请求超时时间（秒），默认10秒
    
    Returns:
        bool: 发送是否成功
    """
    headers = {
        'Content-Type': 'application/json'
    }

    # 构建不同类型的消息体
    if msg_type == "text":
        data = {
            "msg_type": "text",
            "content": {
                "text": message
            }
        }
    elif msg_type == "post":
        data = {
            "msg_type": "post",
            "content": {
                "post": message
            }
        }
    else:
        log.error(f"不支持的消息类型: {msg_type}")
        return False

    # 重试机制，指数退避
    for attempt in range(retries):
        try:
            response = requests.post(
                webhook,
                headers=headers,
                data=json.dumps(data),
                timeout=timeout
            )
            response.raise_for_status()
            log.info(f"通知发送成功: {message}")
            return True
        except requests.exceptions.RequestException as e:
            wait_time = 2 ** attempt  # 指数退避: 1s, 2s, 4s...
            if attempt < retries - 1:
                log.warning(f"通知发送失败 (尝试 {attempt + 1}/{retries}): {str(e)}，{wait_time}秒后重试")
                time.sleep(wait_time)
            else:
                log.error(f"通知发送失败 (已重试{retries}次): {str(e)}")
    
    return False
