import os
import re
import asyncio
import aiohttp
from time import time

# 输出文件
outfile = os.path.join(os.getcwd(), "cmlive.txt")

# 创建或清空输出文件
with open(outfile, "w", encoding="utf-8") as f:
    f.write("")
print(f"📄 输出文件: {outfile}")

# 数据源 URL
url = "https://raw.githubusercontent.com/q1017673817/iptvz/refs/heads/main/zubo_all.txt"

# 下载源文件
print("📡 正在下载直播源...")
import requests
try:
    res = requests.get(url, timeout=60)
    res.encoding = 'utf-8'
    lines = [i.strip() for i in res.text.splitlines() if i.strip()]
    print(f"✅ 成功下载源文件，共 {len(lines)} 条")
except Exception as e:
    print(f"❌ 下载失败: {e}")
    raise SystemExit(1)

# 省份关键词
provinces = ["北京","天津","河北","山西","内蒙古","辽宁","吉林","黑龙江","上海","江苏","浙江",
             "安徽","福建","江西","山东","河南","湖北","湖南","广东","广西","海南","重庆","四川",
             "贵州","云南","西藏","陕西","甘肃","青海","宁夏","新疆","港澳台"]

# 分类逻辑
groups = {}
current_group = None

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

    groups.setdefault(group, []).append({"name": name, "link": link})

# 异步测速函数
async def test_stream(session, item):
    start = time()
    try:
        async with session.get(item["link"], timeout=5) as resp:
            await resp.content.read(1024)  # 只读前1KB，避免下载整个流
        elapsed = time() - start
        return (item["name"], item["link"], elapsed)
    except:
        return (item["name"], item["link"], float("inf"))

# 异步批量测速
async def test_group(items):
    timeout = aiohttp.ClientTimeout(total=5)
    connector = aiohttp.TCPConnector(limit=1000)  # 最大并发1000
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        tasks = [asyncio.create_task(test_stream(session, item)) for item in items]
        results = await asyncio.gather(*tasks)
    # 按响应时间升序排序
    results.sort(key=lambda x: x[2])
    return [{"name": n, "link": l} for n, l, t in results]

# 执行测速
print("⏱ 开始异步并行测速...")
for group_name, items in groups.items():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    items_sorted = loop.run_until_complete(test_group(items))
    groups[group_name] = items_sorted
    loop.close()
    print(f"✅ {group_name} 测速完成，共 {len(items_sorted)} 条")

# 写入文件
with open(outfile, "w", encoding="utf-8") as f:
    for g, items in groups.items():
        f.write(f"{g},#genre#\n")
        for i in items:
            f.write(f"{i['name']},{i['link']}\n")
        f.write("\n")

total = sum(len(v) for v in groups.values())
print(f"✅ 已生成 {outfile}，共 {total} 条直播源，分组内按测速最快排序")
