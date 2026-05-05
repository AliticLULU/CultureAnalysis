import pandas as pd

df = pd.read_csv('train_data.csv')

print("First 100 rows of desc.clean and textExtra.hashtagName.clean:\n")
print("=" * 80)

for i in range(min(100, len(df))):
    desc = df.loc[i, 'str.chinese'] if pd.notna(df.loc[i, 'str.chinese']) else ''

    print(f"Row {i}:")
    print(f"  desc.clean: {desc[:200]}")  # 限制显示长度
    print("-" * 80)