import pandas as pd

# 所有需要处理的输入文件路径
input_files = [
    'origindata/俄语/cleaned.csv',
    'origindata/日语/cleaned.csv',
    'origindata/法语/cleaned.csv',
    'origindata/简体/cleaned.csv',
    'origindata/繁体/cleaned.csv',
    'origindata/英语/cleaned.csv',
    'origindata/西语/cleaned.csv',
    'origindata/越南语/cleaned.csv',
    'origindata/韩语/cleaned.csv',
]

# 输出文件路径（始终是同一个文件）
output_file = 'all_data.csv'

# 读取输出文件
output_df = pd.read_csv(output_file)
print(f"Output CSV records: {len(output_df):,}")

# 检查并添加缺失的列
if 'desc.clean' not in output_df.columns:
    output_df['desc.clean'] = ''
    print("Added missing column: desc.clean")

if 'textExtra.hashtagName.clean' not in output_df.columns:
    output_df['textExtra.hashtagName.clean'] = ''
    print("Added missing column: textExtra.hashtagName.clean")

# 记录初始空值数量
desc_empty_before = output_df['desc.clean'].isna().sum() + (output_df['desc.clean'].fillna('').str.strip() == '').sum()
hashtag_empty_before = output_df['textExtra.hashtagName.clean'].isna().sum() + (
            output_df['textExtra.hashtagName.clean'].fillna('').str.strip() == '').sum()

print(f"\nBefore processing:")
print(f"  desc.clean empty: {desc_empty_before:,}")
print(f"  textExtra.hashtagName.clean empty: {hashtag_empty_before:,}")

# 逐个处理输入文件
total_desc_filled = 0
total_hashtag_filled = 0

for input_file in input_files:
    print(f"\n{'=' * 60}")
    print(f"Processing: {input_file}")

    try:
        input_df = pd.read_csv(input_file)
        print(f"  Input records: {len(input_df):,}")

        # 筛选出desc.clean不为空的行，创建映射
        input_desc_not_empty = input_df[input_df['desc.clean'].notna() & (input_df['desc.clean'].str.strip() != '')]
        desc_map = input_desc_not_empty.set_index('id')['desc.clean'].to_dict()

        input_hashtag_not_empty = input_df[input_df['textExtra.hashtagName.clean'].notna() & (
                    input_df['textExtra.hashtagName.clean'].str.strip() != '')]
        hashtag_map = input_hashtag_not_empty.set_index('id')['textExtra.hashtagName.clean'].to_dict()

        # 统计该文件能填充的数量
        desc_ids_in_output = output_df['id'].isin(desc_map.keys()).sum()
        hashtag_ids_in_output = output_df['id'].isin(hashtag_map.keys()).sum()

        # 只填充output中为空的行
        desc_filled = 0
        hashtag_filled = 0

        for idx in output_df.index:
            oid = output_df.loc[idx, 'id']
            current_desc = output_df.loc[idx, 'desc.clean']
            current_hashtag = output_df.loc[idx, 'textExtra.hashtagName.clean']

            # desc.clean为空时填充
            if (pd.isna(current_desc) or str(current_desc).strip() == '') and oid in desc_map:
                output_df.loc[idx, 'desc.clean'] = desc_map[oid]
                desc_filled += 1

            # textExtra.hashtagName.clean为空时填充
            if (pd.isna(current_hashtag) or str(current_hashtag).strip() == '') and oid in hashtag_map:
                output_df.loc[idx, 'textExtra.hashtagName.clean'] = hashtag_map[oid]
                hashtag_filled += 1

        total_desc_filled += desc_filled
        total_hashtag_filled += hashtag_filled
        print(f"  desc.clean filled: {desc_filled:,}")
        print(f"  textExtra.hashtagName.clean filled: {hashtag_filled:,}")

    except FileNotFoundError:
        print(f"  ⚠ File not found, skipping...")
    except Exception as e:
        print(f"  ⚠ Error: {e}, skipping...")

# 保存结果
output_df.to_csv(output_file, index=False)

# 最终统计
desc_empty_after = output_df['desc.clean'].isna().sum() + (output_df['desc.clean'].fillna('').str.strip() == '').sum()
hashtag_empty_after = output_df['textExtra.hashtagName.clean'].isna().sum() + (
            output_df['textExtra.hashtagName.clean'].fillna('').str.strip() == '').sum()

print(f"\n{'=' * 60}")
print(f"FINAL RESULTS")
print(f"{'=' * 60}")
print(f"  desc.clean:")
print(f"    Before: {desc_empty_before:,} empty → After: {desc_empty_after:,} empty")
print(f"    Total filled: {total_desc_filled:,}")
print(f"  textExtra.hashtagName.clean:")
print(f"    Before: {hashtag_empty_before:,} empty → After: {hashtag_empty_after:,} empty")
print(f"    Total filled: {total_hashtag_filled:,}")
print(f"\n✅ Saved to {output_file}")