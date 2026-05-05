# -*- coding: utf-8 -*-

import csv
import io
import pandas as pd
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models
from tqdm import tqdm
import os
import time
import numpy as np

SecretId = ""  # 替换为您的SecretId
SecretKey = ""  # 替换为您的SecretKey


class Translator:
    def __init__(self, from_lang, to_lang):
        self.from_lang = from_lang
        self.to_lang = to_lang

    def translate(self, text):
        try:
            cred = credential.Credential(SecretId, SecretKey)
            httpProfile = HttpProfile()
            httpProfile.endpoint = "tmt.tencentcloudapi.com"

            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = tmt_client.TmtClient(cred, "ap-beijing", clientProfile)

            req = models.TextTranslateRequest()

            # 清理文本，确保没有特殊字符导致问题
            clean_text = str(text).replace('\n', ' ').replace('\r', ' ').strip()

            # 腾讯翻译API限制单次请求字符数，通常不超过5000字符
            if len(clean_text) > 2000:  # 设置更保守的限制
                clean_text = clean_text[:2000]

            req.SourceText = clean_text
            req.Source = self.from_lang
            req.Target = self.to_lang
            req.ProjectId = 0

            resp = client.TextTranslate(req)
            return resp.TargetText

        except TencentCloudSDKException as err:
            error_code = str(err.get_code())
            if error_code == 'FailedOperation':
                print(f"翻译失败: {err}")
                return str(text)  # 返回原文，避免程序中断
            elif error_code == 'LimitExceeded':
                print(f"访问频率超限，等待3秒后重试...")
                time.sleep(3)
                return self.translate(text)  # 递归重试
            elif error_code == 'AuthFailure':
                print(f"认证失败: {err}")
                return str(text)
            else:
                print(f"翻译错误: {err}")
                return str(text)  # 返回原文，避免程序中断
        except Exception as e:
            print(f"翻译异常: {e}")
            return str(text)


def translate_single_text_tencent(text, from_lang='auto', to_lang='zh'):
    """
    使用腾讯翻译API翻译单个文本
    """
    if pd.isna(text) or text == '':
        return ''

    translator = Translator(from_lang=from_lang, to_lang=to_lang)
    return translator.translate(text)


def translate_column_with_save(df, source_col, target_col, file_path):
    """
    使用腾讯翻译API逐行翻译指定列，每翻译完一行就保存数据
    """
    print(f"开始使用腾讯翻译API逐行翻译 {source_col} -> {target_col}，边翻译边保存...")

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

    # 初始化翻译器
    translator = Translator(from_lang='auto', to_lang='zh')  # 自动识别源语言

    for idx in tqdm(range(start_idx, len(df)), desc=f"腾讯翻译 {source_col}", initial=start_idx, total=len(df)):
        original_text = df.iloc[idx][source_col]

        if pd.isna(original_text) or original_text == '':
            df.at[idx, target_col] = ''
        else:
            # 翻译当前行的数据
            translated_text = translator.translate(str(original_text))
            df.at[idx, target_col] = translated_text

        # 每翻译完一行就保存一次CSV文件
        df.to_csv(file_path, index=False, encoding='utf-8')

        # 控制请求频率，避免超出API限制
        time.sleep(0.25)  # 腾讯API限制5次/秒

    print(f"列 {target_col} 翻译完成！结果已保存到 {file_path}")
    return df


def main():
    file_path = 'origindata/西语/cleaned.csv'

    # 读取CSV文件
    df = pd.read_csv(file_path)

    print("开始使用腾讯翻译API逐行翻译(自动识别语言)到中文...")

    # 翻译desc列 - 每翻译完一行就保存
    df = translate_column_with_save(df, 'desc', 'desc.cn', file_path)

    # 翻译textExtra.hashtagName列 - 每翻译完一行就保存
    df = translate_column_with_save(df, 'textExtra.hashtagName', 'textExtra.hashtagName.cn', file_path)

    print("所有翻译完成！结果已保存到 origindata/西语/cleaned.csv")

    # 显示翻译结果的前几行以供验证
    print("\n翻译结果预览:")
    preview_cols = [col for col in df.columns if '.cn' in col or col in ['desc', 'textExtra.hashtagName']]
    if preview_cols:
        print(df[preview_cols].head())


def batch_translate_with_save(df, source_col, target_col, file_path, batch_size=5):
    """
    使用腾讯翻译API批量翻译指定列，每批翻译完成后保存数据
    """
    print(f"开始使用腾讯翻译API批量翻译 {source_col} -> {target_col}，每批翻译后保存...")

    # 检查目标列是否存在，不存在则创建
    if target_col not in df.columns:
        df[target_col] = ''

    # 找到需要翻译的行索引
    need_translate_indices = []
    for idx in range(len(df)):
        if pd.isna(df.iloc[idx][target_col]) or df.iloc[idx][target_col] == '':
            need_translate_indices.append(idx)

    if not need_translate_indices:
        print(f"列 {target_col} 已经全部翻译完成，跳过...")
        return df

    print(f"找到 {len(need_translate_indices)} 行需要翻译...")

    # 初始化翻译器
    translator = Translator(from_lang='auto', to_lang='zh')  # 自动识别源语言

    # 分批处理
    for i in tqdm(range(0, len(need_translate_indices), batch_size),
                  desc=f"腾讯翻译 {source_col} (批量)",
                  total=(len(need_translate_indices) + batch_size - 1) // batch_size):

        batch_indices = need_translate_indices[i:i + batch_size]

        for idx in batch_indices:
            original_text = df.iloc[idx][source_col]

            if pd.isna(original_text) or original_text == '':
                df.at[idx, target_col] = ''
            else:
                # 翻译当前行的数据
                translated_text = translator.translate(str(original_text))
                df.at[idx, target_col] = translated_text

        # 每批翻译完成后保存一次CSV文件
        df.to_csv(file_path, index=False, encoding='utf-8')

        # 控制请求频率
        time.sleep(0.25)  # 腾讯API限制5次/秒

    print(f"列 {target_col} 翻译完成！结果已保存到 {file_path}")
    return df


if __name__ == '__main__':
    main()