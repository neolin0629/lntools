"""Tools to send email with enhanced functionality and type safety.
@author Neo
@time 2024/6/12
"""
import re
import smtplib
import time
from typing import Union, List, Optional, Any

from email import encoders
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.utils import parseaddr, formataddr

import pandas as pd
import polars as pl

from lntools.config import CONFIG
from lntools.utils import Logger
from lntools.utils.typing import PathLike

log = Logger("lntools.mail")


class MailPlus:
    """A tool to send emails with rich content support including HTML, images, and attachments."""

    REQUIRED_CONFIG = {'server', 'username', 'password'}
    DEFAULT_PORT = 25
    DEFAULT_TLS_PORT = 465
    CHINESE_PATTERN = re.compile('[\u4e00-\u9fa5]+')

    def __init__(self, cfg: Optional[dict[str, str]] = None) -> None:
        """Initialize MailPlus with configuration.

        Args:
            cfg: Mail configuration dictionary containing server, username, and password.
                 Optional: port (default 25), use_tls (default False).
                 Defaults to CONFIG.mail if None.

        Raises:
            ValueError: If required configuration is missing.
        """
        cfg = cfg or CONFIG.mail
        if not cfg or not all(key in cfg for key in self.REQUIRED_CONFIG):
            raise ValueError("Missing required mail configuration")

        self.use_tls = cfg.get('use_tls', 'false').lower() == 'true'
        default_port = self.DEFAULT_TLS_PORT if self.use_tls else self.DEFAULT_PORT

        self.config: dict[str, Any] = {
            'server': cfg['server'],
            'port': int(cfg.get('port', default_port)),
            'username': cfg['username'],
            'password': cfg['password'],
            'use_tls': self.use_tls
        }

        self.msg = MIMEMultipart()
        self.from_name = self.config['username'].split('@')[0]
        self.msg['From'] = self._format_addr(f'{self.from_name} <{self.config["username"]}>')

        self.text: str = ''
        self.image_cnt: int = 0
        self.to: List[str] = []
        self.cc: List[str] = []

        log.debug("MailPlus initialized: server=%s, port=%d, TLS=%s",
                  cfg['server'], self.config['port'], self.use_tls)

    def _format_addr(self, s: str) -> str:
        """
        Format email address with UTF-8 encoding for display name.

        Args:
            s: Email address string in format "Name <email@example.com>".

        Returns:
            Formatted email address string with proper header encoding.

        Time Complexity: O(n) where n is string length.
        """
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    def _contain_zh(self, s: str) -> bool:
        """
        Check if string contains Chinese (CJK Unified Ideographs) characters.

        Args:
            s: String to check.

        Returns:
            True if Chinese characters found, False otherwise.

        Time Complexity: O(n) where n is string length.
        """
        return bool(self.CHINESE_PATTERN.search(s))

    def newemail(
        self,
        to: Union[str, List[str]],
        subject: str,
        cc: Optional[Union[str, List[str]]] = None
    ) -> "MailPlus":
        """
        Initialize a new email with recipients and subject.

        Args:
            to: Single recipient email or list of recipient emails.
            subject: Email subject line.
            cc: Optional carbon copy recipient(s).

        Returns:
            Self for method chaining.

        Time Complexity: O(n) where n is number of recipients.
        """
        self.to = [to] if isinstance(to, str) else to
        self.cc = [] if cc is None else [cc] if isinstance(cc, str) else cc
        self.msg['To'] = ','.join(self.to)
        self.msg['Subject'] = Header(subject, 'utf-8').encode()
        if self.cc:
            self.msg['Cc'] = ','.join(self.cc)
        return self

    def add_content(self, content: str) -> "MailPlus":
        """
        Add paragraph content to email body.

        Args:
            content: Text content (HTML entities will be escaped by browser).

        Returns:
            Self for method chaining.

        Time Complexity: O(n) where n is content length.
        """
        self.text += f'<p>{content}</p>'
        return self

    def add_title(self, title: str) -> "MailPlus":
        """
        Add H1 title to email body.

        Args:
            title: Title text.

        Returns:
            Self for method chaining.

        Time Complexity: O(n) where n is title length.
        """
        self.text += f'<h1>{title}</h1>'
        return self

    def add_href(self, href: str, title: Optional[str] = None) -> "MailPlus":
        """
        Add hyperlink to email body.

        Args:
            href: Target URL.
            title: Link display text (defaults to href if not provided).

        Returns:
            Self for method chaining.

        Time Complexity: O(1)
        """
        safe_title = title if title else href
        self.text += f'<p><a href="{href}">{safe_title}</a></p>'
        return self

    def add_table(self, df: Union[pd.DataFrame, pl.DataFrame]) -> "MailPlus":
        """
        Add DataFrame as HTML table to email body.

        Args:
            df: pandas or polars DataFrame.

        Returns:
            Self for method chaining.

        Raises:
            ValueError: If DataFrame is empty (0 rows).

        Time Complexity: O(n*m) where n=rows, m=columns.
        """
        if df.shape[0] == 0:
            raise ValueError("Cannot add empty DataFrame as table")

        html_table = (
            df.to_pandas().to_html(index=False)
            if isinstance(df, pl.DataFrame)
            else df.to_html(index=False)
        )
        self.text += html_table
        return self

    def add_images(self, imgs: List[PathLike]) -> "MailPlus":
        """
        Add inline images to email body with CID (Content-ID) references.

        Args:
            imgs: List of image file paths (supports str and Path objects).

        Returns:
            Self for method chaining.

        Raises:
            FileNotFoundError: If any image file does not exist.
            OSError: If file cannot be read.

        Time Complexity: O(n*k) where n=number of images, k=average image size.
        """
        from pathlib import Path

        for img in imgs:
            img_path = Path(img)
            if not img_path.exists():
                log.error("Image file not found: %s", img_path)
                raise FileNotFoundError(f"Image file not found: {img_path}")

            try:
                with open(img_path, 'rb') as f:
                    msg_image = MIMEImage(f.read())
                    cid = str(self.image_cnt)
                    msg_image.add_header('Content-ID', f'<{cid}>')
                    self.msg.attach(msg_image)
                    self.text += f'<p><img src="cid:{cid}"></p>'
                    self.image_cnt += 1
                    log.debug("Attached image: %s (CID: %s)", img_path.name, cid)
            except OSError as e:
                log.error("Failed to read image file '%s': %s", img_path, e)
                raise OSError(f"Cannot read image file: {img_path}") from e
        return self

    def add_attachments(self, files: List[PathLike]) -> "MailPlus":
        """
        Add file attachments to email (supports any file type).

        Args:
            files: List of file paths to attach (supports str and Path objects).

        Returns:
            Self for method chaining.

        Raises:
            FileNotFoundError: If any file does not exist.
            OSError: If file cannot be read.

        Time Complexity: O(n*k) where n=number of files, k=average file size.
        """
        from pathlib import Path

        for file in files:
            file_path = Path(file)
            if not file_path.exists():
                log.error("Attachment file not found: %s", file_path)
                raise FileNotFoundError(f"Attachment file not found: {file_path}")

            try:
                with open(file_path, 'rb') as f:
                    mime = MIMEBase('application', 'octet-stream')
                    mime.set_payload(f.read())
                    encoders.encode_base64(mime)

                    filename = file_path.name
                    filename_header = (
                        Header(filename, 'gbk').encode()
                        if self._contain_zh(filename)
                        else filename
                    )

                    mime.add_header('Content-Disposition', 'attachment', filename=filename_header)
                    self.msg.attach(mime)
                    log.debug("Attached file: %s (%d bytes)", filename, file_path.stat().st_size)
            except OSError as e:
                log.error("Failed to read attachment file '%s': %s", file_path, e)
                raise OSError(f"Cannot read attachment file: {file_path}") from e
        return self

    def sendmail(self, retries: int = 3, retry_delay: float = 2.0) -> bool:
        """Send the email with all added content.

        Args:
            retries: Maximum retry attempts on failure (default: 3).
            retry_delay: Delay in seconds between retries (default: 2.0).

        Returns:
            bool: True if sent successfully, False otherwise

        Raises:
            ValueError: If no recipients are specified
        """
        if not self.to and not self.cc:
            log.error("No recipients specified for email")
            raise ValueError("No recipients specified")

        self.msg.attach(MIMEText(self.text, 'html', 'utf-8'))
        recipients = self.to + self.cc

        for attempt in range(retries):
            try:
                if self.config['use_tls']:
                    # Use SMTP_SSL for TLS connection
                    with smtplib.SMTP_SSL(
                        self.config['server'],
                        self.config['port'],
                        timeout=30
                    ) as smtp:
                        smtp.login(self.config['username'], self.config['password'])
                        smtp.sendmail(self.config['username'], recipients, self.msg.as_string())
                else:
                    # Use standard SMTP
                    with smtplib.SMTP(
                        self.config['server'],
                        self.config['port'],
                        timeout=30
                    ) as smtp:
                        smtp.login(self.config['username'], self.config['password'])
                        smtp.sendmail(self.config['username'], recipients, self.msg.as_string())

                log.info("Email sent successfully to %d recipient(s)", len(recipients))
                return True

            except smtplib.SMTPAuthenticationError as e:
                log.error("SMTP authentication failed: %s", e)
                return False  # Don't retry on auth failure

            except smtplib.SMTPException as e:
                if attempt < retries - 1:
                    log.warning(
                        "Email send failed (attempt %d/%d): %s, retrying in %.1fs",
                        attempt + 1, retries, e, retry_delay
                    )
                    time.sleep(retry_delay)
                else:
                    log.error("Email send failed after %d attempts: %s", retries, e)
                    return False

            except (ConnectionError, OSError, TimeoutError) as e:
                if attempt < retries - 1:
                    log.warning(
                        "Connection error (attempt %d/%d): %s, retrying in %.1fs",
                        attempt + 1, retries, e, retry_delay
                    )
                    time.sleep(retry_delay)
                else:
                    log.error("Connection failed after %d attempts: %s", retries, e)
                    return False

        return False

    def set_server(self, cfg: dict[str, str]) -> "MailPlus":
        """Update mail server configuration.

        Args:
            cfg: Mail configuration dictionary containing server, username, and password.
                 Optional: port, use_tls. Must include all required config keys.

        Returns:
            self for method chaining

        Raises:
            ValueError: If required configuration is missing or invalid
        """
        # Validate configuration
        if not cfg or not all(key in cfg for key in self.REQUIRED_CONFIG):
            raise ValueError("Missing required mail configuration")

        try:
            self.use_tls = cfg.get('use_tls', 'false').lower() == 'true'
            default_port = self.DEFAULT_TLS_PORT if self.use_tls else self.DEFAULT_PORT

            # Update configuration
            self.config = {
                'server': cfg['server'],
                'port': int(cfg.get('port', default_port)),
                'username': cfg['username'],
                'password': cfg['password'],
                'use_tls': self.use_tls
            }

            # Update message headers
            self.msg = MIMEMultipart()
            self.from_name = self.config['username'].split('@')[0]
            self.msg['From'] = self._format_addr(f'{self.from_name} <{self.config["username"]}>')

            # Clear existing content
            self.text = ''
            self.image_cnt = 0
            self.to = []
            self.cc = []

            log.info("Mail server updated: %s:%d (TLS: %s)",
                     self.config['server'], self.config['port'], self.use_tls)
            return self

        except (KeyError, ValueError) as e:
            log.error("Invalid mail configuration: %s", e)
            raise ValueError(f"Invalid configuration: {str(e)}") from e

    @property
    def help(self):
        return """
        The properties of `mailplus`, write in `~/.cache/np/lntools/mail.ini`:

        [xxxx]
        server = smtp.163.com
        username = xxx@163.com
        password = xxx%

        1. how to send a mail

            # Example usage with method chaining
            mail = MailPlus()
            success = (mail.newemail("recipient@example.com", "Test Email")
                        .add_title("Report")
                        .add_content("Please find the report attached.")
                        .add_table(df)
                        .add_images(["graph1.png", "graph2.png"])
                        .add_attachments(["report.pdf"])
                        .sendmail())

        2. change mail server

            s_dict = {
                "server": "smtp.163.com",
                "username": "xxx@163.com",
                "password": "xxx%",
            }
            m.set_server(s_dict)
        """
