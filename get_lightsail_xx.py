import boto3
import pandas as pd
from openpyxl.styles import Alignment  # 用于设置单元格对齐方式

# ========== 用户配置 ==========
AWS_ACCESS_KEY = r""
AWS_SECRET_KEY = r""
OUTPUT_FILE = "lightsail_instances.xlsx"

# 直接定义要扫描的 Lightsail 区域
LIGHTSAIL_REGIONS = [
    "us-west-2",
    "ap-northeast-1",
    "ap-northeast-2",
    "ap-southeast-1",
]
# =================================

# OS 翻译映射表（可按需扩展）
OS_MAP = {
    "amazon_linux": "Amazon Linux",
    "amazon_linux_2": "Amazon Linux 2",
    "ubuntu_18_04": "Ubuntu 18.04 LTS",
    "ubuntu_20_04": "Ubuntu 20.04 LTS",
    "ubuntu_22_04": "Ubuntu 22.04 LTS",
    "debian_10": "Debian 10",
    "debian_11": "Debian 11",
    "centos_7_1901_01": "CentOS 7",
    "windows_2016_base": "Windows Server 2016",
    "windows_2019_base": "Windows Server 2019",
    "windows_2022_base": "Windows Server 2022",
}


# 建立全局 session（不绑定区域）
session = boto3.session.Session(
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
)


def get_instances_in_region(region):
    """获取指定区域的所有 Lightsail 实例"""
    client = session.client("lightsail", region_name=region)
    instances = []

    try:
        resp = client.get_instances()
        instances.extend(resp["instances"])

        # 如果有分页
        while "nextPageToken" in resp:
            resp = client.get_instances(pageToken=resp["nextPageToken"])
            instances.extend(resp["instances"])
    except Exception as e:
        print(f"⚠️ 跳过区域 {region}：{str(e)}")
        return []

    return instances


def get_bundle_info(region):
    """获取套餐规格映射（bundleId -> vCPU/内存/磁盘）"""
    client = session.client("lightsail", region_name=region)
    try:
        bundles = client.get_bundles()["bundles"]
        return {b["bundleId"]: b for b in bundles}
    except Exception as e:
        print(f"⚠️ 获取区域 {region} bundle 信息失败：{str(e)}")
        return {}


def translate_os(blueprint_id):
    """翻译 blueprintId 到友好名称"""
    return OS_MAP.get(blueprint_id, blueprint_id)


def auto_adjust_excel_sheet(worksheet):
    """
    🔥 核心优化：自动调整 Excel 工作表的列宽、行高和对齐方式
    1. 列宽自适应内容长度
    2. 表头行高加大+居中对齐
    3. 内容行高优化+左对齐（IP/名称类）、居中对齐（数值类）
    """
    # 定义各列的「基础宽度」（根据字段类型调整，避免自适应过窄）
    column_base_width = {
        "A": 12,   # Region（区域代码，如 ap-northeast-1）
        "B": 8,    # Count（数值，较短）
        "C": 20,   # InstanceName（实例名称，可能较长）
        "D": 18,   # PublicIP（公网IP，固定长度）
        "E": 18,   # PrivateIP（内网IP，固定长度）
        "F": 10,   # State（状态，如 running/stopped）
        "G": 22,   # OS（操作系统名称，可能较长）
        "H": 6,    # vCPU（数值）
        "I": 10,   # RAM_GB（数值+单位）
        "J": 10    # Disk_GB（数值+单位）
    }

    # 1. 调整列宽：基础宽度 + 内容自适应（取最大值）
    for column in worksheet.columns:
        col_letter = column[0].column_letter  # 获取列字母（A、B、C...）
        max_length = column_base_width.get(col_letter, 15)  # 默认基础宽度15
        for cell in column:
            try:
                # 计算单元格内容长度（中文按2个字符计算，英文按1个）
                cell_length = sum(2 if ord(char) > 127 else 1 for char in str(cell.value))
                if cell_length > max_length:
                    max_length = cell_length
            except:
                pass
        # 最终列宽 = 最大长度 + 2（预留边距，避免内容溢出）
        adjusted_width = min(max_length + 2, 50)  # 限制最大宽度50，避免过宽
        worksheet.column_dimensions[col_letter].width = adjusted_width

    # 2. 调整表头（第1行）：行高加大+加粗+居中对齐
    worksheet.row_dimensions[1].height = 25  # 表头行高
    for cell in worksheet[1]:
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=False)
        # 表头加粗（可选，视觉更清晰）
        if cell.font.bold is None:
            cell.font = cell.font.copy(bold=True)

    # 3. 调整内容行：行高+对齐方式
    for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row):
        worksheet.row_dimensions[row[0].row].height = 20  # 内容行高
        for idx, cell in enumerate(row):
            # 数值类字段（Count、vCPU、RAM_GB、Disk_GB）居中对齐
            if idx in [1, 7, 8, 9]:  # 对应 B、H、I、J 列
                cell.alignment = Alignment(horizontal="center", vertical="center")
            # 其他字段（文本、IP）左对齐
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")

    # 4. 冻结首行（可选，滚动时表头固定）
    worksheet.freeze_panes = "A2"


def main():
    rows = []

    for region in LIGHTSAIL_REGIONS:
        instances = get_instances_in_region(region)
        bundle_map = get_bundle_info(region)

        if not instances:
            rows.append({
                "Region": region,
                "Count": 0,
                "InstanceName": "-",
                "PublicIP": "-",
                "PrivateIP": "-",
                "State": "-",
                "OS": "-",
                "vCPU": "-",
                "RAM_GB": "-",
                "Disk_GB": "-"
            })
            continue

        for inst in instances:
            bundle = bundle_map.get(inst["bundleId"], {})
            os_name = translate_os(inst.get("blueprintId", "N/A"))
            rows.append({
                "Region": region,
                "Count": len(instances),
                "InstanceName": inst["name"],
                "PublicIP": inst.get("publicIpAddress", "N/A"),
                "PrivateIP": inst.get("privateIpAddress", "N/A"),
                "State": inst["state"]["name"],
                "OS": os_name,
                "vCPU": bundle.get("cpuCount", "N/A"),
                "RAM_GB": bundle.get("ramSizeInGb", "N/A"),
                "Disk_GB": bundle.get("diskSizeInGb", "N/A")
            })

    # 转 DataFrame
    df = pd.DataFrame(rows)

    # 拆分数据
    df_cn = df[df["InstanceName"].str.startswith("rn-", na=False)]
    df_crn = df[df["InstanceName"].str.startswith("crn-", na=False)]
    df_other = df[~(df["InstanceName"].str.startswith("rn-", na=False) |
                    df["InstanceName"].str.startswith("crn-", na=False))]

    # 保存到多个 Sheet 并自动调整格式
    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        # 写入各Sheet
        df_cn.to_excel(writer, sheet_name="RN_Instances", index=False)
        df_crn.to_excel(writer, sheet_name="CRN_Instances", index=False)
        df_other.to_excel(writer, sheet_name="Other", index=False)

        # 对每个Sheet执行自动调整
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            auto_adjust_excel_sheet(worksheet)
            print(f"📋 已优化 Sheet「{sheet_name}」的格式")

    print(f"\n✅ 已导出 {OUTPUT_FILE}，包含 RN / CRN / Other 三个Sheet")
    print("✨ 表格已自动调整列宽、行高，无需手动拖拽")


if __name__ == "__main__":
    main()