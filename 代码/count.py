import pandas as pd

# 读取 CSV 文件
# 请将 'your_file.csv' 替换为你的实际文件路径
df = pd.read_csv('train/train_data.csv')

# 计算数据行数 (不包括表头)
row_count = len(df)

print(f"数据总行数: {row_count}")