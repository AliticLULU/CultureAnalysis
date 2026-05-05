import pandas as pd
from opencc import OpenCC
import os


def convert_csv_traditional_to_simplified(csv_file_path):
    """
    将CSV文件中的繁体中文转换为简体中文，只处理desc和textExtra.hashtagName两列
    """
    # 创建转换器，t2s表示繁体转简体
    cc = OpenCC('t2s')

    # 读取CSV文件
    df = pd.read_csv(csv_file_path)

    # 检查是否存在需要转换的列
    columns_to_convert = ['desc', 'textExtra.hashtagName']

    for col in columns_to_convert:
        if col in df.columns:
            # 对该列进行繁体转简体转换
            df[col] = df[col].apply(
                lambda x: cc.convert(str(x)) if pd.notna(x) else x
            )
            print(f"已转换列 '{col}' 的繁体中文为简体中文")
        else:
            print(f"警告: 列 '{col}' 在CSV文件中不存在")

    # 保存回原文件，覆盖原数据
    df.to_csv(csv_file_path, index=False)
    print(f"已将转换后的数据保存到原文件: {csv_file_path}")


# 使用示例
if __name__ == "__main__":
    # 替换为你的CSV文件路径
    csv_file_path = "origindata/繁体/cleaned.csv"  # 请修改为实际的文件路径

    # 检查文件是否存在
    if not os.path.exists(csv_file_path):
        print(f"错误: 文件 {csv_file_path} 不存在")
    else:
        # 执行转换
        convert_csv_traditional_to_simplified(csv_file_path)
        print("繁简转换完成!")