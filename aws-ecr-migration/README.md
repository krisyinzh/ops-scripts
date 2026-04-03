# AWS ECR 跨账号迁移工具

一个用于在 AWS 不同账号之间迁移 ECR（Elastic Container Registry）镜像的自动化脚本。

## 功能特性

✅ **全量迁移** - 自动扫描源账号的所有 ECR 仓库并迁移  
✅ **自动创建** - 目标账号中不存在的仓库会自动创建  
✅ **多架构支持** - 支持同时迁移 ARM64 和 AMD64 等多架构镜像  
✅ **完整标签** - 保留所有镜像标签和版本信息  
✅ **跨区域** - 支持任意 AWS 区域

## 前置要求

### 1. 安装依赖

**Python 包：**
```bash
pip install boto3
```

**系统工具（必须）：**
- Linux/Mac：`sudo apt install skopeo` 或 `brew install skopeo`
- Windows：需要在 WSL2 或 Docker 中运行，或使用 [skopeo for Windows](https://github.com/containers/skopeo/releases)

### 2. AWS 账号配置

需要为两个 AWS 账号（源账号和目标账号）分别创建 IAM 用户，并生成访问密钥。

#### 源账号 IAM 权限（只读）：
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:DescribeRepositories",
                "ecr:DescribeImages",
                "ecr:GetAuthorizationToken",
                "sts:GetCallerIdentity"
            ],
            "Resource": "*"
        }
    ]
}
```

#### 目标账号 IAM 权限（读写）：
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:CreateRepository",
                "ecr:DescribeRepositories",
                "ecr:BatchGetImage",
                "ecr:GetDownloadUrlForLayer",
                "ecr:PutImage",
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload",
                "ecr:GetAuthorizationToken",
                "sts:GetCallerIdentity"
            ],
            "Resource": "*"
        }
    ]
}
```

## 使用方法

### 第 1 步：配置脚本

编辑 `migrate_ecr_cross_account.py`，填入你的 AWS 访问密钥和区域：

```python
SOURCE_AK = ""      # 源账号 Access Key
SOURCE_SK = "..."  # 源账号 Secret Key
DEST_AK   = ""     # 目标账号 Access Key
DEST_SK   = "..."  # 目标账号 Secret Key
REGION    = "ap-east-1"                 # AWS 区域
```

### 第 2 步：运行脚本

```bash
python migrate_ecr_cross_account.py
```

### 第 3 步：等待完成

脚本会自动：
1. 连接两个账号并验证权限
2. 列出源账号的所有 ECR 仓库
3. 逐个仓库迁移所有镜像和标签
4. 在目标账号中自动创建不存在的仓库

## 执行示例

```
正在验证账号权限并获取 Token...
共发现 5 个存储库，准备开始全量迁移...

>>> 正在处理存储库: myapp-api
    [!] 目标账号不存在该库，正在自动创建...
    -> 正在同步 Tag: v1.0.0
    [成功] v1.0.0 已同步
    -> 正在同步 Tag: latest
    [成功] latest 已同步
>>> 正在处理存储库: myapp-web
    -> 正在同步 Tag: v2.1.0
    [成功] v2.1.0 已同步
```

## 常见问题

### Q: 如何获取 AWS Access Key？
A: 登录 AWS 控制台 → IAM → Users → 选择用户 → Security credentials → Create access key

### Q: 迁移需要多长时间？
A: 取决于镜像大小和网络速度。大型镜像可能需要几小时。

### Q: 可以只迁移特定仓库吗？
A: 可以。修改脚本，在循环中添加条件过滤：
```python
for repo in repos:
    if repo['repositoryName'] not in ['repo1', 'repo2']:
        continue  # 只迁移指定仓库
```

### Q: 如何处理迁移失败？
A: 脚本会输出具体错误信息。常见原因：
- IAM 权限不足 → 检查目标账号权限
- 网络问题 → 检查网络连接和 AWS 配额
- 磁盘空间不足 → 清理本地临时空间

### Q: 目标账号已有同名仓库怎么办？
A: 脚本会自动跳过创建步骤，直接开始迁移镜像到现有仓库。

## 安全建议

⚠️ **重要**：
- 不要把真实的 Access Key 提交到版本控制
- 使用 `.gitignore` 或环境变量存储敏感信息
- 建议使用临时 STS Token 而不是长期 Access Key
- 迁移完成后删除或禁用临时 IAM 用户

## 许可证

MIT
