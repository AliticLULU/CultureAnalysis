import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

warnings.filterwarnings('ignore')

# 设置样式
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 300
sns.set_style("whitegrid")
sns.set_palette("husl")


class VideoSpreadScorer:
    """视频传播力评分系统"""

    def __init__(self, metrics_list=None):
        """
        初始化评分器

        Parameters:
        -----------
        metrics_list : list
            指标列表，默认使用5个TikTok指标
        """
        if metrics_list is None:
            self.metrics_list = ['playCount', 'diggCount', 'shareCount',
                                 'commentCount', 'collectCount']
        else:
            self.metrics_list = metrics_list

        # 定义三种权重方案
        self.weight_schemes = {
            'balanced': {  # 均衡型
                'playCount': 0.25,
                'diggCount': 0.25,
                'shareCount': 0.20,
                'commentCount': 0.15,
                'collectCount': 0.15
            },
            'interaction': {  # 互动型
                'playCount': 0.15,
                'diggCount': 0.30,
                'shareCount': 0.20,
                'commentCount': 0.20,
                'collectCount': 0.15
            },
            'diffusion': {  # 传播型
                'playCount': 0.20,
                'diggCount': 0.15,
                'shareCount': 0.35,
                'commentCount': 0.10,
                'collectCount': 0.20
            }
        }

        self.scaler = MinMaxScaler()
        self.is_fitted = False

    def fit(self, df):
        """
        拟合评分器，计算归一化参数

        Parameters:
        -----------
        df : DataFrame
            包含指标的数据
        """
        # Step 1: 对数变换
        df_log = np.log1p(df[self.metrics_list])

        # Step 2: 拟合归一化器
        self.scaler.fit(df_log)

        # 存储统计信息用于后续分析
        self.stats_ = {
            'log_mean': df_log.mean(),
            'log_std': df_log.std(),
            'log_median': df_log.median(),
            'original_mean': df[self.metrics_list].mean(),
            'original_median': df[self.metrics_list].median()
        }

        self.is_fitted = True
        print("Scorer fitted successfully!")
        print(f"Metrics used: {self.metrics_list}")

    def score(self, df, scheme='balanced', return_details=False):
        """
        计算传播力得分

        Parameters:
        -----------
        df : DataFrame
            包含指标的数据
        scheme : str
            权重方案: 'balanced', 'interaction', 'diffusion'
        return_details : bool
            是否返回详细的分步计算结果

        Returns:
        --------
        scores : array-like
            传播力得分 (0-100)
        details : DataFrame (if return_details=True)
            详细的计算过程
        """
        if not self.is_fitted:
            raise ValueError("Scorer not fitted. Call fit() first.")

        if scheme not in self.weight_schemes:
            raise ValueError(f"Unknown scheme: {scheme}. Use {list(self.weight_schemes.keys())}")

        weights = self.weight_schemes[scheme]

        # Step 1: 对数变换
        df_log = np.log1p(df[self.metrics_list])

        # Step 2: 归一化
        df_normalized = pd.DataFrame(
            self.scaler.transform(df_log),
            columns=self.metrics_list,
            index=df.index
        )

        # Step 3 & 4: 加权求和
        scores = np.zeros(len(df))
        for metric, weight in weights.items():
            scores += df_normalized[metric].values * weight

        # 映射到0-100分
        scores = scores * 100

        if return_details:
            details = pd.DataFrame({
                'video_id': df.index,
                'final_score': scores,
                'rating_level': self.get_rating_level(scores)
            })

            # 添加各步骤的中间结果
            for metric in self.metrics_list:
                details[f'{metric}_original'] = df[metric]
                details[f'{metric}_log_transformed'] = df_log[metric]
                details[f'{metric}_normalized'] = df_normalized[metric]
                details[f'{metric}_weighted'] = df_normalized[metric] * weights[metric] * 100

            return scores, details

        return scores

    def get_rating_level(self, scores):
        """获取评级"""
        conditions = [
            scores >= 80,
            scores >= 60,
            scores >= 40,
            scores >= 20,
            scores >= 0
        ]
        choices = ['A', 'B', 'C', 'D', 'E']

        if isinstance(scores, (int, float)):
            for condition, choice in zip(conditions, choices):
                if condition:
                    return choice
            return 'E'
        else:
            return pd.cut(scores, bins=[-1, 20, 40, 60, 80, 101],
                          labels=['E', 'D', 'C', 'B', 'A'])

    def analyze_scores(self, df, scores):
        """
        分析评分结果
        """
        print("\n" + "=" * 60)
        print("SCORE DISTRIBUTION ANALYSIS")
        print("=" * 60)

        print(f"\nScore Statistics:")
        print(f"  Mean: {np.mean(scores):.2f}")
        print(f"  Median: {np.median(scores):.2f}")
        print(f"  Std: {np.std(scores):.2f}")
        print(f"  Min: {np.min(scores):.2f}")
        print(f"  Max: {np.max(scores):.2f}")

        # 评级分布
        ratings = self.get_rating_level(scores)
        rating_counts = pd.Series(ratings).value_counts().sort_index()
        print(f"\nRating Distribution:")
        for rating in ['A', 'B', 'C', 'D', 'E']:
            count = rating_counts.get(rating, 0)
            print(f"  Level {rating}: {count} videos ({count / len(scores) * 100:.1f}%)")

        # 各指标贡献度分析
        print(f"\nMetric Contribution Analysis (Top 20% vs Bottom 20%):")
        top_idx = np.argsort(scores)[-int(len(scores) * 0.2):]
        bottom_idx = np.argsort(scores)[:int(len(scores) * 0.2)]

        for metric in self.metrics_list:
            top_avg = df[metric].iloc[top_idx].mean()
            bottom_avg = df[metric].iloc[bottom_idx].mean()
            ratio = top_avg / bottom_avg if bottom_avg > 0 else float('inf')
            print(f"  {metric}: Top avg={top_avg:.1f}, Bottom avg={bottom_avg:.1f}, Ratio={ratio:.1f}x")

    def visualize_scores(self, df, scores, scheme_name):
        """
        可视化评分结果
        """
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))

        # 1. 分数分布直方图
        ax = axes[0, 0]
        ax.hist(scores, bins=30, color='steelblue', edgecolor='black', alpha=0.7)
        ax.axvline(np.mean(scores), color='red', linestyle='--', label=f'Mean: {np.mean(scores):.1f}')
        ax.axvline(np.median(scores), color='green', linestyle='--', label=f'Median: {np.median(scores):.1f}')
        ax.set_xlabel('Spread Score')
        ax.set_ylabel('Frequency')
        ax.set_title(f'Score Distribution ({scheme_name})')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 2. 评级饼图
        ax = axes[0, 1]
        ratings = self.get_rating_level(scores)
        rating_counts = pd.Series(ratings).value_counts().sort_index()
        colors = ['#FF6B6B', '#FFA07A', '#4ECDC4', '#45B7D1', '#96CEB4']
        ax.pie(rating_counts.values, labels=rating_counts.index, autopct='%1.1f%%',
               colors=colors, startangle=90)
        ax.set_title('Rating Distribution')

        # 3. 分数与各指标散点图
        ax = axes[0, 2]
        ax.scatter(np.log1p(df['playCount']), scores, alpha=0.6, c=scores,
                   cmap='viridis', edgecolors='black', linewidth=0.5)
        ax.set_xlabel('Log(Play Count)')
        ax.set_ylabel('Spread Score')
        ax.set_title('Score vs Play Count')
        plt.colorbar(ax.collections[0], ax=ax, label='Score')
        ax.grid(True, alpha=0.3)

        # 4. 各指标重要性条形图
        ax = axes[1, 0]
        weights = self.weight_schemes[scheme_name]
        bars = ax.bar(weights.keys(), weights.values(), color='coral', edgecolor='black')
        ax.set_ylabel('Weight')
        ax.set_title(f'Metric Weights ({scheme_name})')
        ax.tick_params(axis='x', rotation=15)
        for bar, val in zip(bars, weights.values()):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2,
                    f'{val:.2f}', ha='center', va='center', fontweight='bold')

        # 5. 评分百分位曲线
        ax = axes[1, 1]
        sorted_scores = np.sort(scores)
        percentiles = np.arange(1, len(sorted_scores) + 1) / len(sorted_scores) * 100
        ax.plot(percentiles, sorted_scores, 'b-', linewidth=2)
        ax.fill_between(percentiles, 0, sorted_scores, alpha=0.3)
        ax.axhline(y=80, color='r', linestyle='--', alpha=0.5, label='A Level')
        ax.axhline(y=60, color='orange', linestyle='--', alpha=0.5, label='B Level')
        ax.axhline(y=40, color='y', linestyle='--', alpha=0.5, label='C Level')
        ax.set_xlabel('Percentile')
        ax.set_ylabel('Score')
        ax.set_title('Score Percentile Curve')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 6. 各指标与得分的相关系数
        ax = axes[1, 2]
        correlations = {}
        for metric in self.metrics_list:
            corr = np.corrcoef(np.log1p(df[metric]), scores)[0, 1]
            correlations[metric] = corr
        bars = ax.barh(range(len(correlations)), correlations.values(),
                       color='lightgreen', edgecolor='black')
        ax.set_yticks(range(len(correlations)))
        ax.set_yticklabels(correlations.keys())
        ax.set_xlabel('Correlation with Score')
        ax.set_title('Metric-Score Correlation')
        ax.axvline(x=0, color='black', linestyle='-')
        ax.grid(True, alpha=0.3)
        for bar, val in zip(bars, correlations.values()):
            ax.text(val, bar.get_y() + bar.get_height() / 2,
                    f' {val:.3f}', va='center')

        plt.suptitle(f'Spread Score Analysis - {scheme_name.capitalize()} Scheme',
                     fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f'score_analysis_{scheme_name}.png', dpi=300, bbox_inches='tight')
        plt.show()

    def compare_schemes(self, df):
        """
        比较不同权重方案的结果
        """
        if not self.is_fitted:
            raise ValueError("Scorer not fitted. Call fit() first.")

        fig, axes = plt.subplots(1, 3, figsize=(18, 6))

        for idx, (scheme_name, ax) in enumerate(zip(self.weight_schemes.keys(), axes)):
            scores = self.score(df, scheme=scheme_name)

            # 绘制分布
            ax.hist(scores, bins=20, alpha=0.7, label=scheme_name,
                    edgecolor='black', color=plt.cm.Set2(idx))
            ax.axvline(np.mean(scores), color='red', linestyle='--',
                       label=f'Mean: {np.mean(scores):.1f}')
            ax.axvline(np.median(scores), color='green', linestyle='--',
                       label=f'Median: {np.median(scores):.1f}')
            ax.set_xlabel('Score')
            ax.set_ylabel('Frequency')
            ax.set_title(f'{scheme_name.capitalize()} Scheme')
            ax.legend()
            ax.grid(True, alpha=0.3)

        plt.suptitle('Score Distribution Comparison Across Weight Schemes',
                     fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig('scheme_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()

        # 打印对比统计
        print("\n" + "=" * 60)
        print("SCHEME COMPARISON")
        print("=" * 60)
        for scheme_name in self.weight_schemes.keys():
            scores = self.score(df, scheme=scheme_name)
            print(f"\n{scheme_name.capitalize()} Scheme:")
            print(f"  Mean: {np.mean(scores):.2f}")
            print(f"  Median: {np.median(scores):.2f}")
            print(f"  Std: {np.std(scores):.2f}")
            print(f"  Top 10% avg score: {np.mean(np.sort(scores)[-int(len(scores) * 0.1):]):.2f}")