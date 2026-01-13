# lntools

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-0.1.1-orange)

**专为量化研究和运维设计的 Python 工具包**

</div>

---

## ✨ 主要特性

- 🕐 **时间工具** - 强大的日期时间处理和格式转换
- 📁 **文件系统** - 简洁的文件和目录操作 API
- 📧 **邮件发送** - 支持 HTML、图片、附件的链式邮件工具
- 🤖 **消息通知** - 飞书、微信 Webhook 通知集成
- ⚙️ **配置管理** - YAML / INI 配置文件管理
- 📝 **日志记录** - Rich 美化的日志输出
- 🎨 **人性化格式** - 路径、单位、时间等的友好显示
- 🔧 **类型定义** - 完整的类型提示支持
- ⚡ **性能计时** - 函数执行时间装饰器

---

## 📦 安装

### 从源码安装

```bash
git clone https://github.com/neolin0629/lntools.git
cd lntools
pip install .
```

### 依赖项

- `numpy` - 数值计算
- `pandas` - 数据分析
- `polars` - 高性能数据框架
- `rich` - 终端美化输出
- `pyyaml` - YAML 配置文件
- `pyarrow` - 高效数据存储
- `request` - HTTP 客户端库
- `tqdm` - 智能进度条库

---

## 🚀 快速开始

### 配置文件

lntools 使用配置文件 `~/.config/lntools/lntools.yaml` 来管理全局设置。首次运行时会自动创建。

配置文件示例：

```yaml
# 数据库配置（可选）
db:
  host: localhost
  port: 5432
  
# 邮件配置（可选）
mail:
  server: smtp.example.com
  port: 25
  username: your_email@example.com
  password: your_password

# 默认数据框架库
df_lib: pandas  # 可选: pandas, polars
```

---

## 📚 功能模块详细文档

### 4.1 ⏰ 时间工具 (timeutils)

提供丰富的日期时间处理功能，包括格式转换、日期计算等。

#### 核心转换函数

```python
from lntools.timeutils import to_timestamp
import pandas as pd

# 将任意日期类型转换为 pandas.Timestamp
dt = to_timestamp("2024-01-01")                # 字符串
dt = to_timestamp(20240101)                     # 整数 (YYYYMMDD)
dt = to_timestamp(1704067200.0)                 # Unix 时间戳
dt = to_timestamp("today")                      # 特殊关键字
dt = to_timestamp(pd.Timestamp("2024-01-01"))  # Timestamp 对象

# 仅保留日期部分（归一化到午夜）
dt = to_timestamp("2024-01-01 15:30:00", date_only=True)  # 2024-01-01 00:00:00
```

#### 日期计算函数

```python
from lntools.timeutils import adjust, diff, get_range, day_of_week

# 日期调整（加减天数）
tomorrow = adjust("2024-01-01", 1)      # 2024-01-02
yesterday = adjust("2024-01-01", -1)    # 2023-12-31
today = adjust("today", 0)              # 今天

# 仅保留日期部分
date_only = adjust("2024-01-01 15:30:00", 0, date_only=True)

# 计算日期差（天数）
days = diff("2024-01-01", "2024-02-01")  # 31

# 生成日期序列（包含起止日期）
dates = get_range("2024-01-01", "2024-01-31")  # 返回 31 个 Timestamp 对象的列表
dates = get_range("2024-01-01", None)           # 从 2024-01-01 到今天
dates = get_range(None, "2024-12-31")           # 从 2010-01-01 到 2024-12-31（默认起始）

# 获取星期几（1=周一，7=周日）
weekday = day_of_week("2024-01-01")  # 1（周一）
weekday = day_of_week("today")       # 当前是星期几
```

#### 格式转换函数

```python
from lntools.timeutils import dt2str, ts2str
from datetime import datetime
import pandas as pd

# 可用的格式快捷方式
print(SHORTCUTS)
# {
#     "standard": '%Y/%m/%d',              # 2024/01/01
#     "compact": '%Y%m%d',                 # 20240101
#     "wide": '%Y-%m-%d',                  # 2024-01-01
#     "time": '%H:%M:%S',                  # 14:30:00
#     "datetime": '%Y/%m/%d %H:%M:%S'      # 2024/01/01 14:30:00
# }

# datetime/Timestamp -> 字符串
date_str = dt2str(datetime(2024, 1, 1), "wide")       # '2024-01-01'
date_str = dt2str(datetime(2024, 1, 1), "compact")    # '20240101'
date_str = dt2str(datetime(2024, 1, 1), "standard")   # '2024/01/01'
date_str = dt2str(datetime.now(), "datetime")         # '2024/01/01 14:30:00'

# 支持 pandas.Timestamp
date_str = dt2str(pd.Timestamp("2024-01-01"), "wide")  # '2024-01-01'

# Unix 时间戳 -> 字符串
date_str = ts2str(1704067200, "wide")      # '2024-01-01'
date_str = ts2str(1704067200.0, "compact") # '20240101'

# 自定义格式字符串（strftime 格式）
date_str = dt2str(datetime.now(), "%Y年%m月%d日")  # '2024年01月01日'
```

#### 类型检查工具

```python
from lntools.timeutils import is_date_pd, is_date_pl
import pandas as pd
import polars as pl

# 检查 Pandas Series 是否为日期类型
df_pd = pd.DataFrame({"dt": pd.date_range("2024-01-01", periods=10)})
is_date_pd(df_pd["dt"])  # True

# 检查 Polars DataFrame/Series 列是否为日期类型
df_pl = pl.DataFrame({"dt": pl.date_range(pl.date(2024, 1, 1), pl.date(2024, 1, 10), "1d")})
is_date_pl(df_pl, "dt")  # True
is_date_pl(df_pl["dt"])  # True (传入 Series)
```

#### 性能计时装饰器

```python
from lntools.timeutils import timer
import time

# 基础用法：函数耗时超过阈值时打印
@timer(msg="Data Processing", threshold=3.0)
def process_data():
    time.sleep(5)
    return "done"

process_data()  # 输出: [Data Processing] 耗时: 5.00s

# 自定义报告函数和计时方式
import logging
logger = logging.getLogger(__name__)

@timer(
    msg="Heavy Computation",
    reporter=logger.info,           # 使用 logger 输出
    threshold=1.0,
    process_time=True               # 使用 CPU 时间而非墙钟时间
)
def compute():
    # 复杂计算逻辑
    pass
```

---

### 4.2 📁 文件系统 (filesystem)

提供简洁易用的文件和目录操作 API。

#### 路径操作

```python
from lntools import is_dir, is_file, handle_path, make_dirs

# 检查路径类型
is_dir("/path/to/directory")   # True/False
is_file("/path/to/file.txt")   # True/False

# 处理路径（展开用户目录，创建父目录）
path = handle_path("~/data/output.csv")

# 创建目录
make_dirs("/path/to/new/directory")
```

#### 文件操作

```python
from lntools import move, rename, remove, file_time
from pathlib import Path
import shutil

# 使用 lntools 函数
move("source.txt", "destination/", keep_old=True)   # 复制
move("source.txt", "destination/", keep_old=False)  # 移动
rename("old_name.txt", "new_name.txt")              # 重命名
remove("file.txt")                                  # 删除文件
remove("directory/")                                # 删除目录

# 获取文件时间
mtime = file_time("file.txt", method='m')  # 修改时间
atime = file_time("file.txt", method='a')  # 访问时间
ctime = file_time("file.txt", method='c')  # 创建时间
```

#### 目录遍历

```python
from lntools import get_all, get_files, get_dirs
from pathlib import Path

# 获取所有路径
all_paths = get_all("/path/to/directory")

# 仅获取文件
files = get_files("/path/to/directory")

# 仅获取目录
dirs = get_dirs("/path/to/directory")
```

#### 文件读取

```python
from lntools import read_file, read_directory
import pandas as pd

# 读取单个文件（自动识别格式）
df = read_file("data.csv", df_lib="polars")
df = read_file("data.parquet", df_lib="pandas")
df = read_file("data.xlsx", df_lib="polars")

# 读取目录中的所有文件
df = read_directory(
    path="/path/to/data",
    df_lib="polars",
    threads=10
)

# 按日期范围读取（使用自然日期）
df = read_directory(
    path="/path/to/data",
    sdt="2024-01-01",
    edt="2024-01-31",
    file_pattern="{date}.csv",
    date_format="%Y-%m-%d",
    engine="polars"
)

# 按交易日读取（提供自定义日期列表）
trading_days = [
    pd.Timestamp("2024-01-02"),
    pd.Timestamp("2024-01-03"),
    pd.Timestamp("2024-01-04")
]
df = read_directory(
    path="/path/to/data",
    sdt="2024-01-01",
    edt="2024-01-31",
    trading_dates=trading_days,
    file_pattern="{date}.parquet",
    date_format="%Y%m%d",
    engine="polars",
    threads=20
)

# 使用自定义读取函数
def custom_reader(path):
    return pl.read_csv(path, separator="|", ignore_errors=True)

df = read_directory(
    path="/path/to/data",
    reader=custom_reader,
    threads=10
)
```

---

### 4.3 📧 邮件发送 (mail)

支持 HTML、图片、附件和 DataFrame 表格的企业级链式邮件工具，内置 TLS/SSL 加密、自动重试、详细日志和完整错误处理。

#### 配置要求

在 `~/.config/lntools/lntools.yaml` 中配置邮件服务器：

```yaml
mail:
  server: smtp.example.com      # SMTP 服务器地址
  port: 25                       # 端口 (可选，TLS 默认 465，非 TLS 默认 25)
  username: your_email@example.com
  password: your_password
  use_tls: false                 # 是否启用 TLS/SSL 加密 (可选，默认 false)
```

**TLS/SSL 支持：**
- `use_tls: true` - 使用 SMTP_SSL（端口 465），适用于 Gmail、QQ 邮箱等
- `use_tls: false` - 使用标准 SMTP（端口 25），适用于企业内网邮件服务器

#### 基础用法：链式调用

```python
from lntools import MailPlus
import pandas as pd

# 1. 创建邮件对象（自动读取全局配置）
mail = MailPlus()

# 2. 链式调用发送邮件
success = (
    mail.newemail(
        to="recipient@example.com",           # 收件人（支持列表）
        subject="数据报告",                    # 邮件主题
        cc=["cc1@example.com", "cc2@example.com"]  # 抄送（可选）
    )
    .add_title("每日数据报告")                # 添加 H1 标题
    .add_content("以下是今日的数据分析结果：")  # 添加段落文本
    .add_table(df)                           # 添加 DataFrame 表格（pandas 或 polars）
    .add_images(["chart1.png", "chart2.png"])  # 添加内联图片
    .add_href("https://example.com", "查看详情")  # 添加超链接
    .add_attachments(["report.pdf", "data.xlsx"])  # 添加附件（任意文件类型）
    .sendmail(retries=3, retry_delay=2.0)    # 发送邮件（支持自动重试）
)

if success:
    print("邮件发送成功")
else:
    print("邮件发送失败，请检查日志")
```

#### 高级功能示例

##### 1. 自定义邮件配置（不使用全局配置）

```python
# 临时使用不同的邮件服务器
custom_config = {
    "server": "smtp.gmail.com",
    "port": 465,
    "username": "your_gmail@gmail.com",
    "password": "your_app_password",
    "use_tls": "true"  # Gmail 需要 TLS
}

mail = MailPlus(cfg=custom_config)
```

##### 2. 更换邮件服务器

```python
# 在运行时切换到不同的邮件服务器
new_server = {
    "server": "smtp.163.com",
    "port": 25,
    "username": "work_email@163.com",
    "password": "work_password",
    "use_tls": "false"
}

mail.set_server(new_server)
```

##### 3. 发送带 Polars DataFrame 的邮件

```python
import polars as pl

# Polars DataFrame 自动转换为 HTML 表格
df_pl = pl.DataFrame({
    "日期": ["2024-01-01", "2024-01-02"],
    "收益率": [0.025, -0.013],
    "夏普比率": [1.85, 1.72]
})

mail.newemail("analyst@example.com", "Polars 数据报告")
mail.add_table(df_pl).sendmail()
```

##### 4. 使用 Path 对象处理文件

```python
from pathlib import Path

# 支持 Path 对象和字符串路径
output_dir = Path("./output")
images = [output_dir / "fig1.png", output_dir / "fig2.png"]
attachments = [output_dir / "report.xlsx"]

mail.newemail("team@example.com", "项目报告")
mail.add_images(images).add_attachments(attachments).sendmail()
```

##### 5. 自定义重试策略

```python
# 增加重试次数和延迟，适用于网络不稳定环境
success = (
    mail.newemail("client@example.com", "重要通知")
    .add_content("这是一封重要的邮件，确保送达")
    .sendmail(retries=5, retry_delay=5.0)  # 最多重试 5 次，每次延迟 5 秒
)
```

##### 6. 错误处理最佳实践

```python
from lntools.mail.mailplus import MailPlusError

try:
    mail = MailPlus()
    success = (
        mail.newemail("recipient@example.com", "测试邮件")
        .add_content("测试内容")
        .add_attachments(["report.pdf"])  # 如果文件不存在，会抛出 FileNotFoundError
        .sendmail()
    )
    if not success:
        # 发送失败（认证错误、连接超时等）
        print("邮件发送失败，请检查日志获取详细错误信息")
except FileNotFoundError as e:
    print(f"附件文件未找到: {e}")
except MailPlusError as e:
    print(f"邮件配置错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

---

### 4.4 🤖 消息通知 (bot)

飞书 Webhook 通知集成，支持文本、富文本（Post）和交互式卡片消息。

#### FeishuNotifier 类

```python
from lntools.bot.notify import FeishuNotifier

# 创建通知器实例
webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/xxxxx"
notifier = FeishuNotifier(
    webhook=webhook_url,
    timeout=10,      # 请求超时时间（秒）
    retries=3        # 失败重试次数
)

# 1. 发送纯文本消息
notifier.send_text("任务执行完成！")

# 2. 发送交互式卡片
notifier.send_card(
    title="系统监控告警",
    content="**级别**: P0\n**详情**: 数据库连接池占满\n<at id=all></at>",
    theme="red"  # 可选: blue, green, yellow, orange, red, purple 等
)

# 3. 发送富文本（Post）消息
post_content = {
    "zh_cn": {
        "title": "项目更新通知",
        "content": [
            [
                {"tag": "text", "text": "项目进度："},
                {"tag": "a", "text": "查看详情", "href": "https://example.com"},
            ],
            [{"tag": "text", "text": "当前状态："}],
            [{"tag": "text", "text": "✅ 任务1已完成\n⏳ 任务2进行中"}],
        ],
    }
}
notifier.send("post", post_content)
```

#### 卡片主题颜色

可用的主题颜色包括：
- `blue` - 蓝色（默认）
- `wathet` - 浅蓝
- `turquoise` - 青绿
- `green` - 绿色
- `yellow` - 黄色
- `orange` - 橙色
- `red` - 红色
- `carmine` - 洋红
- `violet` - 紫罗兰
- `purple` - 紫色
- `indigo` - 靛蓝
- `grey` - 灰色

#### WeComNotifier 类

企业微信机器人通知工具，支持文本、Markdown、图片、图文、文件和模板卡片消息。

```python
from lntools.bot.notify import WeComNotifier

# 创建通知器实例
webhook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxx"
notifier = WeComNotifier(
    webhook=webhook_url,
    timeout=10,
    retries=3
)

# 1. 发送文本消息
notifier.send_text("任务执行完成！")

# 2. 文本消息 + @提及
notifier.send_text(
    "紧急告警：系统异常",
    mentioned_list=["@all"],  # @所有人
    mentioned_mobile_list=["13812345678"]  # @指定手机号
)

# 3. 发送 Markdown 消息
notifier.send_markdown("""
## 日报总结
**日期**: 2026-01-13
**状态**: <font color="info">正常</font>
**详情**:
- 任务1：已完成
- 任务2：进行中
> 查看[详细报告](https://example.com)
""")

# 4. 发送图文消息
articles = [
    {
        "title": "市场日报",
        "description": "2026-01-13市场摘要",
        "url": "https://example.com/report",
        "picurl": "https://example.com/cover.jpg"
    }
]
notifier.send_news(articles)

# 5. 发送图片消息
import base64
import hashlib

with open("chart.png", "rb") as f:
    img_data = f.read()
img_base64 = base64.b64encode(img_data).decode()
img_md5 = hashlib.md5(img_data).hexdigest()
notifier.send_image(img_base64, img_md5)

# 6. 发送模板卡片（简化版）
notifier.send_text_notice_card(
    title="任务完成通知",
    description="数据处理任务已完成",
    emphasis_title="100%",
    emphasis_desc="完成率",
    url="https://example.com/details",
    fields=[
        {"keyname": "记录数", "value": "1,500,000"},
        {"keyname": "耗时", "value": "5分32秒"}
    ]
)

# 7. 发送模板卡片（完整版）
card_data = {
    "source": {
        "icon_url": "https://example.com/icon.png",
        "desc": "数据管道"
    },
    "main_title": {
        "title": "任务完成",
        "desc": "数据处理成功完成"
    },
    "emphasis_content": {
        "title": "100%",
        "desc": "完成率"
    },
    "sub_title_text": "2026-01-13 10:00:00",
    "horizontal_content_list": [
        {"keyname": "记录数", "value": "1,500,000"},
        {"keyname": "耗时", "value": "5分32秒"}
    ],
    "card_action": {
        "type": 1,
        "url": "https://example.com/details"
    }
}
notifier.send_template_card("text_notice", card_data)
```

---

### 4.5 ⚙️ 配置管理 (config)

YAML 和 INI 配置文件的读写管理，支持类型安全和错误处理。

#### 配置文件位置

lntools 的全局配置文件位于：
- **Linux/macOS**: `~/.config/lntools/lntools.yaml`
- **Windows**: `C:\Users\<username>\.config\lntools\lntools.yaml`

首次导入时自动创建，可手动编辑或通过 API 管理。

#### 全局配置对象

```python
from lntools import CONFIG

# 访问配置
print(CONFIG.df_lib)      # 'polars'
print(CONFIG.mail)        # 邮件配置字典 {'server': 'smtp.example.com', ...}
print(CONFIG.db)          # 数据库配置字典 {'host': 'localhost', ...}
```

#### YAML 文件操作

```python
from lntools import read_yaml, write_yaml, read_pkg_yaml

# 1. 读取项目配置文件（外部文件）
config = read_yaml("./config/database.yaml")
db_host = config["database"]["host"]
db_port = config["database"]["port"]

# 2. 读取用户配置（支持路径展开）
user_config = read_yaml("~/my_project/settings.yaml")

# 3. 写入配置文件
output_config = {
    "model": {
        "name": "factor_model_v1",
        "params": {"learning_rate": 0.01, "epochs": 100}
    },
    "data": {
        "source": "clickhouse",
        "tables": ["market_data", "factor_values"]
    }
}
write_yaml("./config/model_config.yaml", output_config)

# 4. 读取包内资源文件（适用于库开发者）
default_config = read_pkg_yaml("defaults.yaml", package="lntools")

# 5. 错误处理示例
from pathlib import Path

config_path = "./config/optional.yaml"
if Path(config_path).exists():
    try:
        config = read_yaml(config_path)
    except ValueError as e:
        print(f"配置文件格式错误: {e}")
        config = {}
else:
    print("配置文件不存在，使用默认值")
    config = {"default": True}
```

#### INI 文件操作

```python
from lntools import read_ini, write_ini, read_pkg_ini
from configparser import ConfigParser

# 1. 读取数据库配置（外部文件）
config = read_ini("./config/database.ini")
host = config["database"]["host"]
port = config.getint("database", "port")  # 自动类型转换

# 2. 读取多个配置段
api_config = read_ini("/etc/myapp/api.ini")
for section in api_config.sections():
    print(f"[{section}]")
    for key, value in api_config.items(section):
        print(f"  {key} = {value}")

# 3. 修改并保存配置
config = read_ini("settings.ini")
config["server"]["timeout"] = "30"
config["logging"]["level"] = "DEBUG"
write_ini("settings_updated.ini", config)

# 4. 创建新的 INI 文件
new_config = ConfigParser()
new_config["DEFAULT"] = {"debug": "false", "log_level": "info"}
new_config["database"] = {
    "host": "localhost",
    "port": "5432",
    "database": "trading_db"
}
new_config["cache"] = {"enabled": "true", "ttl": "3600"}
write_ini("./config/prod.ini", new_config)

# 5. 读取包内资源文件（适用于库开发者）
pkg_config = read_pkg_ini("defaults.ini", package="lntools")
```

#### 实际应用示例

```python
from lntools import read_yaml, read_ini, CONFIG
from pathlib import Path

# 场景1: 多环境配置管理
env = "production"  # 可从环境变量读取
config_file = f"./config/{env}.yaml"
if Path(config_file).exists():
    app_config = read_yaml(config_file)
else:
    raise FileNotFoundError(f"环境配置文件不存在: {config_file}")

# 场景2: 合并默认配置和用户配置
default_cfg = {"timeout": 10, "retries": 3, "log_level": "INFO"}
user_cfg_path = Path.home() / ".myapp" / "config.yaml"
if user_cfg_path.exists():
    user_cfg = read_yaml(str(user_cfg_path))
    config = {**default_cfg, **user_cfg}  # 用户配置覆盖默认值
else:
    config = default_cfg

# 场景3: 读取数据库连接配置
db_config = read_ini("./config/database.ini")
connection_string = (
    f"clickhouse://{db_config['clickhouse']['user']}:"
    f"{db_config['clickhouse']['password']}@"
    f"{db_config['clickhouse']['host']}:"
    f"{db_config['clickhouse']['port']}/"
    f"{db_config['clickhouse']['database']}"
)
```

---

### 4.6 📝 日志记录 (log)

基于 Rich 的美化日志输出工具，支持配置化管理和动态handler控制。

#### 基础用法

```python
from lntools import Logger

# 简单控制台日志
log = Logger("my_module")
log.info("Application started")

# 控制台 + 文件输出
log = Logger(
    module_name="my_module",
    output_method=["console", "file"],
    file="app.log",
    level="info",
    rich=True
)

# 所有日志级别
log.debug("Debug info")
log.info("Normal message")
log.warning("Warning message")
log.error("Error occurred")
log.critical("System failure")

# 异常日志（自动记录traceback）
try:
    risky_operation()
except Exception:
    log.exception("Operation failed")

# 运行时调整级别
log.set_level("debug")
```

#### 统一配置（推荐）

使用 `LogConfig` 实现项目级别的配置复用：

```python
from lntools import Logger, LogConfig
from pathlib import Path

# 定义项目统一配置
PROJECT_CONFIG = LogConfig(
    datetime_format='%Y-%m-%d %H:%M:%S.%f',
    file_format='[%(asctime)s][%(name)s][%(levelname)s] %(message)s',
    default_level='info',
    default_rich=True,
    default_log_dir=Path('./logs')
)

# 各模块使用相同配置
strategy_log = Logger("strategy", config=PROJECT_CONFIG)
execution_log = Logger("execution", config=PROJECT_CONFIG)
risk_log = Logger("risk", config=PROJECT_CONFIG)
```

#### 动态Handler管理

```python
import logging
from logging.handlers import SysLogHandler

log = Logger("app", output_method="console")

# 运行时添加自定义handler
syslog = SysLogHandler(address='/dev/log')
log.add_handler("syslog", syslog)

# 移除handler
log.remove_handler("console")

# 查看所有handler
print(log.get_handlers())  # {'syslog': <SysLogHandler>}
```

#### 高性能场景

```python
# 高频交易/数据处理：禁用rich格式提升性能
HFT_CONFIG = LogConfig(
    default_rich=False,          # 关键：禁用rich降低overhead
    default_level='warning',     # 只记录重要信息
    console_format='%(asctime)s|%(levelname)s|%(message)s'
)

log = Logger("hft_engine", config=HFT_CONFIG)
```

---

### 4.7 🖥️ 命令行工具 (CLI)

简化的命令行参数解析工具，基于 argparse 封装，提供更简洁的 API 和字典返回值。

#### 基础用法

```python
from lntools.utils.cli import CLI

# 创建 CLI 对象
cli = CLI()

# 添加参数
cli.add("--name", "-n", type=str, required=True, help="用户名")
cli.add("--age", "-a", type=int, default=0, help="年龄")
cli.add("--verbose", "-v", action="store_true", help="详细输出")
cli.add("--output", "-o", type=str, choices=["json", "csv"], help="输出格式")

# 解析参数并返回字典
args = cli.get()

print(f"姓名: {args['name']}")
print(f"年龄: {args['age']}")
print(f"详细模式: {args['verbose']}")
print(f"输出格式: {args.get('output', 'default')}")
```

#### Action 参数类型

`action` 参数定义了参数的行为模式：

```python
from lntools.utils.cli import CLI

cli = CLI()

# store: 存储输入值（默认行为）
cli.add("--config", action="store", help="配置文件路径")

# store_true/store_false: 布尔开关
cli.add("--verbose", action="store_true", help="启用详细输出")
cli.add("--quiet", action="store_false", help="禁用输出")

# store_const: 存储常量值
cli.add("--mode", action="store_const", const="production", help="生产模式")

# append: 多次指定累积到列表
cli.add("--include", action="append", help="包含的模块（可多次指定）")
# 使用: python script.py --include math --include numpy --include pandas
# 结果: args['include'] = ['math', 'numpy', 'pandas']

# append_const: 追加常量到列表
cli.add("--with-cache", action="append_const", const="cache", dest="features")
cli.add("--with-log", action="append_const", const="logging", dest="features")
# 使用: python script.py --with-cache --with-log
# 结果: args['features'] = ['cache', 'logging']

# count: 计数（常用于 -vvv 形式）
cli.add("-v", "--verbose", action="count", default=0, help="详细级别")
# 使用: python script.py -vvv
# 结果: args['verbose'] = 3

args = cli.get()
```

#### Nargs 参数 - 多值参数

`nargs` 参数控制参数接受的值的数量：

```python
from lntools.utils.cli import CLI

cli = CLI()

# nargs='?': 可选单个值
cli.add("--log", nargs="?", const="INFO", default="WARNING", help="日志级别")
# 使用: python script.py --log DEBUG  → args['log'] = 'DEBUG'
# 使用: python script.py --log        → args['log'] = 'INFO' (const)
# 使用: python script.py              → args['log'] = 'WARNING' (default)

# nargs='*': 零个或多个值（结果为列表）
cli.add("--files", nargs="*", help="要处理的文件列表")
# 使用: python script.py --files a.csv b.csv c.csv
# 结果: args['files'] = ['a.csv', 'b.csv', 'c.csv']

# nargs='+': 一个或多个值（至少一个）
cli.add("--symbols", nargs="+", required=True, help="股票代码")
# 使用: python script.py --symbols AAPL GOOGL MSFT
# 结果: args['symbols'] = ['AAPL', 'GOOGL', 'MSFT']

# nargs=<整数>: 指定数量的值
cli.add("--point", nargs=2, type=float, help="坐标点 (x, y)")
# 使用: python script.py --point 10.5 20.3
# 结果: args['point'] = [10.5, 20.3]

args = cli.get()
```

#### 处理未知参数

使用 `allow_unknown=True` 可以接受未定义的参数而不报错：

```python
from lntools.utils.cli import CLI

cli = CLI()
cli.add("--known", type=str, help="已知参数")

# 允许未知参数（适用于插件系统或动态参数）
args = cli.get(allow_unknown=True)

print(f"已知参数: {args['known']}")
print(f"未知参数: {args['unknown']}")
# 使用: python script.py --known value --unknown1 abc --unknown2 xyz
# 结果: 
#   args['known'] = 'value'
#   args['unknown'] = ['--unknown1', 'abc', '--unknown2', 'xyz']
```

#### 错误处理

```python
from lntools.utils.cli import CLI, CLIError

cli = CLI()

try:
    cli.add("--port", type=int, help="端口号")
    args = cli.get()
    
    # 自定义验证
    if args.get("port") and not (1024 <= args["port"] <= 65535):
        raise CLIError("Port must be between 1024 and 65535", error_code=1)
        
except CLIError as e:
    print(f"CLI Error: {e}")  # 输出: [Error 1] Port must be between 1024 and 65535
    exit(e.error_code)
```

#### 实际应用示例

##### 1. 数据处理脚本

```python
from lntools.utils.cli import CLI
import polars as pl

cli = CLI()
cli.add("--input", "-i", nargs="+", required=True, help="输入文件路径")
cli.add("--output", "-o", type=str, required=True, help="输出文件路径")
cli.add("--format", choices=["csv", "parquet", "excel"], default="parquet")
cli.add("--threads", type=int, default=4, help="并行线程数")
cli.add("-v", "--verbose", action="count", default=0, help="详细级别")

args = cli.get()

# 根据详细级别设置日志
log_level = ["ERROR", "WARNING", "INFO", "DEBUG"][min(args['verbose'], 3)]
print(f"Log Level: {log_level}")

# 处理多个输入文件
for file_path in args['input']:
    df = pl.read_csv(file_path)
    # 处理数据...
    
print(f"Data saved to {args['output']} as {args['format']}")
```

##### 2. 回测工具

```python
from lntools.utils.cli import CLI
from lntools.timeutils import to_timestamp

cli = CLI()
cli.add("--symbols", nargs="+", required=True, help="股票代码列表")
cli.add("--start", type=str, required=True, help="开始日期 (YYYY-MM-DD)")
cli.add("--end", type=str, required=True, help="结束日期 (YYYY-MM-DD)")
cli.add("--initial-capital", type=float, default=100000.0, help="初始资金")
cli.add("--strategy", choices=["momentum", "mean_reversion"], required=True)
cli.add("--dry-run", action="store_true", help="仅模拟运行")
cli.add("--debug", action="store_true", help="调试模式")

args = cli.get()

# 日期验证
start_dt = to_timestamp(args['start'])
end_dt = to_timestamp(args['end'])

if start_dt >= end_dt:
    print("Error: Start date must be before end date")
    exit(1)

print(f"Backtesting {len(args['symbols'])} symbols from {args['start']} to {args['end']}")
print(f"Strategy: {args['strategy']}, Initial Capital: ${args['initial_capital']:,.2f}")

if args['dry_run']:
    print("[DRY RUN] No actual execution")
```

---

### 4.8 🎨 人性化格式化 (human)

提供各种数据的人性化显示格式，优化日志和 CLI 输出体验。

#### 基础格式化

```python
from lntools import path, unit, bytes_size, sec2str, datetime_str

# 路径 (自动简化为相对路径)
print(path("/home/user/project/data.csv"))

# 数值单位 (支持自动复数和自动缩放)
print(unit(5, "apple"))                     # '5 apples'
print(unit(1500, "user", auto_scale=True))  # '1.5K users'

# 字节大小
print(bytes_size(1024**3 * 1.5))            # '1.5 GB'

# 时间间隔 (支持微秒、自动省略次要单位)
print(sec2str(0.0005))      # '500µs'
print(sec2str(3665))        # '1 hr 1 min'

# 日期时间
print(datetime_str("today", "compact"))     # '20240112'
```

#### 集合展示

```python
from lntools import lists, ranges

# 列表预览 (支持截断显示)
items = [1, 2, 3, 4, 5]
print(lists(items, n=3))      # '[1, 2, 3] (& 2 others)'

# 日期范围描述
dates = ["2024-01-01", "2024-02-01"]
print(ranges(dates))          # '2024-01-01 ~ 2024-02-01 (32 days, 32D)'
```

#### 进度跟踪

```python
from lntools import track_simple, RichProgressManager
import time

# 1. 基础用法 (基于 tqdm，无依赖时回退到文本)
for i in track_simple(50, msg="Processing"):
    time.sleep(0.01)

# 2. 高级用法 (基于 Rich，支持嵌套与并发)
with RichProgressManager(remove_task_on_finish=True) as rpm:
    # 嵌套循环
    for epoch in rpm.track(3, msg="Epochs"):
        for batch in rpm.track(10, msg=f"Batch {epoch}"):
            time.sleep(0.05)

    # 并发支持：只需将 rpm 对象传递给子线程中调用 rpm.track() 即可
```

#### 刷新打印

```python
from lntools import fprint

# 在同一行刷新输出（简易进度显示）
for i in range(100):
    fprint(f"进度: {i+1}/100")
```

---

### 4.9 ⚡ 性能计时 (decorator)

函数执行时间装饰器。

```python
from lntools import timer

# 使用装饰器记录函数执行时间
@timer(msg="数据处理", threshold=3)
def process_data():
    # 如果执行时间超过 3 秒，将打印时间
    # 数据处理: 5.2s
    pass

# 自定义报告函数
@timer(
    msg="计算任务",
    reporter=lambda x: print(f"[INFO] {x}"),
    threshold=1,
    process_time=True  # 使用 CPU 时间而非墙钟时间
)
def compute():
    pass
```

---

### 4.10 🔤 类型定义 (typing)

完整的类型提示支持，提升代码可读性和 IDE 支持。

```python
from lntools import (
    ArrayLike,
    SeriesLike,
    DatetimeLike,
    DataFrameLike,
    PathLike
)

# 在函数签名中使用类型提示
def process_data(
    data: DataFrameLike,
    dates: DatetimeLike,
    path: PathLike
) -> SeriesLike:
    pass
```

#### 类型定义说明

- `ArrayLike` - 类数组类型（list, np.ndarray, pd.Series, pl.Series）
- `SeriesLike` - 序列类型（pd.Series, pl.Series）
- `DatetimeLike` - 日期时间类型（pd.Timestamp, int, float, str, datetime）
  - `int`: 例如 `20240101` (年月日)
  - `float`: 例如 `1704067200.0` (Unix 时间戳)
  - `str`: 例如 `"2024-01-01"` 或 `"today"`
- `DataFrameLike` - 数据框类型（pd.DataFrame, pl.DataFrame, pl.LazyFrame）
- `PathLike` - 路径类型（str, Path）

---

## 📂 项目结构

```
lntools/
├── lntools/
│   ├── __init__.py           # 主模块入口
│   ├── bot/                  # 消息通知模块
│   │   ├── __init__.py
│   │   └── notify.py         # 飞书通知
│   ├── config/               # 配置管理模块
│   │   ├── __init__.py
│   │   └── api.py            # 配置 API
│   ├── mail/                 # 邮件发送模块
│   │   ├── __init__.py
│   │   └── mailplus.py       # MailPlus 类
│   ├── timeutils/            # 时间工具模块
│   │   ├── __init__.py
│   │   └── api.py            # 时间处理 API
│   └── utils/                # 工具集模块
│       ├── __init__.py
│       ├── cli.py            # CLI 工具
│       ├── filesystem.py     # 文件系统操作
│       ├── human.py          # 人性化格式化
│       ├── log.py            # 日志工具
│       ├── misc.py           # 其他工具
│       └── typing.py         # 类型定义
├── tests/                    # 测试文件
├── pyproject.toml            # 安装配置
├── README.md                 # 项目文档
├── .flake8                   # Flake8 配置
└── .pylintrc                 # Pylint 配置
```

---

## 🛠️ 开发说明

### 安装开发依赖

```bash
pip install -e .[dev]
```

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试文件
python -m pytest tests/test_timeutils.py

# 查看测试覆盖率
python -m pytest --cov=lntools tests/
```

### 代码检查

```bash
# 使用 flake8 检查代码风格
flake8 lntools/

# 使用 pylint 进行代码质量检查
pylint lntools/

# 使用 mypy 进行类型检查
mypy lntools/
```

---

## 📄 许可证

本项目采用 [MIT License](https://opensource.org/licenses/MIT) 开源协议。

---

## 👤 作者信息

**Neo (Linnan)**

- 📧 Email: lnonly@163.com
- 🔗 GitHub: [@neolin0629](https://github.com/neolin0629)

---

## 🙏 致谢

感谢所有为 lntools 项目做出贡献的开发者！

---

<div align="center">

**如果这个项目对你有帮助，请给它一个 ⭐️！**

Made with ❤️ by Neo

</div>
