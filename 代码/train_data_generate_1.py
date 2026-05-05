import pandas as pd

# 读取文件
df = pd.read_csv('train_data.csv')
print(f"Total records: {len(df):,}")

# 仅保留指定列
columns_to_keep = [
    'id',
    'stats.collectCount',
    'stats.commentCount',
    'stats.diggCount',
    'stats.playCount',
    'stats.shareCount',
    'str.chinese',
    'length',
    'spread_score'
]

df = df[columns_to_keep]

# 保存
df.to_csv('train_data.csv', index=False)
print(f"Columns: {list(df.columns)}")
print(f"\n✅ Saved to train_data.csv")