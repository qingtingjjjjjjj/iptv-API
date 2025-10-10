import os, re, requests

# ✅ 文件名（始终在仓库根目录）
outfile = os.path.join(os.getcwd(), "cmlive.txt")

# ✅ 自动创建文件
if not os.path.exists(outfile):
    with open(outfile, "w", encoding="utf-8") as f:
        f.write("")
    print(f"🆕 已自动创建文件: {outfile}")
else:
    print(f"📄 已存在: {outfile}")

# ✅ 数据源
url = "https://raw.githubusercontent.com/q1017673817/iptvz/refs/heads/main/zubo_all.txt"

print("📡 正在下载直播源...")
try:
    res = requests.get(url, timeout=60)
    res.encoding = 'utf-8'
    lines = [i.strip() for i in res.text.splitlines() if i.strip()]
    print(f"✅ 成功下载源文件，共 {len(lines)} 行")
except Exception as e:
    print(f"❌ 下载失败: {e}")
    raise SystemExit(1)

groups = {}
current_group = None

# ✅ 省份关键词
provinces = ["北京","天津","河北","山西","内蒙古","辽宁","吉林","黑龙江","上海","江苏","浙江",
             "安徽","福建","江西","山东","河南","湖北","湖南","广东","广西","海南","重庆","四川",
             "贵州","云南","西藏","陕西","甘肃","青海","宁夏","新疆","港澳台"]

# ✅ 分类逻辑
for line in lines:
    if line.endswith(",#genre#"):
        current_group = line.replace(",#genre#", "")
        continue
    if "," not in line:
        continue
    name, link = line.split(",", 1)

    group = None
    if re.search(r"CCTV|CETV", name):
        group = "央视频道"
    elif "卫视" in name:
        group = "卫视频道"
    else:
        matched = False
        if current_group:
            for prov in provinces:
                if prov in current_group:
                    group = f"{prov}频道"
                    matched = True
                    break
        if not matched:
            for prov in provinces:
                if prov in name:
                    group = f"{prov}频道"
                    matched = True
                    break
        if not matched:
            group = "其他频道"

    groups.setdefault(group, []).append(f"{name},{link}")

# ✅ 写入文件
with open(outfile, "w", encoding="utf-8") as f:
    for g, items in groups.items():
        f.write(f"{g},#genre#\n")
        for i in items:
            f.write(i + "\n")
        f.write("\n")

total = sum(len(v) for v in groups.values())
print(f"✅ 已生成 {outfile}，共 {total} 条直播源")
