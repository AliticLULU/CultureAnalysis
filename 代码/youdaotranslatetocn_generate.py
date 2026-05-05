# -*- coding: utf-8 -*-
import sys
import uuid
import requests
import hashlib
import time
import pandas as pd
from importlib import reload
from tqdm import tqdm
import numpy as np

reload(sys)

YOUDAO_URL = 'https://openapi.youdao.com/v2/api'
APP_KEY = ''
APP_SECRET = ''


def encrypt(signStr):
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(signStr.encode('utf-8'))
    return hash_algorithm.hexdigest()


def truncate(q):
    if q is None:
        return None
    size = len(q)
    return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]


def translate_single_text(text, from_lang='auto', to_lang='zh-CHS'):
    """
    发送单个翻译请求，等待返回后结束
    """
    if pd.isna(text) or text == '':
        return ''

    # 清理文本
    clean_text = str(text).replace('\n', ' ').replace('\r', ' ').strip()

    # 如果文本太长，进行截断（有道API通常限制在5000字符内）
    if len(clean_text) > 5000:
        clean_text = clean_text[:5000]

    data = {}
    data['from'] = from_lang  # 自动识别源语言
    data['to'] = to_lang  # 中文简体
    data['signType'] = 'v3'
    curtime = str(int(time.time()))
    data['curtime'] = curtime
    salt = str(uuid.uuid1())

    signStr = APP_KEY + truncate(clean_text) + salt + curtime + APP_SECRET
    sign = encrypt(signStr)
    data['appKey'] = APP_KEY
    data['q'] = clean_text
    data['salt'] = salt
    data['sign'] = sign
    time.sleep(0.5)

    try:
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(YOUDAO_URL, data=data, headers=headers, timeout=20)

        if response.status_code == 200:
            result = response.json()
            if result.get('errorCode') == '0':  # 翻译成功
                return result.get('translation', [''])[0]
            elif result.get('errorCode') == '411':
                print(f"文本过长，截断重试: {clean_text[:30]}...")
                # 进一步截断文本
                shorter_text = clean_text[:1000]
                return translate_single_text(shorter_text, from_lang, to_lang)
            else:
                print(f"翻译失败，错误码: {result.get('errorCode')}, 文本: {clean_text[:50]}...")
                return str(text)  # 返回原文本
        else:
            print(f"HTTP请求失败: {response.status_code}, 文本: {clean_text[:50]}...")
            return str(text)  # 返回原文本

    except Exception as e:
        print(f"翻译异常: {e}, 文本: {clean_text[:50]}...")
        return str(text)  # 返回原文本


def translate_with_save_progress(df, source_col, target_col, save_file_path, from_lang='auto', to_lang='zh-CHS'):
    """
    翻译指定列，并在每次翻译后保存进度
    """
    print(f"开始翻译 {source_col} -> {target_col}，启用断点续传...")

    # 检查目标列是否存在，不存在则创建
    if target_col not in df.columns:
        df[target_col] = ''

    # 找到第一个未翻译的行（即目标列为空的行）
    start_idx = 0
    for idx in range(len(df)):
        if pd.isna(df.iloc[idx][target_col]) or df.iloc[idx][target_col] == '':
            start_idx = idx
            break

    print(f"从第 {start_idx + 1} 行开始翻译...")

    for idx in tqdm(range(start_idx, len(df)), desc=f"翻译 {source_col}", initial=start_idx, total=len(df)):
        original_text = df.iloc[idx][source_col]

        if pd.isna(original_text) or original_text == '':
            df.at[idx, target_col] = ''
        else:
            # 翻译当前行的数据
            translated_text = translate_single_text(str(original_text), from_lang, to_lang)
            df.at[idx, target_col] = translated_text

        # 每翻译完一行就保存一次
        if idx % 10 == 0 or idx == len(df) - 1:  # 每10行或最后一行保存一次
            df.to_csv(save_file_path, index=False, encoding='utf-8')
            # print(f"已保存进度至第 {idx + 1} 行")

        # 等待一段时间，确保请求处理完成
        time.sleep(0.5)

    # 最后再保存一次
    df.to_csv(save_file_path, index=False, encoding='utf-8')
    print(f"翻译完成！最终结果已保存到 {save_file_path}")

    return df


def main():
    input_file = 'origindata/日语/cleaned.csv'
    output_file = 'origindata/日语/cleaned.csv'

    # 读取CSV文件
    df = pd.read_csv(input_file)

    print("开始使用有道翻译API逐行翻译(自动识别语言)到中文...")

    # 翻译desc列 - 启用断点续传
    df = translate_with_save_progress(df, 'desc', 'desc.cn', output_file, from_lang='auto', to_lang='zh-CHS')

    # 翻译textExtra.hashtagName列 - 启用断点续传
    df = translate_with_save_progress(df, 'textExtra.hashtagName', 'textExtra.hashtagName.cn', output_file,
                                      from_lang='auto', to_lang='zh-CHS')

    print("所有翻译完成！结果已保存到 origindata/日语/cleaned.csv")

    # 显示翻译结果的前几行以供验证
    print("\n翻译结果预览:")
    preview_cols = [col for col in df.columns if '.cn' in col or col in ['desc', 'textExtra.hashtagName']]
    print(df[preview_cols].head())


if __name__ == '__main__':
    # 检查API凭证
    if APP_KEY == '您的应用ID' or APP_SECRET == '您的应用密钥':
        print("请先在代码中填入您的有道翻译API应用ID和应用密钥！")
        print("获取方式：访问 https://ai.youdao.com/")
    else:
        main()