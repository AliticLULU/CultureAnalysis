import pandas as pd
import requests
import time
import json

# 读取CSV文件
df = pd.read_csv('origindata/越南语/cleaned.csv')  # 请将'your_file.csv'替换为您的实际文件路径

# DeepSeek API配置
DEEPSEEK_API_KEY = ""  # 请填入您的API密钥
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"


def translate_with_deepseek(text, source_field):
    """
    使用DeepSeek API翻译文本到中文
    """
    if pd.isna(text) or text == '':
        return ''

    # 构造提示词，严格要求返回纯中文翻译
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
        "model": "deepseek-chat",  # 或者使用其他可用模型
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.1,  # 低温度确保一致性
        "max_tokens": 1000  # 根据需要调整
    }

    try:
        response = requests.post(DEEPSEEK_URL, headers=headers, json=payload)
        response.raise_for_status()

        result = response.json()
        translated_text = result['choices'][0]['message']['content'].strip()

        # 清理可能的多余字符或标记
        translated_text = translated_text.replace('\n', ' ').strip()

        return translated_text

    except requests.exceptions.RequestException as e:
        print(f"API请求错误: {e}")
        return str(text)  # 返回原文本作为备选
    except Exception as e:
        print(f"翻译错误: {e}")
        return str(text)  # 返回原文本作为备选


def batch_translate_column(df, source_col, target_col, batch_size=5):
    """
    批量翻译指定列
    """
    # 创建目标列
    df[target_col] = ''

    for idx in range(len(df)):
        original_text = df.iloc[idx][source_col]

        if pd.isna(original_text) or original_text == '':
            df.at[idx, target_col] = ''
        else:
            print(f"正在翻译第 {idx + 1}/{len(df)} 行的 {source_col}...")

            # 根据列类型选择适当的提示词
            field_type = 'desc' if source_col == 'desc' else 'hashtag'
            translated_text = translate_with_deepseek(original_text, field_type)

            df.at[idx, target_col] = translated_text

            # 添加延时避免API限制
            time.sleep(1)

    return df


# 执行翻译
print("开始翻译 desc 列...")
df = batch_translate_column(df, 'desc', 'desc.cn')

print("开始翻译 textExtra.hashtagName 列...")
df = batch_translate_column(df, 'textExtra.hashtagName', 'textExtra.hashtagName.cn')

# 保存回原CSV文件
df.to_csv('origindata/越南语/cleaned.csv', index=False, encoding='utf-8')

print("翻译完成！结果已保存回原文件 origindata/越南语/cleaned.csv")

# 显示翻译结果的前几行以供验证
print("\n翻译结果预览:")
preview_cols = [col for col in df.columns if '.cn' in col or col in ['desc', 'textExtra.hashtagName']]
print(df[preview_cols].head())