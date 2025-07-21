import geopandas as gpd
import polars as pl
import os
import math
from typing import Tuple
from tqdm import tqdm

def get_relation_docs(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> str:
    """
    (This function is for documentation purposes only and is not called directly in the main logic)
    Calculates the directional relationship between two coordinate points,
    returning one of eight cardinal direction labels (N, NE, E, SE, S, SW, W, NW).

    Args:
        coord1 (tuple): The coordinates of the first point (latitude, longitude).
        coord2 (tuple): The coordinates of the second point (latitude, longitude).

    Returns:
        str: The directional label.
    """
    # Note: Longitude is x, Latitude is y
    lon1, lat1 = coord1[1], coord1[0]
    lon2, lat2 = coord2[1], coord2[0]

    # Calculate the difference in coordinates
    dy = lat2 - lat1
    dx = lon2 - lon1

    # Calculate angle using atan2 for robustness across all quadrants
    angle_rad = math.atan2(dy, dx)
    # Convert radians to degrees
    angle_deg = math.degrees(angle_rad)
    # Normalize angle to [0, 360)
    angle = (angle_deg + 360) % 360

    # Determine the direction label based on the angle
    if 337.5 <= angle or angle < 22.5:
        label = "E"
    elif 22.5 <= angle < 67.5:
        label = "NE"
    elif 67.5 <= angle < 112.5:
        label = "N"
    elif 112.5 <= angle < 157.5:
        label = "NW"
    elif 157.5 <= angle < 202.5:
        label = "W"
    elif 202.5 <= angle < 247.5:
        label = "SW"
    elif 247.5 <= angle < 292.5:
        label = "S"
    else:  # 292.5 <= angle < 337.5
        label = "SE"

    return label

def calculate_city_relations_vectorized(shapefile_path: str, output_dir: str) -> None:
    """
    Extracts city coordinates, calculates directional relationships using a vectorized
    approach, and saves the result into multiple smaller CSV files with a progress bar.

    Args:
        shapefile_path (str): The path to the input shapefile.
        output_dir (str): The directory to save the output CSV files.
    """
    try:
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created directory: {output_dir}")

        # --- 1. Extract Coordinates ---
        print(f"Reading shapefile from: {shapefile_path}")
        gdf = gpd.read_file(shapefile_path)

        if gdf.empty:
            print("Warning: The shapefile is empty.")
            return

        gdf_projected = gdf.to_crs(epsg=7845)
        gdf_projected['centroid'] = gdf_projected['geometry'].centroid
        gdf['centroid'] = gdf_projected['centroid'].to_crs(gdf.crs)
        gdf['longitude'] = gdf['centroid'].x
        gdf['latitude'] = gdf['centroid'].y

        cities_df = pl.from_pandas(
            gdf[['SAL_NAME21', 'latitude', 'longitude']].rename(columns={'SAL_NAME21': 'city'})
        ).drop_nulls()
        
        print(f"Found {len(cities_df)} cities with valid coordinates.")

        # --- 2. Create All Pairs ---
        print("Creating all city pairs...")
        df1 = cities_df.rename({"city": "city1_name", "latitude": "city1_latitude", "longitude": "city1_longitude"})
        df2 = cities_df.rename({"city": "city2_name", "latitude": "city2_latitude", "longitude": "city2_longitude"})
        
        relations_df = df1.join(df2, how='cross').filter(pl.col("city1_name") != pl.col("city2_name"))
        total_relations = len(relations_df)
        print(f"Processing {total_relations} city pairs...")

        # --- 3. Vectorized Calculation ---
        print("Calculating directions using vectorized Polars expressions...")

        angle_expr = (
            pl.arctan2(
                y=(pl.col("city2_latitude") - pl.col("city1_latitude")),
                x=(pl.col("city2_longitude") - pl.col("city1_longitude"))
            ).degrees() + 360
        ) % 360

        direction_expr = (
            pl.when((angle_expr >= 337.5) | (angle_expr < 22.5)).then(pl.lit("E"))
            .when((angle_expr >= 22.5) & (angle_expr < 67.5)).then(pl.lit("NE"))
            .when((angle_expr >= 67.5) & (angle_expr < 112.5)).then(pl.lit("N"))
            .when((angle_expr >= 112.5) & (angle_expr < 157.5)).then(pl.lit("NW"))
            .when((angle_expr >= 157.5) & (angle_expr < 202.5)).then(pl.lit("W"))
            .when((angle_expr >= 202.5) & (angle_expr < 247.5)).then(pl.lit("SW"))
            .when((angle_expr >= 247.5) & (angle_expr < 292.5)).then(pl.lit("S"))
            .otherwise(pl.lit("SE"))
        )

        final_df = relations_df.with_columns(direction=direction_expr)

        # --- 4. Save to Multiple CSVs with Progress Bar ---
        num_partitions = 20
        chunk_size = (total_relations + num_partitions - 1) // num_partitions
        print(f"Splitting data into {num_partitions} files...")
        
        for i in tqdm(range(num_partitions), desc="Writing CSV chunks"):
            chunk_df = final_df.slice(i * chunk_size, chunk_size)
            if chunk_df.is_empty():
                break
            
            output_path = os.path.join(output_dir, f"city_relations_part_{i+1}_of_{num_partitions}.csv")
            chunk_df.write_csv(output_path)
        
        print(f"Successfully calculated and saved city relations to {num_partitions} files in '{output_dir}'.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    shp_path: str = os.path.join('SAL_2021_AUST_GDA2020_SHP', 'SAL_2021_AUST_GDA2020.shp')
    output_directory: str = 'data'
    
    calculate_city_relations_vectorized(shp_path, output_directory)
