# AWS Lightsail 实例导出工具

一键扫描 AWS Lightsail 服务器信息，自动整理成 Excel 报表的工具。支持多区域扫描、自动分类、格式优化。

## 🌟 功能特性

✅ **多区域扫描** - 同时扫描多个 AWS Lightsail 区域  
✅ **全量信息** - 获取实例名称、IP、状态、规格等完整信息  
✅ **自动分类** - 按实例名前缀（RN/CRN/其他）分类为不同 Sheet  
✅ **智能规格** - 自动获取 vCPU、内存、磁盘大小等规格信息  
✅ **OS 翻译** - 友好展示操作系统名称  
✅ **格式优化** - 自动调整列宽、行高、对齐方式，开箱即用  
✅ **表头冻结** - 冻结首行，滚动查看时表头保持可见  

## 📋 输出示例

生成的 Excel 包含以下列：

| 列 | 说明 | 示例 |
|----|------|------|
| Region | AWS 区域 | ap-northeast-1 |
| Count | 该区域实例数 | 5 |
| InstanceName | 实例名称 | rn-web-01 |
| PublicIP | 公网 IP | 203.0.113.42 |
| PrivateIP | 内网 IP | 172.26.1.23 |
| State | 实例状态 | running / stopped |
| OS | 操作系统 | Ubuntu 20.04 LTS |
| vCPU | CPU 核数 | 2 |
| RAM_GB | 内存大小 | 4 |
| Disk_GB | 磁盘大小 | 80 |

## 🔧 前置要求

### Python 环境
- Python 3.6+
- pip 包管理器

### 依赖包
```bash
pip install boto3 pandas openpyxl
```

### AWS 凭证
需要一个 AWS IAM 用户，具备以下权限：
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lightsail:GetInstances",
                "lightsail:GetBundles"
            ],
            "Resource": "*"
        }
    ]
}
```

获取凭证步骤：
1. 登录 AWS 控制台
2. IAM → Users → 选择用户
3. Security credentials → Create access key
4. 复制 Access Key ID 和 Secret Access Key

## 📖 使用方法

### 第 1 步：安装依赖

```bash
pip install boto3 pandas openpyxl
```

### 第 2 步：配置脚本

编辑 `export_lightsail_instances.py`，找到配置区域：

```python
# ========== 用户配置 ==========
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"        # 你的 Access Key
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG..."    # 你的 Secret Key
OUTPUT_FILE = "lightsail_instances.xlsx"       # 输出文件名

# 要扫描的 Lightsail 区域
LIGHTSAIL_REGIONS = [
    "us-west-2",
    "ap-northeast-1",
    "ap-northeast-2",
    "ap-southeast-1",
]
# =================================
```

**支持的 Lightsail 区域列表：**
```
us-east-1, us-east-2, us-west-1, us-west-2
ca-central-1
eu-west-1, eu-west-2, eu-west-3, eu-central-1
ap-northeast-1, ap-northeast-2
ap-southeast-1, ap-southeast-2
```

### 第 3 步：运行脚本

```bash
python export_lightsail_instances.py
```

### 第 4 步：查看结果

脚本会在当前目录生成 `lightsail_instances.xlsx`，包含 3 个 Sheet：

- **RN_Instances** - 名称以 `rn-` 开头的实例
- **CRN_Instances** - 名称以 `crn-` 开头的实例
- **Other** - 其他实例

## 📊 执行示例

```
⚠️ 跳过区域 us-west-1：An error occurred...
📋 已优化 Sheet「RN_Instances」的格式
📋 已优化 Sheet「CRN_Instances」的格式
📋 已优化 Sheet「Other」的格式

✅ 已导出 lightsail_instances.xlsx，包含 RN / CRN / Other 三个Sheet
✨ 表格已自动调整列宽、行高，无需手动拖拽
```

## 🔧 自定义配置

### 1. 修改扫描区域

只扫描特定区域，降低执行时间：

```python
LIGHTSAIL_REGIONS = [
    "ap-northeast-1",      # 日本
    "ap-southeast-1",      # 新加坡
]
```

### 2. 修改输出文件名

```python
OUTPUT_FILE = "server_inventory_2026_04_03.xlsx"
```

### 3. 扩展 OS 翻译表

如果有新的操作系统类型，在 `OS_MAP` 中添加：

```python
OS_MAP = {
    "amazon_linux": "Amazon Linux",
    "your_custom_os": "你的自定义 OS 名称",
    # ...
}
```

### 4. 自定义分类逻辑

默认按名称前缀（`rn-`、`crn-`）分类。如果需要自定义分类，修改 `main()` 函数中的分类逻辑：

```python
# 原逻辑
df_cn = df[df["InstanceName"].str.startswith("rn-", na=False)]
df_crn = df[df["InstanceName"].str.startswith("crn-", na=False)]

# 自定义示例：按区域分类
df_us = df[df["Region"].str.startswith("us-")]
df_ap = df[df["Region"].str.startswith("ap-")]
```

## 🛠️ 高级用法

### 修改 Excel 格式

#### 调整表头样式

在 `auto_adjust_excel_sheet()` 函数中修改：

```python
# 调整表头背景色
from openpyxl.styles import PatternFill
header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
for cell in worksheet[1]:
    cell.fill = header_fill
```

#### 添加冻结行和列

```python
# 冻结首行和首列
worksheet.freeze_panes = "B2"
```

#### 添加自动过滤

```python
worksheet.auto_filter.ref = f"A1:{chr(64+worksheet.max_column)}{worksheet.max_row}"
```

### 使用环境变量配置凭证

为了避免在代码中硬编码凭证，建议使用环境变量：

```python
import os

AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
```

然后在运行前设置环境变量：

**Linux/Mac：**
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
python export_lightsail_instances.py
```

**Windows (PowerShell)：**
```powershell
$env:AWS_ACCESS_KEY_ID="your-access-key"
$env:AWS_SECRET_ACCESS_KEY="your-secret-key"
python export_lightsail_instances.py
```

## 🆘 故障排除

### 问题 1：ImportError - 模块不存在
```
ModuleNotFoundError: No module named 'boto3'
```

**解决：**
```bash
pip install boto3 pandas openpyxl
```

### 问题 2：InvalidParameterException - 凭证错误
```
An error occurred (InvalidParameterException) when calling the GetInstances operation: ...
```

**原因：** AWS_ACCESS_KEY 或 AWS_SECRET_KEY 错误

**解决：**
- 检查凭证是否正确复制
- 检查凭证是否过期
- 确保 IAM 用户有 `lightsail:GetInstances` 权限

### 问题 3：操作超时或很慢

**原因：** 扫描的区域太多

**解决：** 只扫描实际需要的区域

```python
LIGHTSAIL_REGIONS = ["ap-northeast-1"]  # 只扫描日本区
```

### 问题 4：无法连接 AWS

**原因：** 网络问题或代理配置

**解决：**
- 检查网络连接
- 如果使用代理，配置 boto3：

```python
import boto3

session = boto3.session.Session(
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
)

# 使用代理
session.client("lightsail", region_name="ap-northeast-1", config=Config(
    proxies={"https": "http://proxy.example.com:8080"}
))
```

### 问题 5：Excel 打开时损坏

**原因：** openpyxl 版本不兼容

**解决：**
```bash
pip install --upgrade openpyxl
```

## 📝 输出字段说明

### 实例信息

| 字段 | 说明 | 可能值 |
|------|------|--------|
| **Region** | AWS 区域代码 | ap-northeast-1, us-west-2, ... |
| **Count** | 该区域的实例总数 | 1-99 |
| **InstanceName** | 实例名称（唯一） | rn-web-01, crn-db-02, ... |
| **PublicIP** | 公网 IP 地址 | 203.0.113.42, N/A |
| **PrivateIP** | 内网 IP 地址 | 172.26.1.23 |
| **State** | 实例状态 | running, stopped, starting, stopping |

### 规格信息

| 字段 | 说明 | 可能值 |
|------|------|--------|
| **OS** | 操作系统 | Ubuntu 20.04 LTS, CentOS 7, Windows Server 2019, ... |
| **vCPU** | 虚拟 CPU 核数 | 1, 2, 4, 8, ... |
| **RAM_GB** | 内存大小（GB） | 0.5, 1, 2, 4, 8, ... |
| **Disk_GB** | 磁盘大小（GB） | 20, 40, 80, 160, ... |

## 💡 最佳实践

### 1. 定期更新库存

设置定时任务，每周/每月运行一次脚本，生成库存报告：

**Windows 定时任务：**
```powershell
# 创建任务计划
$action = New-ScheduledTaskAction -Execute "python" -Argument "export_lightsail_instances.py"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 09:00AM
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "Lightsail Inventory"
```

**Linux cron：**
```bash
# 每周一上午 9 点执行
0 9 * * 1 cd /path/to/script && python export_lightsail_instances.py
```

### 2. 备份配置

把脚本和凭证配置分离，使用配置文件：

```python
# config.ini
[AWS]
access_key = AKIAIOSFODNN7EXAMPLE
secret_key = wJalrXUtnFEMI/K7MDENG...
regions = us-west-2, ap-northeast-1
output_file = lightsail_instances.xlsx
```

### 3. 日志记录

添加日志，便于调试：

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info(f"开始扫描区域 {region}")
logger.error(f"扫描失败：{error}")
```

### 4. 错误处理

添加更详细的错误处理：

```python
try:
    instances = get_instances_in_region(region)
except ClientError as e:
    if e.response['Error']['Code'] == 'AccessDenied':
        print(f"权限不足：{region}")
    else:
        print(f"未知错误：{e}")
```

## 🔒 安全建议

⚠️ **重要**：
- 不要把 AWS 凭证提交到版本控制
- 使用 `.gitignore` 排除敏感文件
- 建议使用临时 STS Token 而不是长期 Access Key
- 定期轮换 Access Key
- 使用 IAM 角色而不是根账户凭证

## 许可证

MIT

## 更新日志

### v1.0 (2026-04-03)
- 初始版本
- 支持多区域扫描
- 支持自动分类
- 支持格式优化
- 支持表头冻结
