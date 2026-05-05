import pandas as pd
import os

# 定义文件路径
target_file = 'all_data.csv'
source_files = [
    'origindata/俄语/data.csv',
    'origindata/日语/data.csv',
    'origindata/法语/data.csv',
    'origindata/简体/data.csv',
    'origindata/繁体/data.csv',
    'origindata/英语/data.csv',
    'origindata/西语/data.csv',
    'origindata/越南语/data.csv',
    'origindata/韩语/data.csv'
]

# 检查目标文件是否存在，如果存在则清空
if os.path.exists(target_file):
    print(f"清空已存在的 {target_file}")
    # 清空文件内容
    open(target_file, 'w').close()

# 读取并合并所有数据
all_data = []
for source_file in source_files:
    if os.path.exists(source_file):
        print(f"正在读取: {source_file}")
        df = pd.read_csv(source_file)
        all_data.append(df)
        print(f"  - 读取 {len(df)} 行数据")
    else:
        print(f"警告: 文件不存在 - {source_file}")

# 合并所有数据
if all_data:
    merged_df = pd.concat(all_data, ignore_index=True)
    print(f"\n合并完成，共 {len(merged_df)} 行数据")

    # 保存到目标文件
    merged_df.to_csv(target_file, index=False)
    print(f"数据已保存到 {target_file}")
else:
    print("错误: 没有读取到任何数据")