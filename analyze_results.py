import polars as pl
import os
import glob
from tqdm import tqdm

def analyze_direction_distribution(data_directory: str):
    """
    Analyzes the distribution of directional labels from the generated CSV files.

    Args:
        data_directory (str): The directory containing the partitioned CSV files.
    """
    try:
        csv_pattern = os.path.join(data_directory, 'city_relations_part_*.csv')
        csv_files = glob.glob(csv_pattern)

        if not csv_files:
            print(f"Error: No CSV files found in '{data_directory}'. Please run the calculation task first.")
            return

        print(f"Found {len(csv_files)} files to analyze. Reading and concatenating...")

        # Lazily scan all CSVs and then collect them into a single DataFrame
        # This is more memory-efficient than reading them one by one into memory
        lazy_dfs = [pl.scan_csv(file) for file in tqdm(csv_files, desc="Scanning files")]
        all_data_df = pl.concat(lazy_dfs).collect()
        
        print("Calculating direction distribution...")
        
        # Group by the 'direction' column and count the occurrences
        distribution = all_data_df.group_by('direction').agg(
            pl.len().alias('count')
        ).sort('direction')

        # Calculate percentage
        total_count = distribution['count'].sum()
        distribution = distribution.with_columns(
            ((pl.col('count') / total_count) * 100).round(2).alias('percentage')
        )

        print("\n--- Directional Relationship Distribution ---")
        print(distribution)
        print("-------------------------------------------\n")

    except Exception as e:
        print(f"An error occurred during analysis: {e}")

if __name__ == "__main__":
    data_dir = 'data'
    analyze_direction_distribution(data_dir)