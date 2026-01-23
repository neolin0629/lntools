from collections.abc import Sequence
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
        session: requests.Session | None = None,
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

    def send_text(
        self,
        message: str,
        mentioned_list: Sequence[str] | None = None,
    ) -> bool:
        """
        Send plain text message.

        Args:
            message: Text message content
            mentioned_list: List of user IDs to @mention (e.g., ["ou_xxxx", "ou_yyyy"] or ["all"])
            mentioned_mobile_list: List of mobile numbers to @mention

        Returns:
            True if sent successfully

        Note:
            - Content limit is roughly 10000 bytes (UTF-8)
            - Use <at user_id="ou_xxx"></at> syntax for mentions in message text
            - Or use mentioned_list/mentioned_mobile_list parameters

        Example:
            # Method 1: Use mentioned_list parameter
            notifier.send_text("Task completed", mentioned_list=["all"])

            # Method 2: Use <at> tag in message
            notifier.send_text("Task completed <at user_id=\"all\"></at>")
        """
        # 简单的长度警告
        if len(message.encode("utf-8")) > 10000:
            log.warning("Message length exceeds 10000 bytes, may fail to send.")

        # 构建完整消息文本（添加 @提及）
        full_text = message

        # 添加用户ID提及
        if mentioned_list:
            for user_id in mentioned_list:
                full_text += f' <at user_id="{user_id}"></at>'

        return self.send("text", full_text)

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
            "header": {"template": theme, "title": {"content": title, "tag": "plain_text"}},
            "elements": [{"tag": "div", "text": {"content": content, "tag": "lark_md"}}],
        }
        return self.send("interactive", card_data)

    def _build_payload(self, msg_type: str, content: str | dict[str, Any]) -> dict[str, Any] | None:
        """
        构建飞书 API 所需的负载数据。

        Args:
            msg_type: 消息类型
            content: 消息内容（text类型为字符串，其他为字典）

        Returns:
            符合飞书API规范的payload字典
        """
        data: dict[str, Any] = {"msg_type": msg_type}

        if msg_type == "text":
            # 文本消息：content 应为字符串
            data["content"] = {"text": str(content)}

        elif msg_type == "post":
            # 富文本消息：确保正确的嵌套结构
            if isinstance(content, dict):
                # 如果已经有正确的结构，直接使用
                if "zh_cn" in content or "en_us" in content:
                    data["content"] = {"post": content}
                # 如果有 post 键，提取其内容
                elif "post" in content:
                    data["content"] = {"post": content["post"]}
                else:
                    # 否则作为默认中文内容
                    data["content"] = {"post": content}
            else:
                # 字符串内容转换为默认格式
                data["content"] = {
                    "post": {
                        "zh_cn": {
                            "title": "",
                            "content": [[{"tag": "text", "text": str(content)}]]
                        }
                    }
                }

        elif msg_type == "interactive":
            # 交互式卡片
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

                wait_time = 2**attempt
                if attempt < self.retries - 1:
                    log.warning(
                        "Notification failed (Attempt %s/%s): %s, retrying in %ss",
                        attempt + 1,
                        self.retries,
                        exc,
                        wait_time,
                    )
                    time.sleep(wait_time)
                else:
                    log.error("Notification failed, maximum retries reached: %s", exc)

        return False


class WeComNotifier:
    """
    企业微信机器人通知工具类。

    支持文本 (text)、Markdown (markdown)、图片 (image)、图文 (news)、
    文件 (file) 以及模板卡片 (template_card) 消息。

    API文档: https://developer.work.weixin.qq.com/document/path/91770
    """

    def __init__(
        self,
        webhook: str,
        timeout: int = 10,
        retries: int = 3,
        session: requests.Session | None = None,
    ):
        """
        Initialize WeChat Work notifier.

        Args:
            webhook: WeChat Work webhook URL
            timeout: Request timeout in seconds
            retries: Number of retry attempts on failure
            session: Optional requests.Session for connection reuse
        """
        self.webhook = webhook
        self.timeout = timeout
        self.retries = retries
        self.session = session or requests.Session()
        self.headers = {"Content-Type": "application/json"}

    def send(self, msg_type: str, content: dict[str, Any]) -> bool:
        """
        Generic send method.

        Args:
            msg_type: Message type ("text", "markdown", "image", "news", "file", "template_card")
            content: Message content dictionary

        Returns:
            True if sent successfully, False otherwise
        """
        payload = self._build_payload(msg_type, content)
        if payload is None:
            return False
        return self._do_post(payload)

    def send_text(
        self,
        message: str,
        mentioned_list: Sequence[str] | None = None,
        mentioned_mobile_list: Sequence[str] | None = None,
    ) -> bool:
        """
        Send plain text message.

        Args:
            message: Text message content
            mentioned_list: Sequence of userids to @mention (e.g., ["user1", "user2"] or ("user1", "user2"))
            mentioned_mobile_list: Sequence of mobile numbers to @mention

        Returns:
            True if sent successfully

        Example:
            notifier.send_text("Task completed", mentioned_list=["@all"])
            notifier.send_text("Alert", mentioned_list=("admin1", "admin2"))  # tuple also works
        """
        content = {
            "content": message,
            "mentioned_list": list(mentioned_list) if mentioned_list else [],
            "mentioned_mobile_list": list(mentioned_mobile_list) if mentioned_mobile_list else [],
        }
        return self.send("text", content)

    def send_markdown(self, message: str) -> bool:
        """
        Send Markdown formatted message.

        Note: Webhook Markdown does NOT support 'mentioned_list' field.
        To mention users in Markdown, use syntax: <@userid> in the message string.
        """
        content = {"content": message}
        return self.send("markdown", content)

    def send_image(self, image_base64: str, md5: str) -> bool:
        """
        Send image message.

        Args:
            image_base64: Base64 encoded image data
            md5: MD5 hash of image file

        Returns:
            True if sent successfully

        Example:
            import base64
            import hashlib

            with open("chart.png", "rb") as f:
                img_data = f.read()
            img_base64 = base64.b64encode(img_data).decode()
            img_md5 = hashlib.md5(img_data).hexdigest()
            notifier.send_image(img_base64, img_md5)
        """
        content = {"base64": image_base64, "md5": md5}
        return self.send("image", content)

    def send_news(self, articles: Sequence[dict[str, str]]) -> bool:
        """
        Send news (rich media) message with multiple articles.

        Args:
            articles: Sequence of article dicts with keys:
                - title: Article title (required)
                - description: Article description (optional)
                - url: Article URL (required)
                - picurl: Cover image URL (optional)

        Returns:
            True if sent successfully

        Example:
            articles = [
                {
                    "title": "Daily Market Report",
                    "description": "Market summary for 2026-01-13",
                    "url": "https://example.com/report/20260113",
                    "picurl": "https://example.com/cover.jpg"
                },
                {
                    "title": "Trading Alert",
                    "url": "https://example.com/alert"
                }
            ]
            notifier.send_news(articles)
        """
        if not articles or len(articles) == 0:
            log.error("Articles list cannot be empty")
            return False

        # 转换为list以支持切片操作
        articles_list = list(articles)
        if len(articles_list) > 8:
            log.warning("Maximum 8 articles allowed, truncating to first 8")
            articles_list = articles_list[:8]

        content = {"articles": articles_list}
        return self.send("news", content)

    def send_file(self, media_id: str) -> bool:
        """
        Send file message.

        Note: media_id must be obtained by uploading file to WeChat Work API first.

        Args:
            media_id: Media ID from WeChat Work upload API

        Returns:
            True if sent successfully
        """
        content = {"media_id": media_id}
        return self.send("file", content)

    def send_template_card(self, card_type: str, card_data: dict[str, Any]) -> bool:
        """
        Send template card message (text_notice or news_notice).

        Args:
            card_type: "text_notice" or "news_notice"
            card_data: Card configuration dict (see WeChat Work API docs)

        Returns:
            True if sent successfully

        Example (text_notice):
            card_data = {
                "source": {
                    "icon_url": "https://example.com/icon.png",
                    "desc": "Data Pipeline"
                },
                "main_title": {
                    "title": "Task Completed",
                    "desc": "Data processing finished successfully"
                },
                "emphasis_content": {
                    "title": "100%",
                    "desc": "Completion Rate"
                },
                "sub_title_text": "2026-01-13 10:00:00",
                "horizontal_content_list": [
                    {"keyname": "Records", "value": "1,500,000"},
                    {"keyname": "Duration", "value": "5 min 32 sec"}
                ],
                "card_action": {
                    "type": 1,
                    "url": "https://example.com/details"
                }
            }
            notifier.send_template_card("text_notice", card_data)
        """
        content = {"card_type": card_type, **card_data}
        return self.send("template_card", content)

    def send_text_notice_card(
        self,
        title: str,
        description: str = "",
        emphasis_title: str = "",
        emphasis_desc: str = "",
        url: str = "",
        fields: Sequence[dict[str, str]] | None = None,
    ) -> bool:
        """
        Send simplified text notice card.

        Args:
            title: Main title
            description: Main description
            emphasis_title: Emphasized content title (e.g., "99.9%")
            emphasis_desc: Emphasized content description (e.g., "Success Rate")
            url: Action URL when card is clicked
            fields: Sequence of key-value pairs, e.g., [{"keyname": "Status", "value": "OK"}]

        Returns:
            True if sent successfully
        """
        card_data: dict[str, Any] = {"main_title": {"title": title}}

        if description:
            card_data["main_title"]["desc"] = description

        if emphasis_title or emphasis_desc:
            card_data["emphasis_content"] = {}
            if emphasis_title:
                card_data["emphasis_content"]["title"] = emphasis_title
            if emphasis_desc:
                card_data["emphasis_content"]["desc"] = emphasis_desc

        if fields:
            card_data["horizontal_content_list"] = list(fields)

        if url:
            card_data["card_action"] = {"type": 1, "url": url}

        return self.send_template_card("text_notice", card_data)

    def _build_payload(self, msg_type: str, content: dict[str, Any]) -> dict[str, Any] | None:
        """
        Build WeChat Work API payload.

        Args:
            msg_type: Message type
            content: Message content

        Returns:
            Payload dict or None if invalid
        """
        valid_types = {"text", "markdown", "image", "news", "file", "template_card"}
        if msg_type not in valid_types:
            log.error("Unsupported message type: %s. Valid types: %s", msg_type, valid_types)
            return None

        payload: dict[str, Any] = {"msgtype": msg_type}

        # 企业微信的消息格式：每种类型都有自己的键名
        if msg_type == "text":
            payload["text"] = content
        elif msg_type == "markdown":
            payload["markdown"] = content
        elif msg_type == "image":
            payload["image"] = content
        elif msg_type == "news":
            payload["news"] = content
        elif msg_type == "file":
            payload["file"] = content
        elif msg_type == "template_card":
            payload["template_card"] = content

        return payload

    def _do_post(self, data: dict[str, Any]) -> bool:
        """
        Execute POST request with exponential backoff retry.

        Args:
            data: Payload to send

        Returns:
            True if successful, False otherwise
        """
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

                # 企业微信成功返回: {"errcode": 0, "errmsg": "ok"}
                if resp_json.get("errcode") == 0:
                    log.info("WeChat Work notification sent successfully")
                    return True

                # 业务逻辑错误（如 Webhook 失效、频率限制）
                errcode = resp_json.get("errcode")
                errmsg = resp_json.get("errmsg", "Unknown error")

                # 常见错误码：
                # 93000: Webhook 地址无效
                # 45009: 接口调用超过限制
                # 40001: 不合法的secret参数
                log.error("WeChat Work API error [%s]: %s", errcode, errmsg)

                # 如果是频率限制错误，可以重试
                if errcode == 45009 and attempt < self.retries - 1:
                    wait_time = 2**attempt
                    log.warning("Rate limit exceeded, retrying in %ss", wait_time)
                    time.sleep(wait_time)
                    continue

                return False

            except requests.exceptions.RequestException as exc:
                # HTTP 4xx 错误（非 429）通常代表请求有误，不进行重试
                if isinstance(exc, requests.exceptions.HTTPError):
                    status_code = exc.response.status_code if exc.response is not None else None
                    if status_code and 400 <= status_code < 500 and status_code != 429:
                        log.error("HTTP %s client error, stopping retries: %s", status_code, exc)
                        return False

                wait_time = 2**attempt
                if attempt < self.retries - 1:
                    log.warning(
                        "Notification failed (Attempt %s/%s): %s, retrying in %ss",
                        attempt + 1,
                        self.retries,
                        exc,
                        wait_time,
                    )
                    time.sleep(wait_time)
                else:
                    log.error("Notification failed, maximum retries reached: %s", exc)

        return False

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"WeComNotifier(webhook='{self.webhook[:50]}...', timeout={self.timeout}, retries={self.retries})"
