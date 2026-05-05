import pandas as pd
import re
import warnings

warnings.filterwarnings('ignore')

# 读取数据
print("Loading data...")
df = pd.read_csv('origindata/繁体/cleaned_data.csv')
print(f"Total records: {len(df):,}")


def clean_to_chinese_only(text):
    """
    清洗文本，仅保留简体中文字符
    同时清理多余的空白和标点
    """
    if pd.isna(text):
        return ""

    # 转为字符串
    text = str(text)

    # 第一步：去除URL
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)

    # 第二步：仅保留中文字符（包括繁体，后续会转简体）
    # \u4e00-\u9fff 基本汉字
    # \u3400-\u4dbf 扩展A区汉字
    text = re.sub(r'[^\u4e00-\u9fff\u3400-\u4dbf]', '', text)

    # 第三步：去除多余空格和换行
    text = text.strip()

    return text


# 处理 desc.cn 列
print("\nProcessing desc.cn...")
df['desc'] = df['desc'].fillna('')
df['desc.clean'] = df['desc'].apply(clean_to_chinese_only)
non_empty_desc = (df['desc.clean'].str.len() > 0).sum()
print(f"  Non-empty after cleaning: {non_empty_desc:,} / {len(df):,}")

# 处理 textExtra.hashtagName.cn 列
print("\nProcessing textExtra.hashtagName.cn...")
df['textExtra.hashtagName'] = df['textExtra.hashtagName'].fillna('')
df['textExtra.hashtagName.clean'] = df['textExtra.hashtagName'].apply(clean_to_chinese_only)
non_empty_hashtag = (df['textExtra.hashtagName.clean'].str.len() > 0).sum()
print(f"  Non-empty after cleaning: {non_empty_hashtag:,} / {len(df):,}")

# 展示一些清洗前后对比
print("\n" + "=" * 80)
print("Sample before/after comparison:")
print("=" * 80)
sample_idx = [0, 1] if len(df) >= 2 else [0]
for idx in sample_idx:
    print(f"\nRecord {idx}:")
    print(f"  desc.cn (before): {str(df.loc[idx, 'desc'])[:150]}...")
    print(f"  desc.clean (after): {df.loc[idx, 'desc.clean'][:150]}...")
    print(f"\n  hashtag.cn (before): {str(df.loc[idx, 'textExtra.hashtagName'])[:100]}...")
    print(f"  hashtag.clean (after): {df.loc[idx, 'textExtra.hashtagName.clean'][:100]}...")

# 保存结果
print("\nSaving to all_data.csv...")
df.to_csv('origindata/繁体/cleaned.csv', index=False)
print("✅ Done! New columns added: desc.clean, textExtra.hashtagName.clean")

# 统计清洗后的数据质量
print("\n" + "=" * 80)
print("Cleaning Statistics:")
print("=" * 80)
print(f"Total records: {len(df):,}")
print(f"desc.clean has content: {non_empty_desc:,} ({non_empty_desc / len(df) * 100:.1f}%)")
print(f"textExtra.hashtagName.clean has content: {non_empty_hashtag:,} ({non_empty_hashtag / len(df) * 100:.1f}%)")
print(
    f"Both columns have content: {((df['desc.clean'].str.len() > 0) & (df['textExtra.hashtagName.clean'].str.len() > 0)).sum():,}")

avg_desc_len = df['desc.clean'].str.len().mean()
avg_hashtag_len = df['textExtra.hashtagName.clean'].str.len().mean()
print(f"\nAverage desc.clean length: {avg_desc_len:.1f} characters")
print(f"Average hashtag.clean length: {avg_hashtag_len:.1f} characters")