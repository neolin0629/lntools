import time
from typing import Any

import requests

from lntools.utils.log import Logger
log = Logger("lntools.bot.notify")


class FeishuNotifier:
    """
    飞书机器人通知工具类。
    支持文本 (text)、富文本 (post) 以及交互式卡片 (interactive) 消息。
    """

    def __init__(
        self,
        webhook: str,
        timeout: int = 10,
        retries: int = 3,
        session: requests.Session | None = None
    ):
        """
        初始化通知器。

        Args:
            webhook: 飞书 Webhook 地址。
            timeout: 请求超时时间。
            retries: 失败重试次数。
            session: 可选的 requests.Session 实例，用于复用连接。
        """
        self.webhook = webhook
        self.timeout = timeout
        self.retries = retries
        self.session = session or requests.Session()
        self.headers = {"Content-Type": "application/json"}

    def send(self, msg_type: str, content: str | dict[str, Any]) -> bool:
        """
        通用发送方法。

        Args:
            msg_type: 消息类型 ("text", "post", "interactive")
            content: 消息内容。
        """
        payload = self._build_payload(msg_type, content)
        if payload is None:
            return False
        return self._do_post(payload)

    def send_text(self, message: str) -> bool:
        """发送纯文本消息。"""
        return self.send("text", message)

    def send_card(self, title: str, content: str, theme: str = "blue") -> bool:
        """
        发送简单的交互式卡片。

        Args:
            title: 卡片标题。
            content: 卡片正文（支持 Markdown）。
            theme: 标题栏主题颜色。
        """
        card_data = {
            "config": {"enable_forward": True},
            "header": {
                "template": theme,
                "title": {"content": title, "tag": "plain_text"}
            },
            "elements": [{
                "tag": "div",
                "text": {"content": content, "tag": "lark_md"}
            }],
        }
        return self.send("interactive", card_data)

    def _build_payload(self, msg_type: str, content: str | dict[str, Any]) -> dict[str, Any] | None:
        """构建飞书 API 所需的负载数据。"""
        data: dict[str, Any] = {"msg_type": msg_type}

        if msg_type == "text":
            data["content"] = {"text": content}
        elif msg_type == "post":
            if isinstance(content, dict) and "post" in content:
                post_body = content["post"]
            else:
                post_body = (
                    content
                    if isinstance(content, dict)
                    else {"zh_cn": {"title": "", "content": [[{"tag": "text", "text": str(content)}]]}}
                )
            data["content"] = {"post": post_body}
        elif msg_type == "interactive":
            data["card"] = content
        else:
            log.error("Unsupported message type: %s", msg_type)
            return None

        return data

    def _do_post(self, data: dict[str, Any]) -> bool:
        """执行带有指数退避重试的 POST 请求。"""
        for attempt in range(self.retries):
            try:
                response = self.session.post(
                    self.webhook,
                    headers=self.headers,
                    json=data,
                    timeout=self.timeout,
                )
                response.raise_for_status()

                resp_json = response.json()
                if resp_json.get("code") == 0:
                    log.info("Notification sent successfully")
                    return True

                # 业务逻辑错误（如 Webhook 失效、签名错误）通常不需要重试
                log.error("Feishu business error: %s", resp_json)
                return False

            except requests.exceptions.RequestException as exc:
                # 针对 HTTP 4xx 错误（非 429）通常代表客户端请求有误，不进行重试
                if isinstance(exc, requests.exceptions.HTTPError):
                    status_code = exc.response.status_code if exc.response is not None else None
                    if status_code and 400 <= status_code < 500 and status_code != 429:
                        log.error("HTTP %s client error, stopping retries: %s", status_code, exc)
                        return False

                wait_time = 2 ** attempt
                if attempt < self.retries - 1:
                    log.warning(
                        "Notification failed (Attempt %s/%s): %s, retrying in %ss",
                        attempt + 1, self.retries, exc, wait_time
                    )
                    time.sleep(wait_time)
                else:
                    log.error("Notification failed, maximum retries reached: %s", exc)

        return False


if __name__ == "__main__":
    # 使用示例
    WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/a8288a19-4973-4c54-9825-ee0e223cfb93"
    notifier = FeishuNotifier(WEBHOOK_URL)

    notifier.send_text("This is a test message")
    notifier.send_card(
        title="System Alert",
        content="**Level**: P0\n**Detail**: DB connection pool full\n<at id=all></at>",
        theme="red",
    )
    post_content = {
        "zh_cn": {
            "title": "项目更新通知",
            "content": [
                [
                    {"tag": "text", "text": "项目进度："},
                    {"tag": "a", "text": "查看详情", "href": "https://example.com"},
                ],
                [{"tag": "text", "text": "当前状态："}],
                [{"tag": "text", "text": "✅ 任务1已完成\n⏳ 任务2进行中\n"}],
            ],
        }
    }
    notifier.send("post", post_content)
