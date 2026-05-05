import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import RobustScaler
import warnings

warnings.filterwarnings('ignore')


class SpreadScoreBuilder:
    """
    视频传播力评分构建器
    基于六个维度：在线天数、点赞、分享、评论、收藏、播放
    """

    def __init__(self):
        self.metrics = ['length', 'stats.diggCount', 'stats.shareCount',
                        'stats.commentCount', 'stats.collectCount', 'stats.playCount']

        # 存储学习到的参数
        self.params = {}

    def fit(self, df):
        """
        从数据中学习所有需要的参数
        """
        print("=" * 80)
        print("PHASE 2: Learning Data Parameters")
        print("=" * 80)

        data = df[self.metrics].copy()

        # Step 1: 学习每个指标的对数分布参数
        print("\n1. Learning log-normal distribution parameters...")
        for metric in self.metrics:
            log_data = np.log1p(data[metric])
            self.params[f'{metric}_log'] = {
                'mean': log_data.mean(),
                'std': log_data.std(),
                'median': log_data.median(),
                'q25': log_data.quantile(0.25),
                'q75': log_data.quantile(0.75),
                'q95': log_data.quantile(0.95),
                'q99': log_data.quantile(0.99),
                'skewness': log_data.skew()
            }

        # Step 2: 计算衍生指标的分布
        print("\n2. Computing derived metrics distributions...")

        # 互动率（单位播放的互动）
        engagement = (data['stats.diggCount'] + data['stats.commentCount'] +
                      data['stats.collectCount']) / (data['stats.playCount'] + 1)
        log_engagement = np.log1p(engagement)
        self.params['engagement_rate'] = {
            'mean': log_engagement.mean(),
            'std': log_engagement.std(),
            'q50': log_engagement.quantile(0.5),
            'q75': log_engagement.quantile(0.75),
            'q90': log_engagement.quantile(0.90)
        }

        # 分享率
        share_rate = data['stats.shareCount'] / (data['stats.playCount'] + 1)
        log_share_rate = np.log1p(share_rate * 100)
        self.params['share_rate'] = {
            'mean': log_share_rate.mean(),
            'std': log_share_rate.std(),
            'q50': log_share_rate.quantile(0.5),
            'q75': log_share_rate.quantile(0.75)
        }

        # 日均播放量
        daily_play = data['stats.playCount'] / (data['length'] + 1)
        log_daily_play = np.log1p(daily_play)
        self.params['daily_play'] = {
            'mean': log_daily_play.mean(),
            'std': log_daily_play.std(),
            'q50': log_daily_play.quantile(0.5),
            'q75': log_daily_play.quantile(0.75),
            'q90': log_daily_play.quantile(0.90)
        }

        # Step 3: 计算指标间相关性
        print("\n3. Computing correlation structure...")
        log_data = np.log1p(data)
        self.params['correlation'] = log_data.corr()

        # Step 4: 计算信息熵权重
        print("\n4. Computing entropy-based weights...")
        normalized = (log_data - log_data.min()) / (log_data.max() - log_data.min())
        n = len(normalized)
        entropies = {}
        for col in self.metrics:
            p = normalized[col] / normalized[col].sum()
            p = p[p > 0]
            entropy = -np.sum(p * np.log(p)) / np.log(n)
            entropies[col] = entropy

        # 熵值越小，区分度越大，权重越高
        total_entropy = sum(1 - v for v in entropies.values())
        self.params['entropy_weights'] = {
            k: (1 - v) / total_entropy for k, v in entropies.items()
        }

        print("\nEntropy Weights:")
        for metric, weight in self.params['entropy_weights'].items():
            print(f"  {metric}: {weight:.3f}")

        print("\n✅ Parameter learning complete!")

    def _percentile_score(self, values, metric_name):
        """
        基于经验分布的百分位评分
        """
        params = self.params[f'{metric_name}_log']
        log_values = np.log1p(values)

        # Z-score
        z_scores = (log_values - params['mean']) / (params['std'] + 1e-8)

        # 理论百分位
        percentiles = stats.norm.cdf(z_scores)

        # Sigmoid变换增强区分度
        scores = 1 / (1 + np.exp(-10 * (percentiles - 0.5)))

        return scores

    def calculate_scores(self, df):
        """
        计算最终的传播力得分
        """
        print("\n" + "=" * 80)
        print("PHASE 3: Computing Spread Scores")
        print("=" * 80)

        result = pd.DataFrame(index=df.index)

        # ===== 维度1: 传播规模 (Scale) =====
        # 基于播放量的绝对值和日均播放
        print("1. Computing Scale Score...")
        play_score = self._percentile_score(df['stats.playCount'], 'stats.playCount')

        daily_play = df['stats.playCount'] / (df['length'] + 1)
        log_daily = np.log1p(daily_play)
        daily_score = (log_daily - self.params['daily_play']['mean']) / (self.params['daily_play']['std'] + 1e-8)
        daily_score = stats.norm.cdf(daily_score)
        daily_score = 1 / (1 + np.exp(-8 * (daily_score - 0.5)))

        scale_score = 0.6 * play_score + 0.4 * daily_score

        # ===== 维度2: 用户参与度 (Engagement) =====
        print("2. Computing Engagement Score...")
        digg_score = self._percentile_score(df['stats.diggCount'], 'stats.diggCount')
        comment_score = self._percentile_score(df['stats.commentCount'], 'stats.commentCount')

        # 评论权重更高（深度互动）
        engagement_score = 0.4 * digg_score + 0.6 * comment_score

        # ===== 维度3: 传播扩散力 (Virality) =====
        print("3. Computing Virality Score...")
        share_abs_score = self._percentile_score(df['stats.shareCount'], 'stats.shareCount')

        share_rate = df['stats.shareCount'] / (df['stats.playCount'] + 1)
        log_share_rate = np.log1p(share_rate * 100)
        share_rate_score = (log_share_rate - self.params['share_rate']['mean']) / (
                    self.params['share_rate']['std'] + 1e-8)
        share_rate_score = stats.norm.cdf(share_rate_score)
        share_rate_score = 1 / (1 + np.exp(-12 * (share_rate_score - 0.4)))

        virality_score = 0.45 * share_abs_score + 0.55 * share_rate_score

        # ===== 维度4: 内容价值 (Value) =====
        print("4. Computing Value Score...")
        collect_score = self._percentile_score(df['stats.collectCount'], 'stats.collectCount')

        # 收藏率（相对点赞）
        collect_rate = df['stats.collectCount'] / (df['stats.diggCount'] + 1)
        log_collect_rate = np.log1p(collect_rate)
        collect_rate_score = (log_collect_rate - log_collect_rate.mean()) / (log_collect_rate.std() + 1e-8)
        collect_rate_score = stats.norm.cdf(collect_rate_score)
        collect_rate_score = 1 / (1 + np.exp(-8 * (collect_rate_score - 0.5)))

        value_score = 0.55 * collect_score + 0.45 * collect_rate_score

        # ===== 维度5: 时间效率 (Time Efficiency) =====
        print("5. Computing Time Efficiency Score...")
        # 总互动（加权）
        total_interaction = (df['stats.diggCount'] +
                             df['stats.commentCount'] * 1.5 +
                             df['stats.collectCount'] * 2 +
                             df['stats.shareCount'] * 3)

        # 日均互动
        daily_interaction = total_interaction / (df['length'] + 1)
        log_daily_int = np.log1p(daily_interaction)
        daily_int_score = (log_daily_int - log_daily_int.mean()) / (log_daily_int.std() + 1e-8)
        daily_int_score = stats.norm.cdf(daily_int_score)
        daily_int_score = np.sqrt(daily_int_score)  # 温和变换

        time_score = daily_int_score

        # ===== 维度6: 互动效率 (Interaction Efficiency) =====
        print("6. Computing Interaction Efficiency Score...")
        engagement_rate = total_interaction / (df['stats.playCount'] + 1)
        log_eng_rate = np.log1p(engagement_rate)
        eng_rate_score = (log_eng_rate - self.params['engagement_rate']['mean']) / (
                    self.params['engagement_rate']['std'] + 1e-8)
        eng_rate_score = stats.norm.cdf(eng_rate_score)
        eng_rate_score = 1 / (1 + np.exp(-10 * (eng_rate_score - 0.45)))

        efficiency_score = eng_rate_score

        # ===== 综合评分 =====
        print("\n7. Computing Final Spread Score...")

        # 基础权重
        weights = {
            'scale': 0.25,  # 传播规模
            'engagement': 0.20,  # 用户参与
            'virality': 0.25,  # 扩散力（权重最高）
            'value': 0.15,  # 内容价值
            'time': 0.10,  # 时间效率
            'efficiency': 0.05  # 互动效率
        }

        # 计算综合得分
        final_score = (weights['scale'] * scale_score +
                       weights['engagement'] * engagement_score +
                       weights['virality'] * virality_score +
                       weights['value'] * value_score +
                       weights['time'] * time_score +
                       weights['efficiency'] * efficiency_score)

        # 映射到0-100
        final_score = final_score * 100

        # 保存各维度得分
        result['spread_score'] = final_score
        result['scale_score'] = scale_score * 100
        result['engagement_score'] = engagement_score * 100
        result['virality_score'] = virality_score * 100
        result['value_score'] = value_score * 100
        result['time_efficiency_score'] = time_score * 100
        result['interaction_efficiency_score'] = efficiency_score * 100

        # 评级
        conditions = [
            final_score >= 80,
            final_score >= 60,
            final_score >= 40,
            final_score >= 20,
            final_score >= 0
        ]
        choices = ['A', 'B', 'C', 'D', 'E']
        result['spread_rating'] = np.select(conditions, choices)

        print("\n✅ Score computation complete!")

        return result


# ============ 执行评分计算 ============

# 读取数据
print("Loading data...")
df = pd.read_csv('all_data.csv')
print(f"Total records: {len(df):,}")

# 创建评分器
builder = SpreadScoreBuilder()

# 学习参数
builder.fit(df)

# 计算得分
scores = builder.calculate_scores(df)

# 合并到原数据
df = pd.concat([df, scores], axis=1)

# 保存
df.to_csv('all_data.csv', index=False)

# ============ 结果统计 ============
print("\n" + "=" * 80)
print("FINAL RESULTS")
print("=" * 80)

print(f"\nSpread Score Statistics:")
print(f"  Mean:   {scores['spread_score'].mean():.2f}")
print(f"  Median: {scores['spread_score'].median():.2f}")
print(f"  Std:    {scores['spread_score'].std():.2f}")
print(f"  Min:    {scores['spread_score'].min():.2f}")
print(f"  Max:    {scores['spread_score'].max():.2f}")
print(f"  Skewness: {scores['spread_score'].skew():.2f}")

print(f"\nRating Distribution:")
rating_dist = scores['spread_rating'].value_counts().sort_index()
for rating in ['A', 'B', 'C', 'D', 'E']:
    count = rating_dist.get(rating, 0)
    pct = count / len(scores) * 100
    print(f"  Level {rating}: {count:>8,} ({pct:>5.1f}%)")

print(f"\nDimension Correlations with Final Score:")
for col in ['scale_score', 'engagement_score', 'virality_score',
            'value_score', 'time_efficiency_score', 'interaction_efficiency_score']:
    corr = scores['spread_score'].corr(scores[col])
    print(f"  {col:35s}: {corr:.3f}")

print(f"\n✅ Results saved to all_data.csv")