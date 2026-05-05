import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings('ignore')

# Set style
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['axes.unicode_minus'] = False

# Read data
df = pd.read_csv('all_data.csv')

# Boolean columns
bool_cols = ['IsAd', 'officalItem', 'originalItem', 'author.verified']
labels = ['Is Advertisement', 'Official Media', 'Original Content', 'Author Verified']
colors = ['#FF6B6B', '#4ECDC4', '#FFD93D', '#6C5CE7']

print(f"Data loaded: {len(df)} records\n")

# ============ Single Elegant Figure ============
fig, axes = plt.subplots(2, 2, figsize=(14, 14))
axes = axes.flatten()

for i, (col, label, color) in enumerate(zip(bool_cols, labels, colors)):
    if col in df.columns:
        true_count = df[col].sum()
        false_count = len(df) - true_count
        true_pct = true_count / len(df) * 100
        sizes = [true_count, false_count]

        # Donut chart
        wedges, texts, autotexts = axes[i].pie(
            sizes,
            labels=['True', 'False'],
            colors=[color, '#ECECEC'],
            autopct='%1.1f%%',
            startangle=90,
            pctdistance=0.82,
            explode=[0.04, 0],
            textprops={'fontsize': 12}
        )

        # Add center circle for donut effect
        centre_circle = plt.Circle((0, 0), 0.62, fc='white', linewidth=2, edgecolor='#DDDDDD')
        axes[i].add_artist(centre_circle)

        # Center text
        axes[i].text(0, 0.08, f'{true_count:,}', ha='center', va='center',
                     fontsize=22, fontweight='bold', color=color)
        axes[i].text(0, -0.18, f'({true_pct:.1f}%)', ha='center', va='center',
                     fontsize=13, color='#888888')

        axes[i].set_title(label, fontsize=16, fontweight='bold', pad=25)

        # Style the percentage texts
        for autotext in autotexts:
            autotext.set_fontweight('bold')
            autotext.set_fontsize(11)

plt.suptitle('Boolean Attributes Distribution Analysis',
             fontsize=20, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('boolean_distribution.png', dpi=300, bbox_inches='tight')
plt.show()

# Print statistics
print("=" * 60)
print("Statistics Summary")
print("=" * 60)
for col, label in zip(bool_cols, labels):
    if col in df.columns:
        true_count = df[col].sum()
        true_pct = true_count / len(df) * 100
        print(
            f"{label:25s}: True={true_count:6d} ({true_pct:5.1f}%)  False={len(df) - true_count:6d} ({100 - true_pct:5.1f}%)")

print(f"\nChart saved as: boolean_distribution.png")