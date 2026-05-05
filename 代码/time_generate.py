import pandas as pd

# 1. 读取CSV文件 (请将 'your_file.csv' 替换为你的实际文件路径)
file_path = 'all_data.csv' # 例如: 'data.csv'
df = pd.read_csv(file_path)

# 2. 转换时间戳为标准日期时间
# 注意: createTime列的数值看起来是秒级时间戳
df['createTime_date'] = pd.to_datetime(df['createTime'], unit='s')

# 3. 保存回原来的CSV文件
df.to_csv(file_path, index=False)

print("转换完成！数据已保存回原文件。")