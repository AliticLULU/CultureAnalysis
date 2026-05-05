import pandas as pd

# 读取文件
df = pd.read_csv('all_data.csv')
print(f"Total records: {len(df):,}")

# 合并两列，用空格拼接
df['str.chinese'] = df['desc.clean'].fillna('') + ' ' + df['textExtra.hashtagName.clean'].fillna('')

# 清理多余空格
df['str.chinese'] = df['str.chinese'].str.strip()

# 统计
has_content = (df['str.chinese'] != '').sum()
empty_count = (df['str.chinese'] == '').sum()
print(f"\nstr.chinese:")
print(f"  Has content: {has_content:,} ({has_content/len(df)*100:.1f}%)")
print(f"  Empty: {empty_count:,} ({empty_count/len(df)*100:.1f}%)")

# 保存
df.to_csv('all_data.csv', index=False)
print(f"\n✅ Saved to all_data.csv")