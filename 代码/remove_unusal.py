import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

# 设置matplotlib支持中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号


def analyze_outliers(df, column_name, id_column='id'):
    """
    Analyze specified column without deletion, return basic information
    """
    print(f"\nAnalyzing column: {column_name}")

    # Calculate character length for each cell
    lengths = df[column_name].astype(str).apply(len)

    # Convert to numeric, replace NaN with 0
    lengths = lengths.replace('nan', 0).astype(float)

    # Calculate statistics
    mean_len = lengths.mean()
    std_len = lengths.std()
    median_len = lengths.median()
    q25 = lengths.quantile(0.25)
    q75 = lengths.quantile(0.75)
    iqr = q75 - q25

    print(f"  Average length: {mean_len:.2f}")
    print(f"  Standard deviation: {std_len:.2f}")
    print(f"  Median length: {median_len:.2f}")
    print(f"  25th percentile: {q25:.2f}")
    print(f"  75th percentile: {q75:.2f}")
    print(f"  IQR: {iqr:.2f}")

    return lengths


def create_histogram_all_data(df, column_name, id_column='id'):
    """
    Create histogram showing frequency distribution of all data
    """
    # Calculate character lengths
    lengths = df[column_name].astype(str).apply(len)
    lengths = lengths.replace('nan', 0).astype(float)

    # Create figure
    plt.figure(figsize=(12, 8))

    # Plot histogram for all data
    plt.hist(lengths, bins=200, alpha=0.7, color='blue', edgecolor='black')

    plt.title(f'Distribution of Character Lengths in {column_name} Column\n(Frequency of all data)', fontsize=14)
    plt.xlabel('Character Length', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

    # Print basic statistics
    print(f"\n{column_name} Basic Statistics:")
    print(f"  Total data points: {len(lengths)}")
    print(f"  Min length: {lengths.min():.0f}")
    print(f"  Max length: {lengths.max():.0f}")
    print(f"  Range: {lengths.max() - lengths.min():.0f}")
    print(f"  Length range: {lengths.min():.0f} - {lengths.max():.0f}")

    return lengths


def show_detailed_analysis(df, column_name, id_column='id'):
    """
    Show detailed analysis including extreme values
    """
    lengths = df[column_name].astype(str).apply(len)
    lengths = lengths.replace('nan', 0).astype(float)

    # Get longest entries
    sorted_by_length = df.copy()
    sorted_by_length['char_length'] = lengths
    sorted_by_length = sorted_by_length.sort_values('char_length', ascending=False)

    print(f"\nTop 10 longest entries in {column_name} column:")
    print("-" * 80)

    for i, (idx, row) in enumerate(sorted_by_length.head(10).iterrows()):
        if pd.notna(row[column_name]):  # Only process non-null values
            content_preview = str(row[column_name])[:200]  # Preview first 200 characters
            if len(str(row[column_name])) > 200:
                content_preview += "..."
            print(
                f"Rank {i + 1}: ID: {row[id_column]} | Length: {int(row['char_length'])} | Content: {content_preview}")
        else:
            print(f"Rank {i + 1}: ID: {row[id_column]} | Length: 0 | Content: NaN")

    # Get shortest non-zero entries
    sorted_shortest = sorted_by_length.sort_values('char_length', ascending=True)
    non_zero_entries = sorted_shortest[sorted_shortest['char_length'] > 0]

    print(f"\nTop 10 shortest non-empty entries in {column_name} column:")
    print("-" * 80)

    for i, (idx, row) in enumerate(non_zero_entries.head(10).iterrows()):
        content_preview = str(row[column_name])[:200]  # Preview first 200 characters
        if len(str(row[column_name])) > 200:
            content_preview += "..."
        print(f"Rank {i + 1}: ID: {row[id_column]} | Length: {int(row['char_length'])} | Content: {content_preview}")

    return lengths


def analyze_csv_outliers(file_path, columns_to_check=['desc', 'textExtra.hashtagName'], id_column='id'):
    """
    Analyze specified columns of CSV file and generate histograms for all data
    """
    # Read CSV file
    df = pd.read_csv(file_path)

    print(f"Data shape: {df.shape}")

    for column in columns_to_check:
        if column in df.columns:
            print(f"\n{'=' * 60}")
            print(f"Analyzing column: {column}")
            print(f"{'=' * 60}")

            # Basic analysis
            lengths = analyze_outliers(df, column, id_column)

            # Generate histogram for all data
            print(f"\nGenerating frequency distribution histogram for {column} column...")
            create_histogram_all_data(df, column, id_column)

            # Show detailed information
            detailed_lengths = show_detailed_analysis(df, column, id_column)

        else:
            print(f"Warning: Column '{column}' does not exist in the data")


def main():
    file_path = 'origindata/韩语/cleaned.csv'

    # Analyze data
    analyze_csv_outliers(
        file_path=file_path,
        columns_to_check=['desc', 'textExtra.hashtagName'],
        id_column='id'
    )


if __name__ == '__main__':
    main()