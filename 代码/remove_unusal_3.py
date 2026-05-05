import pandas as pd

# 1. 读取 CSV 文件
# 请确保文件路径正确
input_file = 'origindata/越南语/cleaned.csv'
output_file = 'origindata/越南语/cleaned.csv'  # 这里直接覆盖原文件，如果想备份可以改成新文件名

try:
    df = pd.read_csv(input_file)
    print(f"✅ 成功读取文件，原始列数: {len(df.columns)}")

    # 2. 定义需要删除的列
    columns_to_drop = [
        'author.signature',
        'authorStats.followingCount',
        'stickersOnItem.StickerText'
    ]

    # 3. 执行删除操作
    # errors='ignore' 的作用是：如果某些列不存在，程序不会报错，而是自动跳过
    df.drop(columns=columns_to_drop, errors='ignore', inplace=True)

    # 4. 保存回 CSV 文件
    df.to_csv(output_file, index=False, encoding='utf-8')

    print(f"✅ 删除完成，剩余列数: {len(df.columns)}")
    print(f"💾 文件已保存至: {output_file}")
    print(f"📋 当前保留的列: {list(df.columns)}")

except Exception as e:
    print(f"❌ 发生错误: {e}")