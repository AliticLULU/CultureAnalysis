import pandas as pd

# 读取文件
df = pd.read_csv('all_data.csv')
print(f"Total records: {len(df):,}")

# 筛选str.chinese不为空的行
df_train = df[df['str.chinese'].notna() & (df['str.chinese'].str.strip() != '')]

print(f"Filtered records: {len(df_train):,} ({len(df_train)/len(df)*100:.1f}%)")

# 保存为新文件
df_train.to_csv('train_data.csv', index=False)
print(f"\n✅ Saved to train_data.csv")