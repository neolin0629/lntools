"""Tools to send email with enhanced functionality and type safety.
@author Neo
@time 2024/6/12
"""
import re
import smtplib
from pathlib import PurePath
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
from lntools.utils.typing import PathLike


class MailPlusError(Exception):
    """Custom exception for MailPlus errors."""
    def __init__(self, message: str = None, error_code: int = None):
        self.message = message or "An error occurred in MailPlus"
        self.error_code = error_code
        super().__init__(self.message)

    def __str__(self):
        if self.error_code:
            return f"[Error {self.error_code}] {self.message}"
        return self.message


class MailPlus:
    """A tool to send emails with rich content support including HTML, images, and attachments."""

    REQUIRED_CONFIG = {'server', 'username', 'password'}
    DEFAULT_PORT = 25
    CHINESE_PATTERN = re.compile('[\u4e00-\u9fa5]+')

    def __init__(self, cfg: Optional[dict[str, str]] = CONFIG.mail) -> None:
        """Initialize MailPlus with configuration.

        Args:
            cfg: Mail configuration dictionary containing server, username, and password.
                 Defaults to CONFIG.mail.

        Raises:
            MailPlusError: If required configuration is missing.
        """
        if not cfg or not all(key in cfg for key in self.REQUIRED_CONFIG):
            raise MailPlusError("Missing required mail config. Please check ~/.config/lntools/lntools.yaml")

        self.config: dict[str, Any] = {
            'server': cfg['server'],
            'port': int(cfg.get('port', self.DEFAULT_PORT)),
            'username': cfg['username'],
            'password': cfg['password']
        }

        self.msg = MIMEMultipart()
        self.from_name = self.config['username'].split('@')[0]
        self.msg['From'] = self._format_addr(f'{self.from_name} <{self.config["username"]}>')

        self.text: str = ''
        self.image_cnt: int = 0
        self.to: List[str] = []
        self.cc: List[str] = []

    def _format_addr(self, s: str) -> str:
        """Format email address with proper encoding."""
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    def _contain_zh(self, s: str) -> bool:
        """Check if string contains Chinese characters."""
        return bool(self.CHINESE_PATTERN.search(s))

    def newemail(self, to: Union[str, List[str]],
                 subject: str,
                 cc: Optional[Union[str, List[str]]] = None):
        """Create a new email with recipients and subject.

        Args:
            to: Single recipient or list of recipients
            subject: Email subject
            cc: Carbon copy recipients (optional)

        Returns:
            self for method chaining
        """
        self.to = [to] if isinstance(to, str) else to
        self.cc = [] if cc is None else [cc] if isinstance(cc, str) else cc
        self.msg['To'] = ','.join(self.to)
        self.msg['Subject'] = Header(subject, 'utf-8').encode()
        if self.cc:
            self.msg['Cc'] = ','.join(self.cc)
        return self

    def add_content(self, content: str):
        """Add HTML paragraph content to email.

        Args:
            content: Text content to add

        Returns:
            self for method chaining
        """
        self.text += f'<p>{content}</p>'
        return self

    def add_title(self, title: str):
        """Add HTML title (h1) to email.

        Args:
            title: Title text to add

        Returns:
            self for method chaining
        """
        self.text += f'<h1>{title}</h1>'
        return self

    def add_href(self, href: str, title: Optional[str] = None):
        """Add HTML hyperlink to email.

        Args:
            href: URL to link to
            title: Optional title for the link, defaults to href if not provided

        Returns:
            self for method chaining
        """
        safe_title = title if title else href
        self.text += f'<p><a href="{href}">{safe_title}</a></p>'
        return self

    def add_table(self, df: Union[pd.DataFrame, pl.DataFrame]):
        """Add HTML table from DataFrame to email.

        Args:
            df: pandas or polars DataFrame to convert to HTML table

        Returns:
            self for method chaining

        Raises:
            ValueError: If DataFrame is empty
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

    def add_images(self, imgs: List[PathLike]):
        """Add inline images to email.

        Args:
            imgs: List of image file paths to attach

        Returns:
            self for method chaining

        Raises:
            FileNotFoundError: If any image file cannot be opened
        """
        for img in imgs:
            try:
                with open(img, 'rb') as f:
                    msg_image = MIMEImage(f.read())
                    cid = str(self.image_cnt)
                    msg_image.add_header('Content-ID', f'<{cid}>')
                    self.msg.attach(msg_image)
                    self.text += f'<p><img src="cid:{cid}"></p>'
                    self.image_cnt += 1
            except FileNotFoundError as e:
                raise FileNotFoundError(f"Could not open image file {img}: {e}") from e
        return self

    def add_attachments(self, files: List[PathLike]):
        """Add file attachments to email.

        Args:
            files: List of file paths to attach

        Returns:
            self for method chaining

        Raises:
            FileNotFoundError: If any file cannot be opened
        """
        for file in files:
            try:
                with open(file, 'rb') as f:
                    mime = MIMEBase('application', 'octet-stream')
                    mime.set_payload(f.read())
                    encoders.encode_base64(mime)

                    filename = PurePath(file).name if isinstance(file, str) else file.name
                    filename_header = (Header(filename, 'gbk').encode()
                                       if self._contain_zh(filename)
                                       else filename)

                    mime.add_header('Content-Disposition', 'attachment', filename=filename_header)
                    self.msg.attach(mime)
            except FileNotFoundError as e:
                raise FileNotFoundError(f"Could not open file {file}: {e}") from e
        return self

    def sendmail(self) -> bool:
        """Send the email with all added content.

        Returns:
            bool: True if sent successfully, False otherwise

        Raises:
            MailPlusError: If no recipients are specified
        """
        if not self.to and not self.cc:
            raise MailPlusError("No recipients specified")

        self.msg.attach(MIMEText(self.text, 'html', 'utf-8'))

        try:
            with smtplib.SMTP(self.config['server'], self.config['port']) as smtp:
                smtp.login(self.config['username'], self.config['password'])
                smtp.sendmail(
                    self.config['username'],
                    self.to + self.cc,
                    self.msg.as_string()
                )
            return True
        except (smtplib.SMTPException, ConnectionError) as e:
            print(f"Failed to send email: {e}")
            return False

    def set_server(self, cfg: dict[str, str]):
        """Update mail server configuration.

        Args:
            cfg: Mail configuration dictionary containing server, username, and password.
                 Must include all required config keys.

        Returns:
            self for method chaining

        Raises:
            MailPlusError: If required configuration is missing or invalid
        """
        # Validate configuration
        if not cfg or not all(key in cfg for key in self.REQUIRED_CONFIG):
            raise MailPlusError("Missing required mail configuration keys: server, username, password")

        try:
            # Update configuration
            self.config = {
                'server': cfg['server'],
                'port': int(cfg.get('port', self.DEFAULT_PORT)),
                'username': cfg['username'],
                'password': cfg['password']
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

            return self

        except (KeyError, ValueError) as e:
            raise MailPlusError(f"Invalid configuration: {str(e)}") from e

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
