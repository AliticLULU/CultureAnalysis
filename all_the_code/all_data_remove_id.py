import pandas as pd
import os

target_file = 'all_data.csv'

if os.path.exists(target_file):
    # 读取数据
    df = pd.read_csv(target_file)
    original_count = len(df)

    # 根据id列去重，保留第一条
    df = df.drop_duplicates(subset=['id'], keep='first')
    new_count = len(df)

    # 保存去重后的数据
    df.to_csv(target_file, index=False)

    print(f"去重前数据行数: {original_count}")
    print(f"去重后数据行数: {new_count}")
    print(f"去除重复行数: {original_count - new_count}")
    print(f"数据已保存到 {target_file}")
else:
    print(f"错误: 文件 {target_file} 不存在")