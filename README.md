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
- 🤖 **消息通知** - 飞书 Webhook 通知集成
- ⚙️ **配置管理** - YAML/INI 配置文件管理
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
pip install -e .
```

### 依赖项

- `numpy` - 数值计算
- `pandas` - 数据分析
- `polars` - 高性能数据框架
- `rich` - 终端美化输出
- `pyyaml` - YAML 配置文件
- `pyarrow` - 高效数据存储

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
df_lib: polars  # 可选: pandas, polars, numpy
```

---

## 📚 功能模块详细文档

### 4.1 ⏰ 时间工具 (timeutils)

提供丰富的日期时间处理功能，包括格式转换、日期计算等。

#### 基础函数

```python
from lntools import now, adjust, diff, get, day_of_week

# 获取当前时间
current = now()

# 日期调整（加减天数）
tomorrow = adjust("2024-01-01", 1)      # 2024-01-02（下一天）
yesterday = adjust("2024-01-01", -1)    # 2023-12-31（前一天）
today = adjust("today")                  # 今天

# 计算日期差（天数）
days = diff("2024-01-01", "2024-02-01")  # 返回 31（两个日期之间相差31天）

# 生成日期序列（包含起止日期）
dates = get("2024-01-01", "2024-01-31")  # 返回31个日期的列表（1月1日到1月31日）

# 获取星期几（1=周一，7=周日）
weekday = day_of_week("2024-01-01")
weekday = day_of_week("today")
```

#### 格式转换函数

```python
from lntools import str2dt, str2ts, ts2dt, ts2str, dt2str, dt2ts
from datetime import datetime

# 字符串 -> Timestamp
dt = str2dt("2024-01-01")
dt = str2dt("20240101")

# 字符串 -> Unix时间戳
timestamp = str2ts("2024-01-01")  # 1704067200.0

# Unix时间戳 -> datetime
dt = ts2dt(1704067200)

# Unix时间戳 -> 字符串
date_str = ts2str(1704067200, "wide")      # '2024-01-01'
date_str = ts2str(1704067200, "compact")   # '20240101'

# datetime -> Unix时间戳
timestamp = dt2ts(datetime(2024, 1, 1))

# datetime -> 字符串
date_str = dt2str(datetime(2024, 1, 1), "wide")  # '2024-01-01'
```

#### 日期格式快捷方式

```python
from lntools import SHORTCUTS

# 可用的格式快捷方式
# SHORTCUTS = {
#     "standard": '%Y/%m/%d',       # 2024/01/01
#     "compact": '%Y%m%d',          # 20240101
#     "wide": '%Y-%m-%d',           # 2024-01-01
#     "time": '%H:%M:%S',           # 14:30:00
#     "datetime": '%Y/%m/%d %H:%M:%S'  # 2024/01/01 14:30:00
# }

# 使用快捷方式
from lntools import dt2str
from datetime import datetime

dt2str(datetime.now(), "standard")  # '2024/01/01'
dt2str(datetime.now(), "compact")   # '20240101'
dt2str(datetime.now(), "datetime")  # '2024/01/01 14:30:00'
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

# 移动文件（默认复制）
move("source.txt", "destination/", keep_old=True)

# 移动文件（删除原文件）
move("source.txt", "destination/", keep_old=False)

# 重命名
rename("old_name.txt", "new_name.txt")

# 删除文件或目录
remove("file.txt")
remove("directory/")

# 获取文件时间
mtime = file_time("file.txt", method='m')  # 修改时间
atime = file_time("file.txt", method='a')  # 访问时间
ctime = file_time("file.txt", method='c')  # 创建时间
```

#### 目录遍历

```python
from lntools import get_all, get_files, get_dirs

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

# 按日期范围读取（需要文件名包含日期）
df = read_directory(
    path="/path/to/data",
    sdt="2024-01-01",
    edt="2024-01-31",
    file_pattern="{date}.csv",
    date_format="%Y-%m-%d",
    df_lib="polars"
)
```

#### File 类

```python
from lntools import File

# 创建 File 对象
f = File("path/to/data.csv")

# 属性
print(f.path)       # 绝对路径
print(f.directory)  # 父目录
print(f.basename)   # 文件名（含扩展名）
print(f.filename)   # 文件名（不含扩展名）
print(f.extension)  # 扩展名

# 读取文件
data = f.read(df_lib="polars")

# 文件操作
f.cp("backup/")     # 复制
f.mv("archive/")    # 移动
f.rm()              # 删除
```

#### Directory 类

```python
from lntools import Directory

# 创建 Directory 对象
d = Directory("/path/to/data", threads=10)

# 读取整个目录
data = d.read(lib="polars")

# 按日期范围读取
data = d.read(
    sdt="2024-01-01",
    edt="2024-01-31",
    file_pattern="{date}.parquet",
    date_format="%Y-%m-%d",
    use_tcal=True,
    lib="polars"
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

基于 Rich 的美化日志输出工具。

#### Logger 类的使用

```python
from lntools import Logger

# 创建日志记录器（仅控制台输出）
log = Logger("my_module")

# 同时输出到控制台和文件
log = Logger(
    "my_module",
    output_method=["console", "file"],
    file="app.log",
    level="info",
    rich=True
)

# 记录不同级别的日志
log.debug("调试信息")
log.info("普通信息")
log.warning("警告信息")
log.error("错误信息")

# 设置日志级别
log.set_level("debug")
```

#### 日志级别

- `debug` - 调试信息
- `info` - 普通信息（默认）
- `warning` - 警告信息
- `error` - 错误信息
- `critical` - 严重错误

---

### 4.7 🖥️ 命令行工具 (CLI)

简化的命令行参数解析工具。

```python
from lntools import CLI

# 创建 CLI 对象
cli = CLI()

# 添加参数
cli.add("--name", "-n", type=str, required=True, help="用户名")
cli.add("--age", "-a", type=int, default=0, help="年龄")
cli.add("--verbose", "-v", action="store_true", help="详细输出")
cli.add("--output", "-o", type=str, choices=["json", "csv"], help="输出格式")

# 解析参数
args = cli.get()

print(f"姓名: {args['name']}")
print(f"年龄: {args['age']}")
print(f"详细模式: {args['verbose']}")
```

---

### 4.8 🎨 人性化格式化 (human)

提供各种数据的人性化显示格式。

#### 路径格式化

```python
from lntools import path

# 显示相对路径（如果在当前目录下）
print(path("/home/user/project/data.csv"))
```

#### 单位格式化

```python
from lntools import unit

print(unit(1, "apple"))           # '1 apple'
print(unit(5, "apple"))           # '5 apples'
print(unit(3.141, "meter", 2))    # '3.14 meters'
```

#### 时间格式化

```python
from lntools import sec2str

print(sec2str(3.14))      # '3.1416s'
print(sec2str(65))        # '1 min 5 s'
print(sec2str(3661))      # '1 hours 1 min'
```

#### 列表格式化

```python
from lntools import lists

items = [1, 2, 3, 4, 5, 6, 7]
print(lists(items, n=3))  # '[1, 2, 3] (& 4 others)'
```

#### 日期范围格式化

```python
from lntools import ranges, get

dates = get("2024-01-01", "2024-01-31")
print(ranges(dates))
# 输出: '2024/01/01 ~ 2024/01/31 (31 days, 1M0D)'
```

#### 日期时间格式化

```python
from lntools import datetime

print(datetime("2024-01-01", "standard"))  # '2024/01/01'
print(datetime("2024-01-01", "compact"))   # '20240101'
print(datetime("2024-01-01", "wide"))      # '2024-01-01'
```

#### 进度跟踪

```python
from lntools import track

# 使用 Rich 进度条
for item in track(range(100), msg="处理中"):
    # 处理 item
    pass
```

#### 刷新打印

```python
from lntools import fprint

# 在同一行刷新输出（用于进度显示）
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
    PathLike,
    PolarsDate
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
- `PolarsDate` - Polars 日期类型（pl.Datetime, pl.Date, pl.Time）

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
│       ├── columns.py        # 列操作工具
│       ├── decorator.py      # 装饰器
│       ├── directory.py      # Directory 类
│       ├── file.py           # File 类
│       ├── filesystem.py     # 文件系统操作
│       ├── human.py          # 人性化格式化
│       ├── log.py            # 日志工具
│       ├── misc.py           # 其他工具
│       └── typing.py         # 类型定义
├── tests/                    # 测试文件
├── setup.py                  # 安装配置
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
