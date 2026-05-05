import pandas as pd
import requests
import time
import json
import os

# 读取CSV文件
file_path = 'origindata/韩语/cleaned.csv'  # 请修改为您的实际文件路径
df = pd.read_csv(file_path)

# DeepSeek API配置
DEEPSEEK_API_KEY = ""
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"


def translate_with_deepseek(text, source_field):
    """
    使用DeepSeek API翻译文本到中文
    """
    if pd.isna(text) or str(text).strip() == '':
        return ''

    text = str(text).strip()

    # 构造提示词
    if source_field == 'desc':
        prompt = f"""请将以下内容翻译成简体中文，只返回翻译结果，不要添加任何解释或说明：
{text}"""
    elif source_field == 'hashtag':
        prompt = f"""请将以下标签或话题名称翻译成简体中文，只返回翻译结果，不要添加任何解释或说明：
{text}"""

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.1,
        "max_tokens": 1000
    }

    try:
        response = requests.post(DEEPSEEK_URL, headers=headers, json=payload)
        response.raise_for_status()

        result = response.json()
        translated_text = result['choices'][0]['message']['content'].strip()
        translated_text = translated_text.replace('\n', ' ').strip()

        return translated_text

    except requests.exceptions.RequestException as e:
        print(f"  API请求错误: {e}")
        return ''
    except Exception as e:
        print(f"  翻译错误: {e}")
        return ''


def translate_and_save(df, file_path, source_col, target_col):
    """
    逐行检查并翻译，每翻译一条就保存一次
    """
    field_type = 'desc' if source_col == 'desc' else 'hashtag'

    # 统计需要翻译的行数
    need_translate = 0
    for idx in range(len(df)):
        original_text = df.iloc[idx][source_col]
        existing_translation = df.iloc[idx][target_col] if target_col in df.columns else ''

        # 原文不为空 且 译文为空
        if (pd.notna(original_text) and str(original_text).strip() != '') and \
                (pd.isna(existing_translation) or str(existing_translation).strip() == ''):
            need_translate += 1

    if need_translate == 0:
        print(f"\n{source_col} → {target_col}: 所有内容已翻译完毕，无需处理")
        return df

    print(f"\n{source_col} → {target_col}: 发现 {need_translate} 条需要翻译")

    translated_count = 0
    for idx in range(len(df)):
        original_text = df.iloc[idx][source_col]
        existing_translation = df.iloc[idx][target_col] if target_col in df.columns else ''

        # 原文不为空 且 译文为空
        if (pd.notna(original_text) and str(original_text).strip() != '') and \
                (pd.isna(existing_translation) or str(existing_translation).strip() == ''):
            print(f"  [{translated_count + 1}/{need_translate}] 翻译第 {idx + 1} 行...")

            translated_text = translate_with_deepseek(original_text, field_type)
            df.at[idx, target_col] = translated_text
            translated_count += 1

            # 每翻译一条就保存一次
            df.to_csv(file_path, index=False, encoding='utf-8')

            # 延时避免API限制
            time.sleep(1)

    print(f"  {source_col} → {target_col}: 完成，共翻译 {translated_count} 条")
    return df


# 确保目标列存在
if 'desc.cn' not in df.columns:
    df['desc.cn'] = ''
if 'textExtra.hashtagName.cn' not in df.columns:
    df['textExtra.hashtagName.cn'] = ''

# 先保存一次，确保列结构存在
df.to_csv(file_path, index=False, encoding='utf-8')

print(f"文件: {file_path}")
print(f"总行数: {len(df):,}")

# 处理 desc 列
df = translate_and_save(df, file_path, 'desc', 'desc.cn')

# 重新读取（确保数据最新）
df = pd.read_csv(file_path)

# 处理 textExtra.hashtagName 列
df = translate_and_save(df, file_path, 'textExtra.hashtagName', 'textExtra.hashtagName.cn')

print(f"\n✅ 全部处理完成！结果已保存至: {file_path}")

# 显示翻译结果统计
print(f"\n翻译结果统计:")
desc_original = df['desc'].notna().sum()
desc_translated = (df['desc.cn'].notna() & (df['desc.cn'] != '')).sum()
print(f"  desc: 原文有内容 {desc_original:,} → 已翻译 {desc_translated:,}")

hashtag_original = df['textExtra.hashtagName'].notna().sum()
hashtag_translated = (df['textExtra.hashtagName.cn'].notna() & (df['textExtra.hashtagName.cn'] != '')).sum()
print(f"  textExtra.hashtagName: 原文有内容 {hashtag_original:,} → 已翻译 {hashtag_translated:,}")