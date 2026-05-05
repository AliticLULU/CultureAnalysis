import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings

warnings.filterwarnings('ignore')

# Set style
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['axes.unicode_minus'] = False
sns.set_style("whitegrid")

# Read data
df = pd.read_csv('all_data.csv')

# Author stats columns
author_cols = ['authorStats.diggCount', 'authorStats.followerCount']
labels = ['Author Digg Count', 'Author Follower Count']
colors = ['#FF6B6B', '#4ECDC4']

print(f"Data loaded: {len(df)} records\n")

# Calculate statistics
for col, label in zip(author_cols, labels):
    if col in df.columns:
        data = df[col].dropna()
        print(f"{label}:")
        print(f"  Mean:   {data.mean():>12,.0f}")
        print(f"  Median: {data.median():>12,.0f}")
        print(f"  Std:    {data.std():>12,.0f}")
        print(f"  Min:    {data.min():>12,.0f}")
        print(f"  Max:    {data.max():>12,.0f}")
        print(f"  Skewness: {data.skew():>10.2f}")
        print()

# ============ Elegant Figure ============
fig = plt.figure(figsize=(18, 10))
gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.3)

for idx, (col, label, color) in enumerate(zip(author_cols, labels, colors)):
    if col in df.columns:
        data = df[col].dropna()
        log_data = np.log1p(data)

        # ===== 1. Histogram with KDE (Log Scale) =====
        ax1 = fig.add_subplot(gs[idx, 0])

        n, bins, patches = ax1.hist(log_data, bins=40, color=color, alpha=0.7,
                                    edgecolor='white', linewidth=0.8, density=True)

        kde = stats.gaussian_kde(log_data)
        x_range = np.linspace(log_data.min(), log_data.max(), 200)
        ax1.plot(x_range, kde(x_range), color='#2C3E50', linewidth=2.5, label='KDE')

        log_mean = log_data.mean()
        log_median = log_data.median()
        ax1.axvline(log_mean, color='#E74C3C', linestyle='--', linewidth=2,
                    alpha=0.7, label=f'Mean: {np.expm1(log_mean):,.0f}')
        ax1.axvline(log_median, color='#2ECC71', linestyle='--', linewidth=2,
                    alpha=0.7, label=f'Median: {np.expm1(log_median):,.0f}')

        ax1.set_xlabel('Log(Value + 1)', fontsize=11)
        ax1.set_ylabel('Density', fontsize=11)
        ax1.set_title(f'{label}\nDistribution (Log Scale)', fontsize=13, fontweight='bold')
        ax1.legend(fontsize=9, framealpha=0.8)
        ax1.grid(True, alpha=0.3, linestyle='--')

        # ===== 2. Box Plot with Violin =====
        ax2 = fig.add_subplot(gs[idx, 1])

        parts = ax2.violinplot(log_data, positions=[0], vert=True,
                               showmeans=True, showmedians=True)

        for pc in parts['bodies']:
            pc.set_facecolor(color)
            pc.set_alpha(0.6)
        parts['cmeans'].set_color('#E74C3C')
        parts['cmedians'].set_color('#2ECC71')

        bp = ax2.boxplot(log_data, positions=[0], widths=0.3,
                         patch_artist=True, showfliers=True,
                         flierprops=dict(marker='o', markerfacecolor=color,
                                         markersize=4, alpha=0.5))
        bp['boxes'][0].set_facecolor('white')
        bp['boxes'][0].set_alpha(0.8)

        sample_size = min(200, len(log_data))
        indices = np.random.choice(len(log_data), sample_size, replace=False)
        ax2.scatter(np.zeros(sample_size) + np.random.normal(0, 0.04, sample_size),
                    log_data.iloc[indices], alpha=0.3, s=15, color='#2C3E50')

        ax2.set_ylabel('Log(Value + 1)', fontsize=11)
        ax2.set_title(f'{label}\nViolin & Box Plot', fontsize=13, fontweight='bold')
        ax2.set_xticks([])
        ax2.grid(True, alpha=0.3, linestyle='--', axis='y')

plt.suptitle('Author Statistics Distribution Analysis',
             fontsize=18, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('author_stats_distribution.png', dpi=300, bbox_inches='tight')
plt.show()

# ============ Combined Comparison ============
print("\nGenerating combined comparison chart...")
fig2, axes2 = plt.subplots(1, 2, figsize=(16, 7))

# 1. KDE comparison
ax = axes2[0]
for col, label, color in zip(author_cols, labels, colors):
    if col in df.columns:
        log_data = np.log1p(df[col].dropna())
        sns.kdeplot(data=log_data, label=label, color=color, linewidth=2.5, ax=ax)
        mean_val = log_data.mean()
        ax.axvline(mean_val, color=color, linestyle='--', alpha=0.4, linewidth=1.5)

ax.set_xlabel('Log(Value + 1)', fontsize=12)
ax.set_ylabel('Density', fontsize=12)
ax.set_title('KDE Comparison (Log Scale)', fontsize=14, fontweight='bold')
ax.legend(fontsize=11, framealpha=0.8)
ax.grid(True, alpha=0.3)

# 2. Scatter plot with correlation
ax = axes2[1]
if all(col in df.columns for col in author_cols):
    log_digg = np.log1p(df['authorStats.diggCount'])
    log_follower = np.log1p(df['authorStats.followerCount'])

    hb = ax.hexbin(log_digg, log_follower, gridsize=30, cmap='YlOrRd',
                   mincnt=1, alpha=0.8)

    corr, _ = stats.pearsonr(log_digg, log_follower)

    z = np.polyfit(log_digg, log_follower, 1)
    p = np.poly1d(z)
    x_line = np.linspace(log_digg.min(), log_digg.max(), 100)
    ax.plot(x_line, p(x_line), '--', color='#2C3E50', linewidth=2,
            label=f'Trend (r={corr:.3f})')

    plt.colorbar(hb, ax=ax, label='Count')
    ax.set_xlabel('Log(Digg Count + 1)', fontsize=12)
    ax.set_ylabel('Log(Follower Count + 1)', fontsize=12)
    ax.set_title('Author Digg vs Follower Count', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

plt.suptitle('Author Statistics Combined Analysis', fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('author_stats_comparison.png', dpi=300, bbox_inches='tight')
plt.show()

print(f"\nCharts saved:")
print(f"  1. author_stats_distribution.png - Distribution analysis (2x2)")
print(f"  2. author_stats_comparison.png - Combined comparison")
print(f"\nAnalysis complete!")