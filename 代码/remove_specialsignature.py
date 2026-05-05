import pandas as pd
import re


def clean_text_content(text):
    """
    清理文本内容，只保留语言相关字符
    """
    if pd.isna(text) or text == '':
        return text

    text = str(text)

    # 移除URL链接
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)

    # 移除邮箱地址
    text = re.sub(r'\S+@\S+', '', text)

    # 移除HTML标签
    text = re.sub(r'<[^>]+>', '', text)

    # 移除特殊符号，只保留字母、数字、汉字、基本标点
    text = re.sub(
        r'[^\w\s\u4e00-\u9fff\u0400-\u04FF\u0100-\u017F\u0180-\u024F\u1E00-\u1EFF\uAC00-\uD7AF\u3130-\u318F\u3040-\u309F\u30A0-\u30FF\u31F0-\u31FF\uFF00-\uFFEF.,!?;:\'"(){}\[\]\\\-+=<>~`#@%^&*|]+',
        ' ', text)

    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text)

    # 移除开头和结尾的空白
    text = text.strip()

    return text


def clean_hashtag_content(text):
    """
    清理hashtag内容，只保留语言相关字符
    """
    if pd.isna(text) or text == '':
        return text

    text = str(text)

    # 移除URL链接
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)

    # 移除邮箱地址
    text = re.sub(r'\S+@\S+', '', text)

    # 移除HTML标签
    text = re.sub(r'<[^>]+>', '', text)

    # 对于hashtag，移除特殊分隔符如分号，只保留标签名称
    if ';' in text:
        # 分割标签并清理每个标签
        hashtags = text.split(';')
        cleaned_tags = []
        for tag in hashtags:
            # 只保留字母、数字、汉字等语言字符
            clean_tag = re.sub(
                r'[^\w\u4e00-\u9fff\u0400-\u04FF\u0100-\u017F\u0180-\u024F\u1E00-\u1EFF\uAC00-\uD7AF\u3130-\u318F\u3040-\u309F\u30A0-\u30FF\u31F0-\u31FF\uFF00-\uFFEF]',
                '', tag)
            if clean_tag.strip():  # 只添加非空标签
                cleaned_tags.append(clean_tag.strip())
        text = ';'.join(cleaned_tags)
    else:
        # 只保留字母、数字、汉字等语言字符
        text = re.sub(
            r'[^\w\u4e00-\u9fff\u0400-\u04FF\u0100-\u017F\u0180-\u024F\u1E00-\u1EFF\uAC00-\uD7AF\u3130-\u318F\u3040-\u309F\u30A0-\u30FF\u31F0-\u31FF\uFF00-\uFFEF]',
            '', text)

    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text)

    # 移除开头和结尾的空白
    text = text.strip()

    return text


def clean_csv_columns_only(file_path):
    """
    仅对CSV文件中的desc和textExtra.hashtagName列进行符号清洗
    """
    # 读取CSV文件
    df = pd.read_csv(file_path)

    print("开始清洗符号...")

    # 清洗 desc 列
    if 'desc' in df.columns:
        print("正在清洗 desc 列...")
        df['desc'] = df['desc'].apply(clean_text_content)
        print(f"desc 列清洗完成")

    # 清洗 textExtra.hashtagName 列
    if 'textExtra.hashtagName' in df.columns:
        print("正在清洗 textExtra.hashtagName 列...")
        df['textExtra.hashtagName'] = df['textExtra.hashtagName'].apply(clean_hashtag_content)
        print(f"textExtra.hashtagName 列清洗完成")

    # 保存回原文件
    df.to_csv(file_path, index=False, encoding='utf-8')

    print(f"符号清洗完成！已保存到原文件: {file_path}")

    # 显示清洗结果预览
    print("\n清洗结果预览:")
    preview_cols = [col for col in df.columns if col in ['desc', 'textExtra.hashtagName']]
    if preview_cols:
        print(df[preview_cols].head())

    return df


def main():
    file_path = 'origindata/韩语/cleaned.csv'  # 文件路径

    # 执行符号清洗
    df = clean_csv_columns_only(file_path)

    print("\n符号清洗统计:")
    print(f"总行数: {len(df)}")

    if 'desc' in df.columns:
        desc_non_empty = df['desc'].notna().sum()
        print(f"desc 列非空行数: {desc_non_empty}")

    if 'textExtra.hashtagName' in df.columns:
        hashtag_non_empty = df['textExtra.hashtagName'].notna().sum()
        print(f"textExtra.hashtagName 列非空行数: {hashtag_non_empty}")


if __name__ == '__main__':
    main()