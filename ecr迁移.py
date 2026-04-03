import boto3
import base64
import subprocess

# ================= 配置区 =================
SOURCE_AK = "源账号_ACCESS_KEY"
SOURCE_SK = "源账号_SECRET_KEY"
DEST_AK   = "目标账号_ACCESS_KEY"
DEST_SK   = "目标账号_SECRET_KEY"
REGION    = "ap-east-1"  # 替换为你实际的区域，如 us-east-1
# ==========================================

def get_ecr_auth(ak, sk):
    """获取 ECR 登录 Token 和 账号 ID"""
    session = boto3.Session(aws_access_key_id=ak, aws_secret_access_key=sk, region_name=REGION)
    ecr_client = session.client('ecr')
    sts_client = session.client('sts')
    
    # 获取 Token
    auth_data = ecr_client.get_authorization_token()['authorizationData'][0]
    token = base64.b64decode(auth_data['authorizationToken']).decode('utf-8').split(':')[1]
    
    # 获取账号 ID
    account_id = sts_client.get_caller_identity()['Account']
    
    return session, token, account_id

def run_migration():
    # 1. 初始化两个账号的连接
    print("正在验证账号权限并获取 Token...")
    src_session, src_token, src_id = get_ecr_auth(SOURCE_AK, SOURCE_SK)
    dst_session, dst_token, dst_id = get_ecr_auth(DEST_AK, DEST_SK)
    
    src_client = src_session.client('ecr')
    dst_client = dst_session.client('ecr')
    
    src_registry = f"{src_id}.dkr.ecr.{REGION}.amazonaws.com"
    dst_registry = f"{dst_id}.dkr.ecr.{REGION}.amazonaws.com"

    # 2. 遍历源账号所有存储库
    repos = []
    paginator = src_client.get_paginator('describe_repositories')
    for page in paginator.paginate():
        repos.extend(page['repositories'])

    print(f"共发现 {len(repos)} 个存储库，准备开始全量迁移...\n")

    for repo in repos:
        repo_name = repo['repositoryName']
        print(f">>> 正在处理存储库: {repo_name}")

        # 3. 检查并创建目标存储库
        try:
            dst_client.describe_repositories(repositoryNames=[repo_name])
        except dst_client.exceptions.RepositoryNotFoundException:
            print(f"    [!] 目标账号不存在该库，正在自动创建...")
            dst_client.create_repository(repositoryName=repo_name)

        # 4. 获取该库下所有镜像 Tag
        img_paginator = src_client.get_paginator('describe_images')
        for img_page in img_paginator.paginate(repositoryName=repo_name):
            for img_detail in img_page['imageDetails']:
                if 'imageTags' not in img_detail:
                    continue # 跳过没有标签的中间镜像
                
                for tag in img_detail['imageTags']:
                    src_url = f"docker://{src_registry}/{repo_name}:{tag}"
                    dst_url = f"docker://{dst_registry}/{repo_name}:{tag}"
                    
                    print(f"    -> 正在同步 Tag: {tag}")
                    
                    # 5. 调用 skopeo 执行跨账号传输
                    # --all 确保多架构镜像（如同时支持 arm 和 amd64）完整迁移
                    cmd = [
                        "skopeo", "copy", "--all",
                        "--src-creds", f"AWS:{src_token}",
                        "--dest-creds", f"AWS:{dst_token}",
                        src_url, dst_url
                    ]
                    
                    res = subprocess.run(cmd, capture_output=True, text=True)
                    if res.returncode != 0:
                        print(f"    [错误] 同步失败: {res.stderr}")
                    else:
                        print(f"    [成功] {tag} 已同步")

if __name__ == "__main__":
    # 确保本地已安装 skopeo
    try:
        subprocess.run(["skopeo", "--version"], check=True, capture_output=True)
        run_migration()
    except FileNotFoundError:
        print("错误：未在系统中找到 skopeo。请先安装：sudo apt install skopeo")