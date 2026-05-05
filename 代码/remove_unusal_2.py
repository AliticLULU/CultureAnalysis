import pandas as pd


def clean_csv_by_length_threshold(file_path, output_file):
    """
    删除CSV文件中超过指定长度阈值的行
    """
    # 读取CSV文件
    df = pd.read_csv(file_path)

    print(f"原始数据形状: {df.shape}")

    # 记录删除前的行数
    initial_rows = len(df)

    # 删除desc列字符串长度超过1420的行
    if 'desc' in df.columns:
        desc_lengths = df['desc'].astype(str).apply(len)
        df = df[desc_lengths <= 825]
        print(f"删除desc列长度>1420的行后，剩余行数: {len(df)}")

    # 删除textExtra.hashtagName列字符串长度超过330的行
    if 'textExtra.hashtagName' in df.columns:
        hashtag_lengths = df['textExtra.hashtagName'].astype(str).apply(len)
        df = df[hashtag_lengths <= 290]
        print(f"删除textExtra.hashtagName列长度>330的行后，剩余行数: {len(df)}")

    # 保存清理后的数据
    df.to_csv(output_file, index=False)

    print(f"删除了 {initial_rows - len(df)} 行数据")
    print(f"最终数据形状: {df.shape}")
    print(f"清理后的数据已保存到: {output_file}")


def main():
    input_file = 'origindata/韩语/cleaned.csv'
    output_file = 'origindata/韩语/cleaned.csv'  # 输出文件路径

    clean_csv_by_length_threshold(input_file, output_file)


if __name__ == '__main__':
    main()