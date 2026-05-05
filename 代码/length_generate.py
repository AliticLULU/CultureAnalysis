import pandas as pd

# 读取CSV文件
df = pd.read_csv('all_data.csv')

# 解析日期列
df['createTime_date'] = pd.to_datetime(df['createTime_date'])

# 设置截至时间
end_date = pd.to_datetime('2026-04-27')

# 计算天数差
df['length'] = (end_date - df['createTime_date']).dt.days

# 保存文件
df.to_csv('all_data.csv', index=False)

print(f"计算完成！共处理 {len(df)} 条数据")
print(f"\nlength 列统计信息：")
print(f"  均值: {df['length'].mean():.1f} 天")
print(f"  中位数: {df['length'].median():.1f} 天")
print(f"  最小值: {df['length'].min()} 天")
print(f"  最大值: {df['length'].max()} 天")
print(f"\n结果已保存到 all_data.csv 的 length 列")