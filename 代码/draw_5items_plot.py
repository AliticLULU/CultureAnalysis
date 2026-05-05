import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# 设置基本样式 - 使用英文避免乱码
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['axes.unicode_minus'] = False
sns.set_style("whitegrid")
sns.set_palette("husl")

# 读取数据（请替换为您的文件路径）
# df = pd.read_csv('your_data.csv')

# 如果没有实际数据，使用示例数据
print("Loading sample data for demonstration...")
np.random.seed(42)
n_samples = 100
sample_data = {
    'diggCount': np.random.exponential(500, n_samples).astype(int),
    'shareCount': np.random.exponential(100, n_samples).astype(int),
    'playCount': np.random.exponential(5000, n_samples).astype(int),
    'collectCount': np.random.exponential(200, n_samples).astype(int),
    'commentCount': np.random.exponential(150, n_samples).astype(int)
}
df = pd.DataFrame(sample_data)

# 提取传播力相关指标
metrics_list = ['diggCount', 'shareCount', 'playCount', 'collectCount', 'commentCount']
analysis_df = df[metrics_list].copy()

print(f"Data loaded successfully: {len(analysis_df)} samples")
print("\nFirst 5 rows:")
print(analysis_df.head())

# 基本统计信息
print("\n" + "="*60)
print("BASIC STATISTICS")
print("="*60)
print(analysis_df.describe())

def create_figure(title, filename, figsize=(12, 8)):
    """创建图表并保存，然后显示"""
    fig = plt.figure(figsize=figsize)
    return fig

def show_and_save(fig, filename):
    """显示图表并保存"""
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()
    print(f"Chart saved as: {filename}")
    input("Press Enter to continue to next chart...")
    plt.close()

# ============ 图表1：箱线图 ============
print("\n" + "="*60)
print("Chart 1: Box Plot")
print("="*60)
fig1, ax1 = plt.subplots(figsize=(12, 8))
# 对数变换
data_for_box = np.log1p(analysis_df)
bp = sns.boxplot(data=data_for_box, ax=ax1, palette="Set3", linewidth=2)
ax1.set_title('Box Plot of Video Metrics (Log Transformed)',
              fontsize=16, fontweight='bold', pad=15)
ax1.set_ylabel('Log(Value + 1)', fontsize=13)
ax1.set_xlabel('Metrics', fontsize=13)
ax1.tick_params(axis='x', labelsize=15, rotation=15)
ax1.grid(True, alpha=0.3, linestyle='--')

# 添加统计信息文本
stats_text = "Statistics Summary:\n"
for col in analysis_df.columns:
    stats_text += f"{col}: median={analysis_df[col].median():.0f}, "
    stats_text += f"max={analysis_df[col].max()}\n"
ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes,
         fontsize=14, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

show_and_save(fig1, '01_boxplot.png')

# ============ 图表2：小提琴图 ============
print("\n" + "="*60)
print("Chart 2: Violin Plot")
print("="*60)
fig2, ax2 = plt.subplots(figsize=(12, 8))
vp = sns.violinplot(data=data_for_box, ax=ax2, palette="Set2", inner="quartile", linewidth=2)
ax2.set_title('Distribution Density of Video Metrics',
              fontsize=16, fontweight='bold', pad=15)
ax2.set_ylabel('Log(Value + 1)', fontsize=13)
ax2.set_xlabel('Metrics', fontsize=13)
ax2.tick_params(axis='x', labelsize=11, rotation=15)
ax2.grid(True, alpha=0.3, linestyle='--')

show_and_save(fig2, '02_violin_plot.png')

# ============ 图表3：密度分布曲线 ============
print("\n" + "="*60)
print("Chart 3: Density Curves")
print("="*60)
fig3, ax3 = plt.subplots(figsize=(12, 8))
colors = sns.color_palette("husl", len(metrics_list))
for i, col in enumerate(analysis_df.columns):
    log_data = np.log1p(analysis_df[col])
    sns.kdeplot(data=log_data, label=col, ax=ax3, color=colors[i],
                linewidth=3, alpha=0.8)
ax3.set_title('Distribution Density Curves (Log Transformed)',
              fontsize=16, fontweight='bold', pad=15)
ax3.set_xlabel('Log(Value + 1)', fontsize=13)
ax3.set_ylabel('Density', fontsize=13)
ax3.legend(loc='upper right', fontsize=11, framealpha=0.8, edgecolor='black')
ax3.grid(True, alpha=0.3, linestyle='--')

# 添加均值线
for i, col in enumerate(analysis_df.columns):
    mean_val = np.log1p(analysis_df[col]).mean()
    ax3.axvline(x=mean_val, color=colors[i], linestyle='--', alpha=0.5, linewidth=1)

show_and_save(fig3, '03_density_curves.png')

# ============ 图表4：相关性热力图 ============
print("\n" + "="*60)
print("Chart 4: Correlation Heatmap")
print("="*60)
fig4, ax4 = plt.subplots(figsize=(10, 8))
correlation_matrix = analysis_df.corr(method='spearman')
mask = np.triu(np.ones_like(correlation_matrix, dtype=bool), k=1)
hm = sns.heatmap(correlation_matrix, annot=True, fmt='.3f', cmap='RdYlBu_r',
                 center=0.5, square=True, linewidths=1, cbar_kws={"shrink": 0.8},
                 mask=mask, ax=ax4, annot_kws={'size': 12, 'weight': 'bold'},
                 vmin=0, vmax=1)
ax4.set_title('Spearman Correlation Matrix',
              fontsize=16, fontweight='bold', pad=15)
ax4.tick_params(labelsize=11)

show_and_save(fig4, '04_correlation_heatmap.png')

# ============ 图表5：散点图矩阵 ============
print("\n" + "="*60)
print("Chart 5: Scatter Plot Matrix")
print("="*60)
# 选择几个关键指标
key_metrics = ['playCount', 'diggCount', 'shareCount']
fig5, axes = plt.subplots(2, 2, figsize=(14, 12))
axes = axes.flatten()

# 5.1: 播放量 vs 点赞数
ax = axes[0]
scatter = ax.scatter(np.log1p(analysis_df['playCount']),
                      np.log1p(analysis_df['diggCount']),
                      c=np.log1p(analysis_df['shareCount']),
                      cmap='viridis', alpha=0.6, s=60, edgecolors='black', linewidth=0.5)
ax.set_xlabel('Log(Play Count)', fontsize=12)
ax.set_ylabel('Log(Digg Count)', fontsize=12)
ax.set_title('Play Count vs Digg Count', fontsize=14, fontweight='bold')
plt.colorbar(scatter, ax=ax, label='Log(Share Count)')
ax.grid(True, alpha=0.3)

# 5.2: 播放量 vs 分享数
ax = axes[1]
scatter = ax.scatter(np.log1p(analysis_df['playCount']),
                      np.log1p(analysis_df['shareCount']),
                      c=np.log1p(analysis_df['commentCount']),
                      cmap='plasma', alpha=0.6, s=60, edgecolors='black', linewidth=0.5)
ax.set_xlabel('Log(Play Count)', fontsize=12)
ax.set_ylabel('Log(Share Count)', fontsize=12)
ax.set_title('Play Count vs Share Count', fontsize=14, fontweight='bold')
plt.colorbar(scatter, ax=ax, label='Log(Comment Count)')
ax.grid(True, alpha=0.3)

# 5.3: 点赞数 vs 评论数
ax = axes[2]
scatter = ax.scatter(np.log1p(analysis_df['diggCount']),
                      np.log1p(analysis_df['commentCount']),
                      c=np.log1p(analysis_df['collectCount']),
                      cmap='coolwarm', alpha=0.6, s=60, edgecolors='black', linewidth=0.5)
ax.set_xlabel('Log(Digg Count)', fontsize=12)
ax.set_ylabel('Log(Comment Count)', fontsize=12)
ax.set_title('Digg Count vs Comment Count', fontsize=14, fontweight='bold')
plt.colorbar(scatter, ax=ax, label='Log(Collect Count)')
ax.grid(True, alpha=0.3)

# 5.4: 收藏数 vs 点赞数
ax = axes[3]
scatter = ax.scatter(np.log1p(analysis_df['collectCount']),
                      np.log1p(analysis_df['diggCount']),
                      c=np.log1p(analysis_df['shareCount']),
                      cmap='magma', alpha=0.6, s=60, edgecolors='black', linewidth=0.5)
ax.set_xlabel('Log(Collect Count)', fontsize=12)
ax.set_ylabel('Log(Digg Count)', fontsize=12)
ax.set_title('Collect Count vs Digg Count', fontsize=14, fontweight='bold')
plt.colorbar(scatter, ax=ax, label='Log(Share Count)')
ax.grid(True, alpha=0.3)

plt.suptitle('Scatter Plot Matrix of Key Metrics', fontsize=16, fontweight='bold', y=1.02)
show_and_save(fig5, '05_scatter_plots.png')

# ============ 图表6：累计分布曲线 ============
print("\n" + "="*60)
print("Chart 6: Cumulative Distribution (Lorenz Curve)")
print("="*60)
fig6, ax6 = plt.subplots(figsize=(12, 8))
for i, col in enumerate(analysis_df.columns):
    sorted_data = np.sort(analysis_df[col])[::-1]
    cumulative_share = np.cumsum(sorted_data) / np.sum(sorted_data)
    x_values = np.arange(1, len(cumulative_share)+1)/len(cumulative_share)*100
    ax6.plot(x_values, cumulative_share*100, label=col,
             linewidth=2.5, marker='o', markersize=3, markevery=10)

# 完全均匀分布线
ax6.plot([0, 100], [0, 100], 'k--', alpha=0.5, linewidth=2, label='Perfect Equality')
ax6.set_xlabel('Cumulative % of Videos', fontsize=13)
ax6.set_ylabel('Cumulative % of Metric', fontsize=13)
ax6.set_title('Concentration Analysis (Lorenz Curves)',
              fontsize=16, fontweight='bold', pad=15)
ax6.legend(loc='lower right', fontsize=11, framealpha=0.8)
ax6.grid(True, alpha=0.3, linestyle='--')
ax6.set_xlim(0, 100)
ax6.set_ylim(0, 100)

# 计算基尼系数
def gini_coefficient(x):
    """计算基尼系数"""
    sorted_x = np.sort(x)
    n = len(x)
    index = np.arange(1, n+1)
    return (2 * np.sum(index * sorted_x)) / (n * np.sum(sorted_x)) - (n + 1) / n

gini_text = "Gini Coefficients:\n"
for col in analysis_df.columns:
    gini = gini_coefficient(analysis_df[col])
    gini_text += f"{col}: {gini:.3f}\n"
ax6.text(0.02, 0.98, gini_text, transform=ax6.transAxes,
         fontsize=10, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))

show_and_save(fig6, '06_lorenz_curves.png')

# ============ 图表7：均值和中位数对比 ============
print("\n" + "="*60)
print("Chart 7: Mean vs Median Comparison")
print("="*60)
fig7, ax7 = plt.subplots(figsize=(12, 8))
x = np.arange(len(metrics_list))
width = 0.35

means = analysis_df.mean()
medians = analysis_df.median()

bars1 = ax7.bar(x - width/2, means.values, width, label='Mean',
                color='#FF6B6B', alpha=0.8, edgecolor='black', linewidth=1.5)
bars2 = ax7.bar(x + width/2, medians.values, width, label='Median',
                color='#4ECDC4', alpha=0.8, edgecolor='black', linewidth=1.5)

ax7.set_xlabel('Metrics', fontsize=13)
ax7.set_ylabel('Value', fontsize=13)
ax7.set_title('Mean vs Median Comparison', fontsize=16, fontweight='bold', pad=15)
ax7.set_xticks(x)
ax7.set_xticklabels(metrics_list, rotation=15, fontsize=11)
ax7.legend(fontsize=12, loc='upper left')
ax7.grid(True, alpha=0.3, axis='y', linestyle='--')

# 添加数值标签
for bar in bars1:
    height = bar.get_height()
    ax7.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:,.0f}', ha='center', va='bottom', fontsize=9)
for bar in bars2:
    height = bar.get_height()
    ax7.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:,.0f}', ha='center', va='bottom', fontsize=9)

show_and_save(fig7, '07_mean_median_comparison.png')

# ============ 图表8：变异系数和偏度分析 ============
print("\n" + "="*60)
print("Chart 8: Coefficient of Variation & Skewness")
print("="*60)
fig8, (ax8a, ax8b) = plt.subplots(1, 2, figsize=(16, 8))

# 变异系数
cv = analysis_df.std() / analysis_df.mean()
colors_cv = ['#FF6B6B' if x > 1.5 else '#FFEAA7' if x > 1 else '#95E1D3' for x in cv.values]
bars_cv = ax8a.barh(np.arange(len(cv)), cv.values, color=colors_cv,
                      edgecolor='black', linewidth=1.5)
ax8a.set_yticks(np.arange(len(cv)))
ax8a.set_yticklabels(cv.index, fontsize=11)
ax8a.set_xlabel('Coefficient of Variation', fontsize=12)
ax8a.set_title('Dispersion Analysis', fontsize=14, fontweight='bold')
ax8a.axvline(x=1, color='red', linestyle='--', alpha=0.7, linewidth=2, label='CV=1 Threshold')
ax8a.legend(fontsize=10)
ax8a.grid(True, alpha=0.3)

for bar, val in zip(bars_cv, cv.values):
    ax8a.text(val + 0.05, bar.get_y() + bar.get_height()/2.,
              f'{val:.2f}', va='center', fontsize=10, fontweight='bold')

# 偏度
skewness = analysis_df.skew()
colors_skew = ['#FF6B6B' if x > 2 else '#FFEAA7' if x > 0 else '#95E1D3' for x in skewness.values]
bars_skew = ax8b.barh(np.arange(len(skewness)), skewness.values, color=colors_skew,
                        edgecolor='black', linewidth=1.5)
ax8b.set_yticks(np.arange(len(skewness)))
ax8b.set_yticklabels(skewness.index, fontsize=11)
ax8b.set_xlabel('Skewness', fontsize=12)
ax8b.set_title('Distribution Symmetry Analysis', fontsize=14, fontweight='bold')
ax8b.axvline(x=0, color='black', linestyle='-', alpha=0.5)
ax8b.axvline(x=1, color='orange', linestyle='--', alpha=0.7, label='High Skewness (>1)')
ax8b.legend(fontsize=10)
ax8b.grid(True, alpha=0.3)

for bar, val in zip(bars_skew, skewness.values):
    ax8b.text(val + 0.05, bar.get_y() + bar.get_height()/2.,
              f'{val:.2f}', va='center', fontsize=10, fontweight='bold')

plt.suptitle('Statistical Properties Analysis', fontsize=16, fontweight='bold', y=1.02)
show_and_save(fig8, '08_cv_skewness.png')

# ============ 图表9：分位数分析 ============
print("\n" + "="*60)
print("Chart 9: Quantile Analysis")
print("="*60)
fig9, ax9 = plt.subplots(figsize=(14, 8))
percentiles = [10, 25, 50, 75, 90]
quantile_data = []
for col in analysis_df.columns:
    quantile_data.append(np.percentile(analysis_df[col], percentiles))
quantile_df = pd.DataFrame(quantile_data, index=metrics_list,
                           columns=[f'P{p}' for p in percentiles])

# 绘制分组条形图
x = np.arange(len(metrics_list))
width = 0.15
for i, (p, color) in enumerate(zip(quantile_df.columns,
                                   ['#FF6B6B', '#FFA07A', '#4ECDC4', '#45B7D1', '#96CEB4'])):
    bars = ax9.bar(x + i*width, quantile_df[p], width, label=p,
                   color=color, alpha=0.8, edgecolor='black', linewidth=1)
    # 添加数值标签（只在P50上）
    if p == 'P50':
        for bar, val in zip(bars, quantile_df[p]):
            ax9.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                     f'{val:,.0f}', ha='center', va='bottom', fontsize=8)

ax9.set_xlabel('Metrics', fontsize=13)
ax9.set_ylabel('Value', fontsize=13)
ax9.set_title('Quantile Distribution Analysis', fontsize=16, fontweight='bold', pad=15)
ax9.set_xticks(x + width*2)
ax9.set_xticklabels(metrics_list, rotation=15, fontsize=11)
ax9.legend(title='Percentiles', fontsize=10, loc='upper left')
ax9.grid(True, alpha=0.3, axis='y', linestyle='--')
ax9.set_yscale('log')  # 对数刻度以便更好显示

show_and_save(fig9, '09_quantile_analysis.png')

# ============ 图表10：雷达图 ============
print("\n" + "="*60)
print("Chart 10: Radar Chart")
print("="*60)
fig10, ax10 = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

# 归一化数据
normalized_df = (np.log1p(analysis_df) - np.log1p(analysis_df).min()) / \
                (np.log1p(analysis_df).max() - np.log1p(analysis_df).min())
mean_normalized = normalized_df.mean()
median_normalized = normalized_df.median()
max_normalized = normalized_df.max()
min_normalized = normalized_df.min()

angles = np.linspace(0, 2 * np.pi, len(metrics_list), endpoint=False).tolist()
angles += angles[:1]

# 绘制多层数据
mean_values = mean_normalized.values.tolist() + [mean_normalized.values[0]]
median_values = median_normalized.values.tolist() + [median_normalized.values[0]]
max_values = max_normalized.values.tolist() + [max_normalized.values[0]]
min_values = min_normalized.values.tolist() + [min_normalized.values[0]]

ax10.fill(angles, max_values, alpha=0.1, color='#FF6B6B')
ax10.plot(angles, max_values, 'o-', color='#FF6B6B', linewidth=1.5, markersize=6, label='Max')
ax10.fill(angles, mean_values, alpha=0.2, color='#4ECDC4')
ax10.plot(angles, mean_values, 'o-', color='#4ECDC4', linewidth=2, markersize=6, label='Mean')
ax10.fill(angles, median_values, alpha=0.2, color='#45B7D1')
ax10.plot(angles, median_values, 'o-', color='#45B7D1', linewidth=2, markersize=6, label='Median')
ax10.fill(angles, min_values, alpha=0.1, color='#96CEB4')
ax10.plot(angles, min_values, 'o-', color='#96CEB4', linewidth=1.5, markersize=6, label='Min')

ax10.set_xticks(angles[:-1])
ax10.set_xticklabels(metrics_list, fontsize=11)
ax10.set_ylim(0, 1)
ax10.set_title('Comprehensive Metrics Comparison (Normalized)',
               fontsize=16, fontweight='bold', pad=25)
ax10.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)
ax10.grid(True, alpha=0.3)

show_and_save(fig10, '10_radar_chart.png')

# ============ 最终统计汇总 ============
print("\n" + "="*60)
print("FINAL SUMMARY STATISTICS")
print("="*60)
summary_df = pd.DataFrame({
    'Mean': analysis_df.mean(),
    'Median': analysis_df.median(),
    'Std': analysis_df.std(),
    'CV': analysis_df.std() / analysis_df.mean(),
    'Skewness': analysis_df.skew(),
    'Kurtosis': analysis_df.kurtosis(),
    'Min': analysis_df.min(),
    'Max': analysis_df.max(),
    'P25': analysis_df.quantile(0.25),
    'P75': analysis_df.quantile(0.75)
})
print(summary_df.round(2))

print("\nAll charts have been generated and saved!")
print("Files created:")
for i in range(1, 11):
    print(f"  {i:02d}_*.png")