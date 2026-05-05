import pandas as pd
import numpy as np
from datetime import datetime


def comprehensive_statistics_analysis(file_path):
    """
    对包含spreadscore列的CSV文件进行综合统计分析
    """
    # 读取CSV文件
    df = pd.read_csv(file_path)

    # 检查必需列是否存在
    required_columns = ['spreadscore', 'stats.playCount', 'stats.diggCount', 'stats.commentCount', 'stats.shareCount']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"缺少必需的列: {col}")

    print(f"正在分析文件: {file_path}")
    print(f"数据行数: {len(df)}")
    print("=" * 60)

    # 要分析的列
    analysis_columns = {
        'spreadscore': '传播影响力得分',
        'stats.playCount': '播放数',
        'stats.diggCount': '点赞数',
        'stats.commentCount': '评论数',
        'stats.shareCount': '分享数'
    }

    # 存储统计结果
    stats_results = {}

    for col, desc in analysis_columns.items():
        data = df[col].dropna()  # 移除空值

        # 基本统计量
        max_val = data.max()
        min_val = data.min()
        mean_val = data.mean()
        median_val = data.median()
        sum_val = data.sum()

        # 其他统计指标
        std_val = data.std()  # 标准差
        var_val = data.var()  # 方差
        q25 = data.quantile(0.25)  # 第一四分位数
        q75 = data.quantile(0.75)  # 第三四分位数
        iqr = q75 - q25  # 四分位距
        skewness = data.skew()  # 偏度
        kurtosis = data.kurtosis()  # 峰度
        count_val = len(data)  # 计数
        unique_count = data.nunique()  # 唯一值数量
        mode_val = data.mode().iloc[0] if not data.mode().empty else "N/A"  # 众数

        stats_results[col] = {
            '描述': desc,
            '计数': count_val,
            '唯一值数': unique_count,
            '最大值': max_val,
            '最小值': min_val,
            '平均值': mean_val,
            '中位数': median_val,
            '总和': sum_val,
            '标准差': std_val,
            '方差': var_val,
            '第一四分位数': q25,
            '第三四分位数': q75,
            '四分位距(IQR)': iqr,
            '偏度': skewness,
            '峰度': kurtosis,
            '众数': mode_val
        }

    # 打印统计结果
    for col, stats_dict in stats_results.items():
        print(f"\n【{stats_dict['描述']} ({col})】")
        print("-" * 40)
        print(f"数据点数量: {stats_dict['计数']}")
        print(f"唯一值数量: {stats_dict['唯一值数']}")
        print(f"最大值: {stats_dict['最大值']:,.2f}")
        print(f"最小值: {stats_dict['最小值']:,.2f}")
        print(f"平均值: {stats_dict['平均值']:,.2f}")
        print(f"中位数: {stats_dict['中位数']:,.2f}")
        print(f"总和: {stats_dict['总和']:,.2f}")
        print(f"标准差: {stats_dict['标准差']:,.2f}")
        print(f"方差: {stats_dict['方差']:,.2f}")
        print(f"第一四分位数 (Q1): {stats_dict['第一四分位数']:,.2f}")
        print(f"第三四分位数 (Q3): {stats_dict['第三四分位数']:,.2f}")
        print(f"四分位距 (IQR): {stats_dict['四分位距(IQR)']:,.2f}")
        print(f"偏度: {stats_dict['偏度']:,.3f}")
        print(f"峰度: {stats_dict['峰度']:,.3f}")
        print(f"众数: {stats_dict['众数']}")

        # 添加一些解释性信息
        cv = (stats_dict['标准差'] / stats_dict['平均值']) * 100 if stats_dict['平均值'] != 0 else 0
        print(f"变异系数: {cv:.2f}%")

        if abs(stats_dict['偏度']) < 0.5:
            skew_desc = "近似对称"
        elif stats_dict['偏度'] > 0.5:
            skew_desc = "右偏（正偏）"
        else:
            skew_desc = "左偏（负偏）"
        print(f"分布形态: {skew_desc}")

        print()

    # 计算相关性矩阵
    print("=" * 60)
    print("【各指标间相关性分析】")
    print("-" * 40)
    correlation_cols = ['spreadscore', 'stats.playCount', 'stats.diggCount', 'stats.commentCount', 'stats.shareCount']
    correlation_matrix = df[correlation_cols].corr()
    print(correlation_matrix.round(3))

    # 计算每列的异常值数量（使用IQR方法）
    print("\n【异常值检测（基于IQR方法）】")
    print("-" * 40)
    for col, stats_dict in stats_results.items():
        Q1 = stats_dict['第一四分位数']
        Q3 = stats_dict['第三四分位数']
        IQR = stats_dict['四分位距(IQR)']
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        outlier_count = len(outliers)
        outlier_percentage = (outlier_count / len(df)) * 100

        print(f"{stats_dict['描述']}: {outlier_count} 个异常值 ({outlier_percentage:.2f}%)")

    # 生成详细的文本报告
    report_text = generate_detailed_report(stats_results, correlation_matrix, df, analysis_columns)

    # 保存报告到txt文件
    txt_output_file = "origindata/法语/statistics.txt"
    with open(txt_output_file, 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(f"\n详细统计报告已保存至: {txt_output_file}")

    return stats_results, correlation_matrix


def generate_detailed_report(stats_results, correlation_matrix, df, analysis_columns):
    """
    生成详细的统计报告文本
    """
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("中国传统文化海外传播数据分析报告")
    report_lines.append("=" * 80)
    report_lines.append(f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"数据集大小: {len(df)} 行")
    report_lines.append("")

    # 基本信息
    report_lines.append("【基本信息】")
    report_lines.append("-" * 50)
    for col, desc in analysis_columns.items():
        report_lines.append(f"{desc} ({col}): 共 {stats_results[col]['计数']} 个数据点")
    report_lines.append("")

    # 各项指标详细统计
    report_lines.append("【各项指标详细统计】")
    report_lines.append("-" * 50)

    for col, stats_dict in stats_results.items():
        report_lines.append(f"\n【{stats_dict['描述']} ({col})】")
        report_lines.append("-" * 40)
        report_lines.append(f"数据点数量: {stats_dict['计数']}")
        report_lines.append(f"唯一值数量: {stats_dict['唯一值数']}")
        report_lines.append(f"最大值: {stats_dict['最大值']:,.2f}")
        report_lines.append(f"最小值: {stats_dict['最小值']:,.2f}")
        report_lines.append(f"平均值: {stats_dict['平均值']:,.2f}")
        report_lines.append(f"中位数: {stats_dict['中位数']:,.2f}")
        report_lines.append(f"总和: {stats_dict['总和']:,.2f}")
        report_lines.append(f"标准差: {stats_dict['标准差']:,.2f}")
        report_lines.append(f"方差: {stats_dict['方差']:,.2f}")
        report_lines.append(f"第一四分位数 (Q1): {stats_dict['第一四分位数']:,.2f}")
        report_lines.append(f"第三四分位数 (Q3): {stats_dict['第三四分位数']:,.2f}")
        report_lines.append(f"四分位距 (IQR): {stats_dict['四分位距(IQR)']:,.2f}")
        report_lines.append(f"偏度: {stats_dict['偏度']:,.3f}")
        report_lines.append(f"峰度: {stats_dict['峰度']:,.3f}")
        report_lines.append(f"众数: {stats_dict['众数']}")

        # 添加解释性信息
        cv = (stats_dict['标准差'] / stats_dict['平均值']) * 100 if stats_dict['平均值'] != 0 else 0
        report_lines.append(f"变异系数: {cv:.2f}%")

        if abs(stats_dict['偏度']) < 0.5:
            skew_desc = "近似对称"
        elif stats_dict['偏度'] > 0.5:
            skew_desc = "右偏（正偏）"
        else:
            skew_desc = "左偏（负偏）"
        report_lines.append(f"分布形态: {skew_desc}")

    # 相关性分析
    report_lines.append("\n\n【各指标间相关性分析】")
    report_lines.append("-" * 50)
    report_lines.append("相关性矩阵:")
    report_lines.append(str(correlation_matrix.round(3)))

    # 异常值分析
    report_lines.append("\n\n【异常值检测（基于IQR方法）】")
    report_lines.append("-" * 50)
    for col, stats_dict in stats_results.items():
        Q1 = stats_dict['第一四分位数']
        Q3 = stats_dict['第三四分位数']
        IQR = stats_dict['四分位距(IQR)']
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        outlier_count = len(outliers)
        outlier_percentage = (outlier_count / len(df)) * 100

        report_lines.append(f"{stats_dict['描述']}: {outlier_count} 个异常值 ({outlier_percentage:.2f}%)")

    # 综合分析总结
    report_lines.append("\n\n【综合分析总结】")
    report_lines.append("-" * 50)

    # 找出最大值对应的指标
    max_values = {col: stats_dict['最大值'] for col, stats_dict in stats_results.items()}
    max_col = max(max_values, key=max_values.get)
    report_lines.append(f"最大值出现在: {stats_results[max_col]['描述']} ({max_col}): {max_values[max_col]:,.2f}")

    # 找出最小值对应的指标
    min_values = {col: stats_dict['最小值'] for col, stats_dict in stats_results.items()}
    min_col = min(min_values, key=min_values.get)
    report_lines.append(f"最小值出现在: {stats_results[min_col]['描述']} ({min_col}): {min_values[min_col]:,.2f}")

    # 找出平均值最高的指标
    mean_values = {col: stats_dict['平均值'] for col, stats_dict in stats_results.items()}
    mean_col = max(mean_values, key=mean_values.get)
    report_lines.append(f"平均值最高的是: {stats_results[mean_col]['描述']} ({mean_col}): {mean_values[mean_col]:,.2f}")

    # 找出变异系数最大的指标（相对波动最大）
    cv_values = {}
    for col, stats_dict in stats_results.items():
        cv = (stats_dict['标准差'] / stats_dict['平均值']) * 100 if stats_dict['平均值'] != 0 else 0
        cv_values[col] = cv
    cv_max_col = max(cv_values, key=cv_values.get)
    report_lines.append(
        f"相对波动最大的是: {stats_results[cv_max_col]['描述']} ({cv_max_col}): 变异系数 {cv_values[cv_max_col]:.2f}%")

    # 找出偏度绝对值最大的指标（最不对称）
    skew_values = {col: abs(stats_dict['偏度']) for col, stats_dict in stats_results.items()}
    skew_max_col = max(skew_values, key=skew_values.get)
    original_skew = stats_results[skew_max_col]['偏度']
    direction = "右偏" if original_skew > 0 else "左偏"
    report_lines.append(
        f"分布最不对称的是: {stats_results[skew_max_col]['描述']} ({skew_max_col}): {direction}, 偏度 {original_skew:.3f}")

    # 找出spreadscore与其它指标的相关性最强的
    spread_corr = correlation_matrix.loc['spreadscore'].drop('spreadscore')
    strongest_corr_col = spread_corr.abs().idxmax()
    strongest_corr_value = spread_corr[strongest_corr_col]
    report_lines.append(
        f"与传播影响力得分(spreadscore)相关性最强的是: {stats_results[strongest_corr_col]['描述']} ({strongest_corr_col}): 相关系数 {strongest_corr_value:.3f}")

    report_lines.append("\n报告生成完毕。")

    return "\n".join(report_lines)


# 使用示例
if __name__ == "__main__":
    # 指定包含spreadscore列的CSV文件路径
    csv_file_path = 'origindata/法语/cleaned.csv'  # 替换为实际的文件路径

    try:
        stats_results, corr_matrix = comprehensive_statistics_analysis(csv_file_path)

        print(f"\n分析完成！共分析了 {len(stats_results)} 个指标。")
        print("详细报告已保存至 statistics.txt 文件。")

    except FileNotFoundError:
        print(f"错误: 找不到文件 {csv_file_path}")
    except Exception as e:
        print(f"分析过程中出现错误: {e}")
        import traceback

        traceback.print_exc()