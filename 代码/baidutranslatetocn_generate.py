# -*- coding: utf-8 -*-

import requests
import random
import json
import time
import pandas as pd
from hashlib import md5
from tqdm import tqdm
import numpy as np

# Set your own appid/appkey.
appid = ''
appkey = ''

# For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`
from_lang = 'auto'  # 自动识别源语言
to_lang = 'zh'  # 中文

endpoint = 'https://fanyi-api.baidu.com'
path = '/api/trans/vip/translate'
url = endpoint + path


def make_md5(s):
    """生成MD5签名，确保编码一致"""
    if isinstance(s, str):
        s = s.encode('utf-8')
    elif not isinstance(s, bytes):
        s = str(s).encode('utf-8')
    return md5(s).hexdigest()


def translate_single_text_baidu(text):
    """
    使用百度翻译API翻译单个文本
    """
    if pd.isna(text) or text == '':
        return ''

    # 清理文本，确保没有特殊字符导致签名问题
    clean_text = str(text).replace('\n', ' ').replace('\r', ' ').strip()

    # 百度翻译API限制单次请求字符数，通常不超过6000字节
    if len(clean_text) > 2000:  # 设置更保守的限制
        clean_text = clean_text[:2000]

    # 生成随机数
    salt = str(random.randint(32768, 65536))

    # 构建签名字符串 - 严格按照 appid+q+salt+密钥 的顺序，使用UTF-8编码
    sign_str = appid + clean_text + salt + appkey

    # 计算签名
    sign = make_md5(sign_str)

    # 构建请求参数
    params = {
        'q': clean_text,
        'from': from_lang,
        'to': to_lang,
        'appid': appid,
        'salt': salt,
        'sign': sign
    }

    try:
        # 使用GET方法发送请求
        response = requests.get(url, params=params, timeout=20)

        if response.status_code == 200:
            result = response.json()

            if 'error_code' in result:
                error_code = result['error_code']
                if error_code == '54001':  # 签名错误
                    print(f"签名错误！")
                    print(f"App ID: {appid}")
                    print(f"Query: {clean_text[:50]}...")
                    print(f"Salt: {salt}")
                    print(f"Sign string: {sign_str}")
                    print(f"Calculated sign: {sign}")
                    print(f"Response: {result}")
                    return str(text)  # 直接返回原文
                elif error_code == '54003':  # 访问频率受限
                    print(f"访问频率受限，等待3秒后重试...")
                    time.sleep(3)
                    return translate_single_text_baidu(text)  # 递归重试
                elif error_code == '54004':  # 账户余额不足
                    print(f"账户余额不足，错误码: {error_code}")
                    return str(text)
                elif error_code == '58001':  # 翻译语言不支持
                    print(f"翻译语言不支持，错误码: {error_code}")
                    return str(text)
                else:
                    print(f"翻译失败，错误码: {error_code}, 文本: {clean_text[:50]}...")
                    return str(text)
            else:
                # 成功翻译
                translated_text = result['trans_result'][0]['dst']
                return translated_text
        else:
            print(f"HTTP请求失败: {response.status_code}, 文本: {clean_text[:50]}...")
            return str(text)

    except Exception as e:
        print(f"翻译异常: {e}, 文本: {clean_text[:50]}...")
        return str(text)


def translate_column_with_save(df, source_col, target_col, file_path):
    """
    使用百度翻译API逐行翻译指定列，每翻译完一行就保存数据
    """
    print(f"开始使用百度翻译API逐行翻译 {source_col} -> {target_col}，边翻译边保存...")

    # 检查目标列是否存在，不存在则创建
    if target_col not in df.columns:
        df[target_col] = ''

    # 找到第一个未翻译的行（即目标列为空的行）
    start_idx = 0
    for idx in range(len(df)):
        if pd.isna(df.iloc[idx][target_col]) or df.iloc[idx][target_col] == '':
            start_idx = idx
            break
    else:
        # 如果所有行都已翻译，则跳过此列
        print(f"列 {target_col} 已经全部翻译完成，跳过...")
        return df

    print(f"从第 {start_idx + 1} 行开始翻译...")

    for idx in tqdm(range(start_idx, len(df)), desc=f"百度翻译 {source_col}", initial=start_idx, total=len(df)):
        original_text = df.iloc[idx][source_col]

        if pd.isna(original_text) or original_text == '':
            df.at[idx, target_col] = ''
        else:
            # 翻译当前行的数据
            translated_text = translate_single_text_baidu(str(original_text))
            df.at[idx, target_col] = translated_text

        # 每翻译完一行就保存一次CSV文件
        df.to_csv(file_path, index=False, encoding='utf-8')

        # 控制请求频率
        time.sleep(0.5)

    print(f"列 {target_col} 翻译完成！结果已保存到 {file_path}")
    return df


def main():
    file_path = 'origindata/法语/cleaned.csv'

    # 读取CSV文件
    df = pd.read_csv(file_path)

    print("开始使用百度翻译API逐行翻译(自动识别语言)到中文...")

    # 翻译desc列 - 每翻译完一行就保存
    df = translate_column_with_save(df, 'desc', 'desc.cn', file_path)

    # 翻译textExtra.hashtagName列 - 每翻译完一行就保存
    df = translate_column_with_save(df, 'textExtra.hashtagName', 'textExtra.hashtagName.cn', file_path)

    print("所有翻译完成！结果已保存到 origindata/法语/cleaned.csv")

    # 显示翻译结果的前几行以供验证
    print("\n翻译结果预览:")
    preview_cols = [col for col in df.columns if '.cn' in col or col in ['desc', 'textExtra.hashtagName']]
    print(df[preview_cols].head())


if __name__ == '__main__':
    main()