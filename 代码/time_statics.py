import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['axes.unicode_minus'] = False
sns.set_style("whitegrid")
sns.set_palette("husl")

# Read data
df = pd.read_csv('all_data.csv')

# Convert to datetime
df['createTime_date'] = pd.to_datetime(df['createTime_date'])

# Extract time components
df['year'] = df['createTime_date'].dt.year
df['month'] = df['createTime_date'].dt.month
df['day'] = df['createTime_date'].dt.day
df['weekday'] = df['createTime_date'].dt.dayofweek
df['hour'] = df['createTime_date'].dt.hour
df['year_month'] = df['createTime_date'].dt.to_period('M')
df['year_week'] = df['createTime_date'].dt.to_period('W')

print(f"Data loaded: {len(df)} records")
print(f"Date range: {df['createTime_date'].min()} to {df['createTime_date'].max()}")

# ============ Chart 1: Daily Distribution ============
print("\nGenerating Chart 1: Daily Distribution...")
fig1, ax1 = plt.subplots(figsize=(16, 8))

daily_counts = df.groupby(df['createTime_date'].dt.date).size()
daily_counts.index = pd.to_datetime(daily_counts.index)

# Plot with gradient fill
ax1.plot(daily_counts.index, daily_counts.values, color='#FF6B6B', linewidth=2, alpha=0.8)
ax1.fill_between(daily_counts.index, daily_counts.values, alpha=0.3, color='#FF6B6B')

# Add trend line
z = np.polyfit(range(len(daily_counts)), daily_counts.values, 3)
p = np.poly1d(z)
ax1.plot(daily_counts.index, p(range(len(daily_counts))),
         '--', color='#2C3E50', linewidth=2, alpha=0.6, label='Trend')

ax1.set_title('Daily Video Publishing Distribution', fontsize=16, fontweight='bold', pad=15)
ax1.set_xlabel('Date', fontsize=13)
ax1.set_ylabel('Number of Videos', fontsize=13)
ax1.legend(fontsize=11)
ax1.grid(True, alpha=0.3, linestyle='--')

# Add statistics
stats_text = f'Total Days: {len(daily_counts)}\nMean: {daily_counts.mean():.1f}\nMax: {daily_counts.max()}'
ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes,
         fontsize=10, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

plt.tight_layout()
plt.savefig('daily_distribution.png', dpi=300, bbox_inches='tight')
plt.show()
print("Chart 1 saved as: daily_distribution.png")
input("Press Enter to continue...")
plt.close()

# ============ Chart 2: Weekly Pattern ============
print("\nGenerating Chart 2: Weekly Pattern...")
fig2, ax2 = plt.subplots(figsize=(12, 8))

weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
weekday_counts = df['weekday'].value_counts().sort_index()

# Beautiful bar chart
colors = ['#FF6B6B' if i >= 5 else '#4ECDC4' for i in range(7)]
bars = ax2.bar(weekday_names, weekday_counts.values, color=colors,
               edgecolor='white', linewidth=2, alpha=0.85)

# Add value labels
for bar, val in zip(bars, weekday_counts.values):
    ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(weekday_counts)*0.01,
             f'{val}\n({val/len(df)*100:.1f}%)', ha='center', va='bottom', fontsize=10)

ax2.set_title('Weekly Publishing Pattern', fontsize=16, fontweight='bold', pad=15)
ax2.set_xlabel('Day of Week', fontsize=13)
ax2.set_ylabel('Number of Videos', fontsize=13)
ax2.grid(True, alpha=0.3, axis='y', linestyle='--')

# Add horizontal line for mean
mean_val = weekday_counts.mean()
ax2.axhline(y=mean_val, color='red', linestyle='--', alpha=0.5, linewidth=1.5, label=f'Mean: {mean_val:.1f}')
ax2.legend(fontsize=10)

plt.tight_layout()
plt.savefig('weekly_pattern.png', dpi=300, bbox_inches='tight')
plt.show()
print("Chart 2 saved as: weekly_pattern.png")
input("Press Enter to continue...")
plt.close()

# ============ Chart 3: Monthly Distribution ============
print("\nGenerating Chart 3: Monthly Distribution...")
fig3, ax3 = plt.subplots(figsize=(16, 8))

monthly_counts = df.groupby('year_month').size()

# Gradient bar chart
colors = plt.cm.Spectral(np.linspace(0, 1, len(monthly_counts)))
bars = ax3.bar(range(len(monthly_counts)), monthly_counts.values, color=colors,
               edgecolor='white', linewidth=1.5, alpha=0.85)

# Set x-ticks
step = max(1, len(monthly_counts) // 12)
ax3.set_xticks(range(0, len(monthly_counts), step))
ax3.set_xticklabels([str(x) for x in monthly_counts.index[::step]], rotation=45, ha='right')

ax3.set_title('Monthly Video Publishing Trend', fontsize=16, fontweight='bold', pad=15)
ax3.set_xlabel('Year-Month', fontsize=13)
ax3.set_ylabel('Number of Videos', fontsize=13)
ax3.grid(True, alpha=0.3, axis='y', linestyle='--')

# Add trend line
z = np.polyfit(range(len(monthly_counts)), monthly_counts.values, 1)
p = np.poly1d(z)
ax3.plot(range(len(monthly_counts)), p(range(len(monthly_counts))),
         '--', color='#2C3E50', linewidth=2.5, alpha=0.7, label='Linear Trend')

# Add moving average
if len(monthly_counts) >= 3:
    ma = monthly_counts.rolling(window=3, min_periods=1).mean()
    ax3.plot(range(len(monthly_counts)), ma.values,
             '-', color='#FF6B6B', linewidth=2, alpha=0.7, label='3-Month MA')

ax3.legend(fontsize=11)

plt.tight_layout()
plt.savefig('monthly_distribution.png', dpi=300, bbox_inches='tight')
plt.show()
print("Chart 3 saved as: monthly_distribution.png")
input("Press Enter to continue...")
plt.close()

# ============ Chart 4: Hourly Distribution ============
print("\nGenerating Chart 4: Hourly Distribution...")
fig4, ax4 = plt.subplots(figsize=(14, 8), subplot_kw=dict(projection='polar'))

hourly_counts = df['hour'].value_counts().sort_index()

# Radar chart for hourly distribution
hours = np.arange(24)
angles = np.linspace(0, 2 * np.pi, 24, endpoint=False).tolist()
angles += angles[:1]

values = hourly_counts.reindex(hours, fill_value=0).values.tolist()
values += values[:1]

ax4.fill(angles, values, alpha=0.3, color='#FF6B6B')
ax4.plot(angles, values, 'o-', color='#FF6B6B', linewidth=2, markersize=6)

ax4.set_xticks(angles[:-1])
ax4.set_xticklabels([f'{h}:00' for h in hours], fontsize=9)
ax4.set_title('Hourly Publishing Distribution (Polar View)', fontsize=16, fontweight='bold', pad=25)
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('hourly_polar.png', dpi=300, bbox_inches='tight')
plt.show()
print("Chart 4 saved as: hourly_polar.png")
input("Press Enter to continue...")
plt.close()

# ============ Chart 5: Hourly Heatmap by Weekday ============
print("\nGenerating Chart 5: Hourly Heatmap by Weekday...")
fig5, ax5 = plt.subplots(figsize=(14, 8))

heatmap_data = df.groupby(['weekday', 'hour']).size().unstack(fill_value=0)

sns.heatmap(heatmap_data, cmap='YlOrRd', annot=True, fmt='d',
            linewidths=1, linecolor='white', cbar_kws={'label': 'Video Count'},
            ax=ax5, annot_kws={'size': 8})

ax5.set_title('Publishing Heatmap: Day of Week vs Hour', fontsize=16, fontweight='bold', pad=15)
ax5.set_xlabel('Hour of Day', fontsize=13)
ax5.set_ylabel('Day of Week', fontsize=13)
ax5.set_yticklabels(weekday_names, rotation=0)

plt.tight_layout()
plt.savefig('heatmap_weekday_hour.png', dpi=300, bbox_inches='tight')
plt.show()
print("Chart 5 saved as: heatmap_weekday_hour.png")
input("Press Enter to continue...")
plt.close()

# ============ Chart 6: Comprehensive Dashboard ============
print("\nGenerating Chart 6: Comprehensive Dashboard...")
fig6 = plt.figure(figsize=(20, 16))

# 6.1: Monthly trend (top left)
ax6_1 = plt.subplot(2, 3, 1)
monthly_counts_6 = df.groupby('year_month').size()
ax6_1.fill_between(range(len(monthly_counts_6)), monthly_counts_6.values,
                    alpha=0.4, color='#FF6B6B')
ax6_1.plot(range(len(monthly_counts_6)), monthly_counts_6.values,
           'o-', color='#FF6B6B', linewidth=2, markersize=4)
step = max(1, len(monthly_counts_6) // 8)
ax6_1.set_xticks(range(0, len(monthly_counts_6), step))
ax6_1.set_xticklabels([str(x) for x in monthly_counts_6.index[::step]], rotation=45, ha='right', fontsize=9)
ax6_1.set_title('Monthly Trend', fontsize=14, fontweight='bold')
ax6_1.set_ylabel('Count', fontsize=11)
ax6_1.grid(True, alpha=0.3)

# 6.2: Day of week distribution (top middle)
ax6_2 = plt.subplot(2, 3, 2)
weekday_counts_6 = df['weekday'].value_counts().sort_index()
colors_pie = ['#FF6B6B', '#FFA07A', '#FFD700', '#4ECDC4', '#45B7D1', '#96CEB4', '#DDA0DD']
wedges, texts, autotexts = ax6_2.pie(weekday_counts_6.values,
                                       labels=weekday_names,
                                       autopct='%1.1f%%',
                                       colors=colors_pie,
                                       startangle=90,
                                       explode=[0.05]*7)
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
ax6_2.set_title('Day of Week Distribution', fontsize=14, fontweight='bold')

# 6.3: Hour distribution (top right)
ax6_3 = plt.subplot(2, 3, 3)
hourly_counts_6 = df['hour'].value_counts().sort_index()
hours_6 = hourly_counts_6.index.tolist()
ax6_3.bar(hours_6, hourly_counts_6.values, color='#4ECDC4', alpha=0.8, edgecolor='white')
ax6_3.set_title('Hour Distribution', fontsize=14, fontweight='bold')
ax6_3.set_xlabel('Hour', fontsize=11)
ax6_3.set_ylabel('Count', fontsize=11)
ax6_3.set_xticks(range(0, 24, 3))
ax6_3.grid(True, alpha=0.3, axis='y')
# Add peak hour annotation
peak_hour = hourly_counts_6.idxmax()
ax6_3.axvline(x=peak_hour, color='red', linestyle='--', alpha=0.5, label=f'Peak: {peak_hour}:00')
ax6_3.legend(fontsize=9)

# 6.4: Cumulative distribution (bottom left)
ax6_4 = plt.subplot(2, 3, 4)
daily_counts_6 = df.groupby(df['createTime_date'].dt.date).size()
sorted_daily = np.sort(daily_counts_6.values)
cumsum = np.cumsum(sorted_daily) / np.sum(sorted_daily) * 100
ax6_4.plot(range(1, len(cumsum)+1), cumsum, 'b-', linewidth=2)
ax6_4.fill_between(range(1, len(cumsum)+1), cumsum, alpha=0.3)
ax6_4.axhline(y=50, color='red', linestyle='--', alpha=0.5, label='50% Line')
ax6_4.axhline(y=80, color='orange', linestyle='--', alpha=0.5, label='80% Line')
ax6_4.set_title('Cumulative Video Distribution', fontsize=14, fontweight='bold')
ax6_4.set_xlabel('Day Rank', fontsize=11)
ax6_4.set_ylabel('Cumulative %', fontsize=11)
ax6_4.legend(fontsize=9)
ax6_4.grid(True, alpha=0.3)

# 6.5: Year distribution (bottom middle)
ax6_5 = plt.subplot(2, 3, 5)
year_counts = df['year'].value_counts().sort_index()
ax6_5.bar(year_counts.index.astype(str), year_counts.values,
          color=['#FF6B6B', '#4ECDC4', '#45B7D1'], edgecolor='white', alpha=0.8)
ax6_5.set_title('Year Distribution', fontsize=14, fontweight='bold')
ax6_5.set_ylabel('Count', fontsize=11)
ax6_5.grid(True, alpha=0.3, axis='y')
for i, (year, count) in enumerate(zip(year_counts.index, year_counts.values)):
    ax6_5.text(i, count + max(year_counts)*0.02, str(count), ha='center', fontweight='bold')

# 6.6: Statistical summary (bottom right)
ax6_6 = plt.subplot(2, 3, 6)
ax6_6.axis('off')

stats = [
    f"Total Records: {len(df):,}",
    f"Date Range: {df['createTime_date'].min().strftime('%Y-%m-%d')}",
    f"           to {df['createTime_date'].max().strftime('%Y-%m-%d')}",
    f"",
    f"Daily Average: {daily_counts_6.mean():.1f}",
    f"Daily Median: {daily_counts_6.median():.1f}",
    f"Daily Max: {daily_counts_6.max()}",
    f"Daily Min: {daily_counts_6.min()}",
    f"",
    f"Peak Day: {daily_counts_6.idxmax()}",
    f"Peak Hour: {peak_hour}:00",
    f"Peak Weekday: {weekday_names[df['weekday'].value_counts().idxmax()]}",
    f"",
    f"Active Days: {len(daily_counts_6)}",
    f"Active Months: {len(df['year_month'].unique())}",
]

for i, text in enumerate(stats):
    ax6_6.text(0.1, 0.95 - i*0.055, text, transform=ax6_6.transAxes,
              fontsize=10, verticalalignment='top', fontfamily='monospace')

ax6_6.set_title('Statistical Summary', fontsize=14, fontweight='bold', pad=15)

plt.suptitle('Video Publishing Time Distribution Dashboard', fontsize=18, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('time_dashboard.png', dpi=300, bbox_inches='tight')
plt.show()
print("Chart 6 saved as: time_dashboard.png")
input("Press Enter to continue...")
plt.close()

# ============ Final Summary ============
print("\n" + "="*60)
print("TIME DISTRIBUTION ANALYSIS COMPLETE")
print("="*60)
print(f"\nTop 5 Peak Publishing Hours:")
for hour, count in hourly_counts.nlargest(5).items():
    print(f"  {hour:02d}:00 - {count} videos")

print(f"\nTop 3 Peak Publishing Days:")
for day_idx, count in weekday_counts.nlargest(3).items():
    print(f"  {weekday_names[day_idx]} - {count} videos")

print(f"\nBusiest Month: {monthly_counts.idxmax()} ({monthly_counts.max()} videos)")
print(f"Quietest Month: {monthly_counts.idxmin()} ({monthly_counts.min()} videos)")

print(f"\nAll charts saved:")
print(f"  1. daily_distribution.png")
print(f"  2. weekly_pattern.png")
print(f"  3. monthly_distribution.png")
print(f"  4. hourly_polar.png")
print(f"  5. heatmap_weekday_hour.png")
print(f"  6. time_dashboard.png")