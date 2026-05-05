import pandas as pd

df = pd.read_csv('all_data.csv')

print(f"Total records: {len(df):,}\n")

# desc 为空情况
desc_null = df['desc.clean'].isna().sum()
desc_empty = (df['desc.clean'].fillna('').str.strip() == '').sum()
desc_has_content = len(df) - desc_empty

print(f"desc column:")
print(f"  NaN (isna):     {desc_null:>8,} ({desc_null/len(df)*100:.2f}%)")
print(f"  Empty/blank:    {desc_empty:>8,} ({desc_empty/len(df)*100:.2f}%)")
print(f"  Has content:    {desc_has_content:>8,} ({desc_has_content/len(df)*100:.2f}%)")

print()

# textExtra.hashtagName 为空情况
hashtag_null = df['textExtra.hashtagName.clean'].isna().sum()
hashtag_empty = (df['textExtra.hashtagName.clean'].fillna('').str.strip() == '').sum()
hashtag_has_content = len(df) - hashtag_empty

print(f"textExtra.hashtagName column:")
print(f"  NaN (isna):     {hashtag_null:>8,} ({hashtag_null/len(df)*100:.2f}%)")
print(f"  Empty/blank:    {hashtag_empty:>8,} ({hashtag_empty/len(df)*100:.2f}%)")
print(f"  Has content:    {hashtag_has_content:>8,} ({hashtag_has_content/len(df)*100:.2f}%)")

print()

# 两列均为空
desc_is_empty = df['desc.clean'].fillna('').str.strip() == ''
hashtag_is_empty = df['textExtra.hashtagName.clean'].fillna('').str.strip() == ''
both_empty = (desc_is_empty & hashtag_is_empty).sum()

# 两列均有内容
both_has_content = ((~desc_is_empty) & (~hashtag_is_empty)).sum()

# 仅desc有内容
only_desc = ((~desc_is_empty) & hashtag_is_empty).sum()

# 仅hashtag有内容
only_hashtag = (desc_is_empty & (~hashtag_is_empty)).sum()

print(f"Combined analysis:")
print(f"  Both empty:         {both_empty:>8,} ({both_empty/len(df)*100:.2f}%)")
print(f"  Both have content:  {both_has_content:>8,} ({both_has_content/len(df)*100:.2f}%)")
print(f"  Only desc:          {only_desc:>8,} ({only_desc/len(df)*100:.2f}%)")
print(f"  Only hashtag:       {only_hashtag:>8,} ({only_hashtag/len(df)*100:.2f}%)")